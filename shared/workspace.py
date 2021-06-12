import os
import json

class Workspace():
    def __init__(self,workspacePath):
        with open(workspacePath, 'r') as workspaceFile:
            workspaceInput=workspaceFile.read()

        workspace = json.loads(workspaceInput)

        self.CosmOSCorePath = workspace['CosmOSCorePath']
        self.CosmOSGeneratedCorePath = workspace['CosmOSGeneratedCorePath']
        self.CosmOSIntegrationLayerPath = workspace['CosmOSIntegrationLayerPath']
        self.CosmOSApplicationLayerPath = workspace['CosmOSApplicationLayerPath']
        self.mcuCfgPath = workspace['mcuCfgPath']
        self.CosmOSCoreTemplatesPath = workspace['CosmOSCoreTemplatesPath']
        self.CosmOSIntegrationLayerTemplatesPath = workspace['CosmOSIntegrationLayerTemplatesPath']
        self.CosmOSApplicationLayerTemplatesPath = workspace['CosmOSApplicationLayerTemplatesPath']
        self.CosmOSApplicationLayerSourceTemplateName = workspace['CosmOSApplicationLayerSourceTemplateName']
        self.CosmOSApplicationLayerHeaderTemplateName = workspace['CosmOSApplicationLayerHeaderTemplateName']
        self.LinkerScriptTemplatePath = workspace['LinkerScriptTemplatePath']
        self.systemModelCfgPath = workspace['systemModelCfgPath']
        self.compilerCfgPath = workspace['compilerCfgPath']
        self.LinkerTemplateName = workspace['LinkerTemplateName']
        self.linkerScriptPaths = workspace['linkerScriptPaths']

        if ( workspace['stmProject'] == True ):
            self.cprojectPaths = workspace['cprojectPaths']
            self.projectPaths = workspace['projectPaths']

        self.CosmOSCoreModules = [d for d in os.listdir(self.CosmOSCorePath) if not(os.path.isfile(d)) and (not d.startswith('.'))]
        self.CosmOSGeneratedCoreModules = [d for d in os.listdir(self.CosmOSGeneratedCorePath) if not(os.path.isfile(d)) and (not d.startswith('.'))]
