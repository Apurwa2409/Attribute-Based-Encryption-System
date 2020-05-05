class CloudReportModel:
    def __init__(self, cloudProviderName="", storageSpace=0, usageCostPerGB=0.0, totalUsedStorage=0.0,   totalUsageCost=0.0):
        self.cloudProviderName = cloudProviderName
        self.storageSpace = storageSpace
        self.totalUsedStorage = totalUsedStorage
        self.usageCostPerGB = usageCostPerGB
        self.totalUsageCost = totalUsageCost
