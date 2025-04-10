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

    # takeIt appends the current character to the current token, and gets
    # the next character from the source program (or the to-be-implemented
    # "untake" buffer in case of look-ahead characters that got 'pushed back'
    # into the input stream).

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
                # 소수점 처리
                if self.currentChar == ".":
                    tokenType = Token.FLOATLITERAL
                    self.takeIt()
                    while self.isDigit(self.currentChar):
                        self.takeIt()
                        

                # 지수 처리 (e 또는 E)
                if self.currentChar in ("e", "E"):
                    # 상태 저장 (rollback 대비)
                    savedLine = self.currentLineNr
                    savedCol = self.currentColNr
                    savedChar = self.currentChar
                    savedLexeme = self.currentLexeme

                    self.takeIt()  # e 또는 E 소비

                    # 부호 있으면 소비
                    if self.currentChar in ("+", "-"):
                        savedLine = self.currentLineNr
                        savedCol = self.currentColNr
                        savedChar = self.currentChar
                        savedLexeme = self.currentLexeme
                        self.takeIt()

                    # 지수 다음에 숫자가 반드시 와야 함!
                    if not self.isDigit(self.currentChar):
                        # 롤백 (지수 표기 전으로 복원)
                        self.currentLineNr = savedLine
                        self.currentColNr = savedCol
                        self.currentChar = savedChar
                        self.currentLexeme = savedLexeme
                        return tokenType  # 지수 표기 전의 INT or FLOAT 리터럴로 종료

                    # 지수 숫자 소비
                    while self.isDigit(self.currentChar):
                        self.takeIt()

                    tokenType = Token.FLOATLITERAL  # 지수까지 유효하므로 무조건 float

                return tokenType

            # 문자열 리터럴: "로 시작하며 동일한 줄 내에서 종료되어야 함.
            case '"':
                self.takeIt()  # 시작 "
                while self.currentChar not in ('"', "\n", SourceFile.EOF):
                    if self.currentChar == "\\":
                        self.takeIt()  # 이스케이프 문자 소비
                        if self.currentChar != "n":
                            print("ERROR: Invalid escape sequence")
                    self.takeIt()
                if self.currentChar == '"':
                    self.takeIt()  # 종료 "
                    return Token.STRINGLITERAL
                else:
                    # Case (3): 문자열이 줄바꿈 또는 EOF로 인해 종료되지 않음
                    print("ERROR: Unterminated string literal")
                    return Token.STRINGLITERAL

            # 식별자 또는 키워드: letter 혹은 '_'로 시작하고, 이후 letter, digit, '_' 지속
            case c if c.isalpha() or c == "_":
                self.takeIt()
                while self.currentChar.isalnum() or self.currentChar == "_":
                    self.takeIt()
                # 이제 현재까지 읽은 lexeme을 사용하여 키워드 여부를 확인합니다.
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
                else:
                    return Token.ID

            # 연산자 및 구분자들
            case "+":
                self.takeIt()
                return Token.PLUS
            case "-":
                self.takeIt()
                return Token.MINUS
            case "*":
                self.takeIt()
                return Token.TIMES
            case '/':
                # 다음 문자를 미리 읽어서 검사
                next_char = self.sourceFile.readChar()

                if next_char == '/':
                    # 한 줄 주석 처리
                    self.currentChar = self.sourceFile.readChar()
                    while self.currentChar not in ('\n', SourceFile.EOF):
                        self.currentChar = self.sourceFile.readChar()
                    
                    # 줄 바꿈 후 다음 문자를 소비
                    if self.currentChar == '\n':
                        self.currentLineNr += 1
                        self.currentColNr = 1
                        self.currentChar = self.sourceFile.readChar()
                    
                    # 주석 이후 다음 유효 토큰을 찾기 위해 재귀 호출
                    return self.scanToken()
                
                elif next_char == '*':
                    # 여러 줄 주석 처리 (/* */)
                    self.currentChar = self.sourceFile.readChar()

                    while True:
                        if self.currentChar == SourceFile.EOF:
                            print("ERROR: Unterminated comment")
                            return Token.EOF

                        elif self.currentChar == '*':
                            # '*' 다음 문자를 미리 확인
                            next_next_char = self.sourceFile.readChar()
                            if next_next_char == '/':
                                # 주석 종료 ('*/') 처리 완료
                                self.currentChar = self.sourceFile.readChar()
                                break
                            else:
                                # '*' 뒤의 문자가 '/'가 아니라면 계속 진행
                                self.currentChar = next_next_char
                        else:
                            # 일반 문자 처리
                            if self.currentChar == '\n':
                                self.currentLineNr += 1
                                self.currentColNr = 1
                            self.currentChar = self.sourceFile.readChar()

                    # 주석 이후의 토큰을 찾기 위해 재귀 호출
                    return self.scanToken()
                else:
                    # '/' 단독 처리 (연산자 토큰)
                    self.takeIt()  # 현재 '/' 소비
                    self.currentChar = next_char  # 다음 문자 설정
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
                # 마지막 줄이 끝난 후 다음 줄에서 EOF가 온다고 가정
                self.currentLineNr += 1
                self.currentColNr = 1
                return Token.EOF
            # 그 외: 미리 정의되지 않은 문자 → ERROR 토큰
            case _:
                self.takeIt()
                return Token.ERROR

    def scan(self):
        self.currentlyScanningToken = False
        while self.currentChar in (" ", "\f", "\n", "\r", "\t"):
            self.takeIt()

        self.currentlyScanningToken = True
        self.currentLexeme = ""

        # ✅ 여기가 정확한 토큰 시작 지점
        pos = SourcePos()
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
