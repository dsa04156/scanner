from Scanner.Token import *
from Scanner.SourceFile import *
from Scanner.SourcePos import *

class Scanner:
    @staticmethod
    def isDigit(c):
        return (c >= '0' and c <= '9')
    
    def __init__(self, source):
        self.sourceFile = source
        self.currentChar = self.sourceFile.readChar()
        self.verbose = False
        self.currentLineNr = -1
        self.currentColNr = -1

        self.currentLexeme = ''
        self.currentlyScanningToken = False
    
    def enableDebugging(self):
        self.verbose = True
    
    # takeIt appends the current character to the current token, and gets
    # the next character from the source program (or the to-be-implemented
    # "untake" buffer in case of look-ahead characters that got 'pushed back'
    # into the input stream).

    def takeIt(self):
        if self.currentlyScanningToken:
            self.currentLexeme += self.currentChar
        self.currentChar = self.sourceFile.readChar()
    
    def scanToken(self):
        match self.currentChar:
            case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                self.takeIt()
                while self.isDigit(self.currentChar):
                    self.takeIt()
                # Note: code for floating point literals is missing here...
                return Token.INTLITERAL
            case '+':
                self.takeIt()
                return Token.PLUS
            case SourceFile.EOF:
                self.currentLexeme += '$'
                return Token.EOF
            # Add code here for the remaining MiniC tokens...
        
            case _:
                self.takeIt()
                return Token.ERROR
    
    def scan(self):
        self.currentlyScanningToken = False
        while self.currentChar in ('',' ', '\f', '\n', '\r', '\t'):
            self.takeIt()
        
        self.currentlyScanningToken = True
        self.currentLexeme = ""
        pos = SourcePos()
        pos.StartLine = self.currentLineNr
        pos.EndLine = self.currentLineNr
        pos.StartCol = self.currentColNr
        kind = self.scanToken()
        currentToken = Token(kind, self.currentLexeme, pos)
        pos.EndCol = self.currentColNr

        if self.verbose:
            print(currentToken)
        
        return currentToken
