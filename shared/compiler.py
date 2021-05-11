import json

class Compiler():
    def __init__(self,paramCompilerCfgPath):
        self.compilerCfgPath = paramCompilerCfgPath
        self.cores = None

        self.parseCompilerCfg()

    def parseCompilerCfg(self):
        with open(self.compilerCfgPath, 'r') as compilerCfgFile:
            compilerCfgFileInput=compilerCfgFile.read()

        compilerCfg = json.loads(compilerCfgFileInput)

        self.cores = compilerCfg['cores']