class RoleModel:
    def __init__(self, roleID, roleName, canCloudProvider=0, canVideoData=0, canBlockchainGeneration=0, canBlockchainReport=0, canRole=0, canUser=0):
        self.roleID = roleID
        self.roleName = roleName
        self.canCloudProvider = canCloudProvider
        self.canVideoData = canVideoData
        self.canBlockchainGeneration = canBlockchainGeneration
        self.canBlockchainReport = canBlockchainReport
        self.canRole = canRole
        self.canUser = canUser
        
        
        
        