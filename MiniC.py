from Scanner.Token import *
from Scanner.SourceFile import *
from Scanner.SourcePos import *
from Scanner.Scanner import *

import sys

class MiniC:
    scanner = None
    def __init__(self):
        pass

    def compileProgram(self, sourceName):
        print("********** " + "MiniC Compiler" + " **********")
        print("Lexical Analysis ...")

        source = SourceFile(sourceName)
        scanner = Scanner(source)
        scanner.enableDebugging()

        while True:
            t = scanner.scan()  # scan 1 token
            if t.kind == Token.EOF: break

miniC = MiniC()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: MiniC filename")
        exit(1)
    sourceName = sys.argv[1]
    miniC.compileProgram(sourceName)