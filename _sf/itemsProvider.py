###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h


###################################################################################
###################################################################################
###################################################################################
class itemsProvider():

    ###################################################################################
    def __init__(self, basePath, forbiddenItems):
        self.basePath = os.path.abspath(basePath)
        self.forbiddenItems = forbiddenItems

    ###################################################################################
    def getFullPath(self, path):
        return os.path.abspath(h.makePath(self.basePath, path))

    ###################################################################################
    def getItems(self, path):
        fullPath = self.getFullPath(path)
        items = h.listDirectoryItems(fullPath, forbbidenItems=self.forbiddenItems)
        items = [item.replace(self.basePath, "") for item in items]
        return items

    ###################################################################################
    def doesItemExists(self, path):
        return os.path.exists(self.getFullPath(path))

    ###################################################################################
    def isItemLeaf(self, path):
        fullPath = self.getFullPath(path)
        if not os.path.exists(fullPath): return False
        return os.path.isfile(fullPath)

    ###################################################################################
    def isItemContainer(self, path):
        fullPath = self.getFullPath(path)
        if not os.path.exists(fullPath): return False
        return os.path.isdir(self.getFullPath(path))
