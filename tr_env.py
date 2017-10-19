#!/usr/bin/env python3

from pathlib import Path
import os, re, argparse, subprocess

def tr_compile(env, descompile):
    p = Path('.')
    lineNumber = 0
    startLine = 0
    openBracket = 0
    closeBracket = 0
    found = False
    regex = ''

    pattern = re.compile(r'#EXCLUDE:')
    patternEnv = re.compile(r''+env)
    patternOpenBracket = re.compile(r'{')
    patternCloseBracket = re.compile(r'}')

    for f in list(p.glob('**/*.tf')):
        with open(f, 'r') as tr_file:
            for line in tr_file.readlines():
                lineNumber += 1
                if (pattern.search(line) and patternEnv.search(line)):
                    found = True
                    startLine = lineNumber + 1
                if (startLine == lineNumber and found == True):
                    if patternOpenBracket.search(line):
                        openBracket += 1
                    if patternCloseBracket.search(line):
                        closeBracket += 1
                    if (descompile == True):
                        if(line[:1] == '#'):
                            regex = str(startLine) + 's/^\#//g'
                    else:
                        regex = str(startLine) + 's/^/\#/g'
                    subprocess.run([
                            "sed",
                            "-i",
                            regex,
                            str(f)
                        ])

                    startLine += 1

                    if (openBracket != 0 and openBracket == closeBracket):
                        found = False
                        startLine = 0
                        openBracket = 0
                        closeBracket = 0
            lineNumber = 0
        tr_file.close()

def run_tr(cmd):
    subprocess.run(cmd.split(' '))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compile/Descompile your Terraform to according Environment.')
    parser.add_argument('-e', action='store', dest='env', required=False, metavar='[prod|stag|...]',
                       help='Environment name. If not present looking for TF_VAR_environment environment variable.')
    parser.add_argument('-t', action='store', dest='tr_cmd', required=True, metavar='terraform [plan|apply|version|...]',
                       help='Terraform CMD. specify you Terraform command to be called.')
    args = vars(parser.parse_args())

    if (args['env'] == None and 'TF_VAR_environment' not in os.environ):
        print("Please set TF_VAR_environment or use -e")
    else:
        if (args['env'] == None):
            args['env'] = os.environ['TF_VAR_environment']

        print("Compiling code to Environment: " + args['env'])
        tr_compile(args['env'], descompile=False)
        print("Running Terraform: " + args['tr_cmd'])
        run_tr(args['tr_cmd'])
        print("Descompiling code to Environment: " + args['env'])
        tr_compile(args['env'], descompile=True)
        print("Done! :)")
