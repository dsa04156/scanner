class SourceFile:
    EOL = '\n'
    EOF = ''
    def __init__(self, filename):
        self.source_file = filename
        self.source = open(filename, 'r')
    
    def readChar(self):
        try:
            c = self.source.read(1)
            if c == -1:
                c = SourceFile.EOF
            return c
        except:
            return SourceFile.EOF
