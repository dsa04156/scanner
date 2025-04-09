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
        self.currentLineNr = 1
        self.currentColNr = 1

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
        if self.currentChar == '\n':
            self.currentLineNr += 1
            self.currentColNr = 1
        else:
            self.currentColNr += 1
        self.currentChar = self.sourceFile.readChar()
    
    def scanToken(self):
        match self.currentChar:
 # 숫자 리터럴: 정수 또는 부동소수점 숫자
            case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                self.takeIt()    # 첫 번째 자리 숫자 소비
                while self.isDigit(self.currentChar):
                    self.takeIt()
                tokenType = Token.INTLITERAL  # 기본적으로 정수 토큰으로 간주

                # 소수점 처리: 점(.)을 만나면 부동소수점 토큰으로 전환
                if self.currentChar == '.':
                    tokenType = Token.FLOATLITERAL
                    self.takeIt()
                    while self.isDigit(self.currentChar):
                        self.takeIt()
                
                # 지수(exponent) 처리: 'e' 또는 'E'를 만나면 부동소수점 토큰으로 전환
                if self.currentChar in ('e', 'E'):
                    tokenType = Token.FLOATLITERAL
                    self.takeIt()
                    if self.currentChar in ('+', '-'):
                        self.takeIt()
                    if not self.isDigit(self.currentChar):
                        print("ERROR: Malformed exponent in float literal")
                        return Token.FLOATLITERAL
                    while self.isDigit(self.currentChar):
                        self.takeIt()
                
                return tokenType


            # 문자열 리터럴: "로 시작하며 동일한 줄 내에서 종료되어야 함.
            case '"':
                self.takeIt()  # 시작 "
                while self.currentChar not in ('"', '\n', SourceFile.EOF):
                    if self.currentChar == '\\':
                        self.takeIt()  # 이스케이프 문자 소비
                        if self.currentChar != 'n':
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
            case c if (c.isalpha() or c == '_'):
                self.takeIt()
                while self.currentChar.isalnum() or self.currentChar == '_':
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
            case '+':
                self.takeIt()
                return Token.PLUS
            case '-':
                self.takeIt()
                return Token.MINUS
            case '*':
                self.takeIt()
                return Token.TIMES
            case '/':
                self.takeIt()  # 첫 번째 '/' 소비
                # peekChar() 대신에, 다음 문자를 바로 읽어 임시 변수에 저장
                temp = self.sourceFile.readChar()
                if temp == '/':
                    # 주석임: 두 번째 '/'도 소비
                    # temp를 이미 읽었으므로, currentChar 대신 이를 사용
                    self.currentChar = temp
                    # 주석 내용은 줄바꿈 또는 EOF가 나올 때까지 소비
                    while self.currentChar not in ('\n', SourceFile.EOF):
                        self.takeIt()
                    return self.scanToken()
                else:
                    # 주석이 아니므로, temp를 currentChar에 할당하여 나중에 그대로 사용
                    self.currentChar = temp
                    return Token.DIV


            case '=':
                self.takeIt()
                if self.currentChar == '=':
                    self.takeIt()
                    return Token.EQ
                return Token.ASSIGN
            case '!':
                self.takeIt()
                if self.currentChar == '=':
                    self.takeIt()
                    return Token.NOTEQ
                return Token.NOT
            case '<':
                self.takeIt()
                if self.currentChar == '=':
                    self.takeIt()
                    return Token.LESSEQ
                return Token.LESS
            case '>':
                self.takeIt()
                if self.currentChar == '=':
                    self.takeIt()
                    return Token.GREATEREQ
                return Token.GREATER
            case '&':
                self.takeIt()
                if self.currentChar == '&':
                    self.takeIt()
                    return Token.AND
                return Token.ERROR
            case '|':
                self.takeIt()
                if self.currentChar == '|':
                    self.takeIt()
                    return Token.OR
                return Token.ERROR
            case '{':
                self.takeIt()
                return Token.LEFTBRACE
            case '}':
                self.takeIt()
                return Token.RIGHTBRACE
            case '[':
                self.takeIt()
                return Token.LEFTBRACKET
            case ']':
                self.takeIt()
                return Token.RIGHTBRACKET
            case '(':
                self.takeIt()
                return Token.LEFTPAREN
            case ')':
                self.takeIt()
                return Token.RIGHTPAREN
            case ',':
                self.takeIt()
                return Token.COMMA
            case ';':
                self.takeIt()
                return Token.SEMICOLON
            case SourceFile.EOF:
                self.currentLexeme += '$'
                return Token.EOF
            # 그 외: 미리 정의되지 않은 문자 → ERROR 토큰
            case _:
                self.takeIt()
                return Token.ERROR
    
    def scan(self):
        self.currentlyScanningToken = False
        while self.currentChar in (' ', '\f', '\n', '\r', '\t'):
            self.takeIt()
        
        self.currentlyScanningToken = True
        self.currentLexeme = ""
        pos = SourcePos()
        pos.StartLine = self.currentLineNr
        pos.StartCol = self.currentColNr
        kind = self.scanToken()
        pos.EndLine = self.currentLineNr
        if kind == Token.EOF:
            pos.EndCol = self.currentColNr
        else:
            pos.EndCol = self.currentColNr-1
        currentToken = Token(kind, self.currentLexeme, pos)

        if self.verbose:
            print(currentToken)
        
        return currentToken
