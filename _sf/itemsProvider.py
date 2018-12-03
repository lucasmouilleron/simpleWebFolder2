###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import authProvider as ap
import markdown2
import zipfile


###################################################################################
###################################################################################
###################################################################################
class itemsProvider():

    ###################################################################################
    def __init__(self, ap: ap.authProvider, basePath):
        self.basePath = os.path.abspath(basePath)
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
    def getZipFile(self, path, r):
        if not self.doesItemExists(path): return None
        fullPath = self.getFullPath(path)
        zipFilePath = h.makePath(h.TMP_FOLDER, h.uniqueID())
        try:
            zipf = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(fullPath):
                dirs[:] = [d for d in dirs if not self.ap.isForbidden(d.replace(self.basePath, ""))]
                dirs[:] = [d for d in dirs if self.ap.isAuthorized(d.replace(self.basePath, ""), r)[3]]
                for f in files:
                    fpath = h.makePath(root, f)
                    frpath = fpath.replace(self.basePath, "")
                    if self.ap.isForbidden(frpath): continue
                    zipf.write(fpath, arcname=frpath)
            return zipFilePath
        except Exception as e:
            os.remove(zipFilePath)
            raise (e)

    ###################################################################################
    def getItems(self, path, r):
        if not self.doesItemExists(path): return [], []
        if self.ap.listingForbidden(path): return [], []
        fullPath = self.getFullPath(path)
        items = h.listDirectoryItems(fullPath)
        itemsContainers = []
        for item in items:
            if not os.path.isdir(item): continue
            itemPath = item.replace(self.basePath, "")
            if self.ap.isForbidden(itemPath): continue
            if self.ap.showForbidden(itemPath): continue
            _, _, _, isAuthorized = self.ap.isAuthorized(itemPath, r)
            itemsContainers.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "nbItems": len(h.listDirectoryItems(item)), "isAuthorized": isAuthorized})
        itemsLeafs = []
        for item in items:
            if not os.path.isfile(item): continue
            itemPath = item.replace(self.basePath, "")
            if self.ap.isForbidden(itemPath): continue
            itemsLeafs.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "extension": os.path.splitext(item)[-1].replace(".", ""), "size": os.path.getsize(item)})
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
