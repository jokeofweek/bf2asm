"""
bf2mips.py
----------
A simple brainf**k to MIPS compiler.
Written by Dominic Charley-Roy
"""

import argparse
import os
import sys

class CompileException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def __main__():
    parser = argparse.ArgumentParser(description='Convert a brainfuck file to MIPS assembly.')
    parser.add_argument('input', metavar='inname', help='the input file.')
    parser.add_argument('-o', dest='outname', help='file to print assembly to.')
    
    args = parser.parse_args()
    
    inname = args.input
    outname = args.outname
    if outname is None:
        outname = os.path.splitext(inname)[0] + '.asm'
    
    branch_id_counter = 1
    branch_ids = []
    last_token = ''
    current_token = ''
    repetitions_count = 0
    succesful_compile = True
    
    header = (".data\n"
              "  bytes:\n"
              "  .space 120000\n"
              ".text\n"
              ".globl main\n"
              "main:\n"
              "  li $t1, 0\n")
    footer = ("  li $v0, 10\n"
              "  syscall")
    generated_code = ""
    
    with open(inname, 'r') as original:
        try:
            while True:
                current_token = original.read(1)
                
                if not current_token:
                    break

                if current_token != last_token and last_token != '':
                    generated_code += get_code(last_token, {'repetitions' : repetitions_count})
                    repetitions_count = 0

                if current_token == '[':
                    branch_ids.append(branch_id_counter)
                    generated_code += get_code(current_token, {'branch_id': branch_id_counter})
                    branch_id_counter += 1
                    
                    last_token = ''
                elif current_token == ']':
                    if branch_ids.__len__() == 0:
                        raise CompileException('Unmatched [].')

                    exit_branch_id = branch_ids.pop()
                    generated_code += get_code(current_token, {'branch_id': exit_branch_id})
                    
                    last_token = ''
                else:
                    last_token = current_token
                    repetitions_count += 1

            # In case there was a repetition at the end..
            if last_token != '':
                generated_code += get_code(last_token, {'repetitions' : repetitions_count})
                
            if branch_ids.__len__() != 0:
                raise CompileException('Unmached [].')
                
        except CompileException as e:
            print("Compile Error: " + e)
            succesful_compile = False

    if succesful_compile:
        with open(outname, 'w+') as output:
            output.write(header)
            output.write(generated_code)
            output.write(footer)
            
def get_code(char, options):
    out = ""
    if char == '+':
        out = ("  lw $t2, bytes($t1)\n"
               "  addi $t2, $t2, %s\n"
               "  sw $t2, bytes($t1)\n"
               % (options['repetitions']))
    elif char == '-':
        out = ("  lw $t2, bytes($t1)\n"
               "  subi $t2, $t2, %s\n"
               "  sw $t2, bytes($t1)\n"
               % (options['repetitions']))
    elif char == '>':
        out = ("  addi $t1, $t1, %s\n"
               % (options['repetitions'] * 4))
    elif char == '<':
        out = ("  subi $t1, $t1, %s\n"
               % (options['repetitions'] * 4))
    elif char == '.':
        out = ("  lw $a0, bytes($t1)\n"
               "  li $v0, 11\n")
        for i in range(0, options['repetitions']):
            out += "  syscall\n"
    elif char == ',':
        out = ("  li $v0, 12\n")
        for i in range(0, options['repetitions']):
            out += "  syscall\n"
        out += "  sw $v0, bytes($t1)\n"
    elif char == '[':
        out += ("  lw $t2, bytes($t1)\n"
                "  beq $t2, $zero, cont_%s\n"
                "func_%s:\n"
                % (options['branch_id'], options['branch_id']))
    elif char == ']':
        out += ("  lw $t2, bytes($t1)\n"
                "  bnez $t2, func_%s\n"
                "\n"
                "cont_%s:\n"
                % (options['branch_id'], options['branch_id']))
    return out

if __name__ == "__main__":
    __main__()
