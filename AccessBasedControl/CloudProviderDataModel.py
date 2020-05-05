class CloudProviderDataModel:
    def __init__(self, cloudProviderID, cloudProviderName, storageSpace=0, usageCostPerGB=0):
        self.cloudProviderID = cloudProviderID
        self.cloudProviderName = cloudProviderName
        self.storageSpace = storageSpace
        self.usageCostPerGB = usageCostPerGB
