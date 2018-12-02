###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import authProvider as ap
import markdown2


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
    def getReadme(self, path):
        readmeFile = h.makePath(self.getFullPath(path), "README.md")
        if not os.path.exists(readmeFile): return None
        return markdown2.markdown(h.readFromFile(readmeFile))

    ###################################################################################
    def getItems(self, path, r):
        if not self.doesItemExists(path): return [], []
        if self.ap.listingForbidden(path): return [], []
        fullPath = self.getFullPath(path)
        items = h.listDirectoryItems(fullPath, forbbidenItems=self.forbiddenItems)
        itemsContainers = []
        for item in items:
            if not os.path.isdir(item): continue
            itemPath = item.replace(self.basePath, "")
            if self.ap.showForbidden(itemPath): continue
            _, _, _, isAuthorized = self.ap.isAuthorized(itemPath, r)
            itemsContainers.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "nbItems": len(h.listDirectoryItems(item)), "isAuthorized": isAuthorized})
        itemsLeafs = []
        for item in items:
            if not os.path.isfile(item): continue
            itemsLeafs.append({"path": item.replace(self.basePath, ""), "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "extension": os.path.splitext(item)[-1].replace(".", ""), "size": os.path.getsize(item)})
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
