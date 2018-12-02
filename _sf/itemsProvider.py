###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import authProvider as ap


###################################################################################
###################################################################################
###################################################################################
class itemsProvider():

    ###################################################################################
    def __init__(self, ap: ap.authProvider, basePath, forbiddenItems):
        self.basePath = os.path.abspath(basePath)
        self.forbiddenItems = forbiddenItems
        self.ap = ap

    ###################################################################################
    def getFullPath(self, path):
        return os.path.abspath(h.makePath(self.basePath, path))

    ###################################################################################
    def getItems(self, path, r):
        fullPath = self.getFullPath(path)
        items = h.listDirectoryItems(fullPath, forbbidenItems=self.forbiddenItems)
        itemsContainers = []
        for item in items:
            if not os.path.isdir(item): continue
            itemPath = item.replace(self.basePath, "")
            _, _, _, isAuthorized = self.ap.isAuthorized(itemPath, r)
            itemsContainers.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "nbItems": len(h.listDirectoryItems(item)), "isAuthorized": isAuthorized})
        itemsLeafs = []
        for item in items:
            if not os.path.isfile(item): continue
            extension, _ = os.path.splitext(item)
            itemsLeafs.append({"path": item.replace(self.basePath, ""), "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "extension": extension, "size": os.path.getsize(item)})
        return itemsContainers, itemsLeafs

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
