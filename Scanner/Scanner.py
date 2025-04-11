from Scanner.Token import *
from Scanner.SourceFile import *
from Scanner.SourcePos import *


class Scanner:
    @staticmethod
    def isDigit(c):
        return c >= "0" and c <= "9"

    def __init__(self, source):
        self.sourceFile = source
        self.currentChar = self.sourceFile.readChar()
        self.verbose = False
        self.currentLineNr = 1
        self.currentColNr = 1

        self.currentLexeme = ""
        self.currentlyScanningToken = False

    def enableDebugging(self):
        self.verbose = True

    def takeIt(self):
        if self.currentlyScanningToken:
            self.currentLexeme += self.currentChar

        if self.currentChar == "\n":
            self.currentLineNr += 1
            self.currentColNr = 1
        else:
            self.currentColNr += 1
        self.currentChar = self.sourceFile.readChar()

    def scanToken(self):
        match self.currentChar:
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self.takeIt()
                while self.isDigit(self.currentChar):
                    self.takeIt()
                tokenType = Token.INTLITERAL

                if self.currentChar == ".":
                    tokenType = Token.FLOATLITERAL
                    self.takeIt()
                    while self.isDigit(self.currentChar):
                        self.takeIt()

                if self.currentChar in ("e", "E"):

                    file_pos_backup = self.sourceFile.source.tell()
                    line_backup = self.currentLineNr
                    col_backup = self.currentColNr
                    lexeme_backup = self.currentLexeme

                    e_char = self.currentChar
                    peek1 = self.sourceFile.readChar()
                    if peek1 in ("+", "-"):
                        peek2 = self.sourceFile.readChar()
                        if not self.isDigit(peek2):

                            self.sourceFile.source.seek(file_pos_backup)
                            self.currentLineNr = line_backup
                            self.currentColNr = col_backup
                            self.currentLexeme = lexeme_backup
                            return tokenType
                        else:
                            self.takeIt()
                            self.currentLexeme += peek1
                            self.currentColNr += 1

                            self.currentLexeme += peek2
                            self.currentColNr += 1
                            while self.isDigit(self.currentChar):
                                self.takeIt()

                            tokenType = Token.FLOATLITERAL
                    elif self.isDigit(peek1):

                        self.takeIt()
                        self.currentLexeme += peek1
                        self.currentColNr += 1

                        while self.isDigit(self.currentChar):
                            self.takeIt()

                        tokenType = Token.FLOATLITERAL
                    else:

                        self.sourceFile.source.seek(file_pos_backup)
                        self.currentLineNr = line_backup
                        self.currentColNr = col_backup
                        self.currentLexeme = lexeme_backup
                        return tokenType

                    while self.isDigit(self.currentChar):
                        self.takeIt()

                    tokenType = Token.FLOATLITERAL

                return tokenType
            case ".":
                peek = self.sourceFile.readChar()
                if self.isDigit(peek):
                    tokenType = Token.FLOATLITERAL
                    self.takeIt()
                    self.currentLexeme += peek
                    self.currentColNr += 1

                    while self.isDigit(self.currentChar):
                        self.takeIt()

                    if self.currentChar in ("e", "E"):
                        file_pos_backup = self.sourceFile.source.tell()
                        line_backup = self.currentLineNr
                        col_backup = self.currentColNr
                        lexeme_backup = self.currentLexeme
                        e_char = self.currentChar
                        peek1 = self.sourceFile.readChar()
                        if peek1 in ("+", "-"):
                            peek2 = self.sourceFile.readChar()
                            if not self.isDigit(peek2):
                                self.sourceFile.source.seek(file_pos_backup)
                                self.currentLineNr = line_backup
                                self.currentColNr = col_backup
                                self.currentLexeme = lexeme_backup
                                return tokenType
                            else:
                                self.takeIt()
                                self.currentLexeme += peek1
                                self.currentColNr += 1
                                self.currentLexeme += peek2
                                self.currentColNr += 1
                                while self.isDigit(self.currentChar):
                                    self.takeIt()
                                tokenType = Token.FLOATLITERAL
                        elif self.isDigit(peek1):
                            self.takeIt()
                            self.currentLexeme += peek1
                            self.currentColNr += 1
                            while self.isDigit(self.currentChar):
                                self.takeIt()
                            tokenType = Token.FLOATLITERAL
                        else:
                            self.sourceFile.source.seek(file_pos_backup)
                            self.currentLineNr = line_backup
                            self.currentColNr = col_backup
                            self.currentLexeme = lexeme_backup
                            return tokenType

                        while self.isDigit(self.currentChar):
                            self.takeIt()
                        tokenType = Token.FLOATLITERAL
                    return tokenType
                else:
                    self.takeIt()
                    self.currentChar=peek
                    return Token.ERROR
            case '"':
                self.currentChar = self.sourceFile.readChar()
                self.currentColNr += 1
                while self.currentChar not in ('"', "\n", SourceFile.EOF):
                    if self.currentChar == "\\":
                        self.takeIt()
                        if self.currentChar != "n":
                            print("ERROR: illegal escape sequence")
                    self.takeIt()
                if self.currentChar == '"':
                    self.currentColNr += 1
                    self.currentChar = self.sourceFile.readChar()
                    return Token.STRINGLITERAL
                else:
                    print("ERROR: unterminated string literal")
                    return Token.STRINGLITERAL

            case c if c.isalpha() or c == "_":
                self.takeIt()
                while self.currentChar.isalnum() or self.currentChar == "_":
                    self.takeIt()
                lexeme = self.currentLexeme
                if lexeme == "bool":
                    return Token.BOOL
                elif lexeme == "else":
                    return Token.ELSE
                elif lexeme == "float":
                    return Token.FLOAT
                elif lexeme == "for":
                    return Token.FOR
                elif lexeme == "if":
                    return Token.IF
                elif lexeme == "int":
                    return Token.INT
                elif lexeme == "return":
                    return Token.RETURN
                elif lexeme == "void":
                    return Token.VOID
                elif lexeme == "while":
                    return Token.WHILE
                elif lexeme == "true" or lexeme == "false":
                    return Token.BOOLLITERAL
                else:
                    return Token.ID
            case "+":
                self.takeIt()
                return Token.PLUS
            case "-":
                self.takeIt()
                return Token.MINUS
            case "*":
                self.takeIt()
                return Token.TIMES

            case "/":
                next_char = self.sourceFile.readChar()
                if next_char == "/":
                    self.currentColNr += 2
                    self.currentChar = self.sourceFile.readChar()
                    while self.currentChar not in ("\n", SourceFile.EOF):
                        self.currentChar = self.sourceFile.readChar()
                        self.currentColNr += 1
                    if self.currentChar == "\n":
                        self.currentLineNr += 1
                        self.currentColNr = 1
                        self.currentChar = self.sourceFile.readChar()
                    return None
                elif next_char == "*":
                    self.currentColNr += 2
                    prevChar = ""
                    self.currentChar = self.sourceFile.readChar()
                    while True:
                        if self.currentChar == SourceFile.EOF:
                            print("ERROR: unterminated multi-line comment.")
                            self.currentLexeme += "$"
                            return Token.EOF
                        if prevChar == "*" and self.currentChar == "/":
                            self.currentChar = self.sourceFile.readChar()
                            self.currentColNr += 1
                            break
                        if self.currentChar == "\n":
                            self.currentLineNr += 1
                            self.currentColNr = 1
                        else:
                            self.currentColNr += 1
                        prevChar = self.currentChar
                        self.currentChar = self.sourceFile.readChar()
                    if self.currentChar == "\n":
                        self.currentLineNr += 1
                        self.currentColNr = 1
                        self.currentChar = self.sourceFile.readChar()
                    return None
                else:
                    self.takeIt()
                    self.currentChar = next_char
                    return Token.DIV
            case "=":
                self.takeIt()
                if self.currentChar == "=":
                    self.takeIt()
                    return Token.EQ
                return Token.ASSIGN
            case "!":
                self.takeIt()
                if self.currentChar == "=":
                    self.takeIt()
                    return Token.NOTEQ
                return Token.NOT
            case "<":
                self.takeIt()
                if self.currentChar == "=":
                    self.takeIt()
                    return Token.LESSEQ
                return Token.LESS
            case ">":
                self.takeIt()
                if self.currentChar == "=":
                    self.takeIt()
                    return Token.GREATEREQ
                return Token.GREATER
            case "&":
                self.takeIt()
                if self.currentChar == "&":
                    self.takeIt()
                    return Token.AND
                return Token.ERROR
            case "|":
                self.takeIt()
                if self.currentChar == "|":
                    self.takeIt()
                    return Token.OR
                return Token.ERROR
            case "{":
                self.takeIt()
                return Token.LEFTBRACE
            case "}":
                self.takeIt()
                return Token.RIGHTBRACE
            case "[":
                self.takeIt()
                return Token.LEFTBRACKET
            case "]":
                self.takeIt()
                return Token.RIGHTBRACKET
            case "(":
                self.takeIt()
                return Token.LEFTPAREN
            case ")":
                self.takeIt()
                return Token.RIGHTPAREN
            case ",":
                self.takeIt()
                return Token.COMMA
            case ";":
                self.takeIt()
                return Token.SEMICOLON
            case SourceFile.EOF:
                self.currentLexeme += "$"
                return Token.EOF
            case " " | "\t" | "\n" | "\r":
                self.currentlyScanningToken = False
                self.takeIt()
                self.currentlyScanningToken = True
                return self.scanToken()
            case _:
                self.takeIt()
                return Token.ERROR

    def scan(self):
        self.currentlyScanningToken = False
        while self.currentChar in (" ", "\f", "\n", "\r", "\t"):
            self.takeIt()

        self.currentlyScanningToken = True
        self.currentLexeme = ""

        pos = SourcePos()
        pos.StartLine = self.currentLineNr
        pos.StartCol = self.currentColNr

        kind = self.scanToken()
        while kind is None:
            pos.StartLine = self.currentLineNr
            pos.StartCol = self.currentColNr
            kind = self.scanToken()

        pos.EndLine = self.currentLineNr
        if kind == Token.EOF:
            pos.StartLine = self.currentLineNr
            pos.StartCol = self.currentColNr
            pos.EndCol = self.currentColNr
        else:
            pos.EndCol = self.currentColNr - 1

        currentToken = Token(kind, self.currentLexeme, pos)

        if self.verbose:
            print(currentToken)

        return currentToken
