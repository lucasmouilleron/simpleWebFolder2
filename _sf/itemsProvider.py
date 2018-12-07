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
    def __init__(self, ap: ap.authProvider, basePath, maxZipSize=50e6, tmpFolder=None, tmpFolderDuration=None, user=None):
        self.basePath = os.path.abspath(basePath)
        self.maxZipSize = maxZipSize
        self.tmpFolder = tmpFolder.lstrip("/")
        self.tmpFolderDuration = tmpFolderDuration
        self.user = h.getUserID(user)
        self.ap = ap

        if self.tmpFolder is not None:
            tmpPath = h.makePath(self.basePath, self.tmpFolder)
            if not os.path.exists(tmpPath):
                h.makeDir(tmpPath)
                if self.user is not None: h.changeFileOwner(tmpPath, self.user)
            ap.setListingForbidden(self.tmpFolder)
            ap.setDownloadForbidden(self.tmpFolder)
            ap.setShowForbidden(self.tmpFolder)
            ap.setShareForbidden(self.tmpFolder)
            ap.setAddAllowed(self.tmpFolder)

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
        addedSize = 0
        if not self.doesItemExists(path): return None
        fullPath = self.getFullPath(path)
        zipFilePath = h.makePath(h.TMP_FOLDER, h.uniqueID())
        try:
            zipf = zipfile.ZipFile(zipFilePath, "w", zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(fullPath):
                dirs[:] = [d for d in dirs if not self.ap.isForbidden(d.replace(self.basePath, ""))]
                dirs[:] = [d for d in dirs if self.ap.isAuthorized(d.replace(self.basePath, ""), r)[3]]
                dirs[:] = [d for d in dirs if not self.ap.downloadForbidden(d.replace(self.basePath, ""))]
                for f in files:
                    fpath = h.makePath(root, f)
                    frpath = fpath.replace(self.basePath, "")
                    if self.ap.isForbidden(frpath): continue
                    addedSize += h.getFileSize(fpath)
                    if addedSize > self.maxZipSize: break
                    zipf.write(fpath, arcname=frpath)
                if addedSize > self.maxZipSize:
                    h.logDebug("Max zip file size reached", path, self.maxZipSize)
                    break
            return zipFilePath
        except Exception as e:
            os.remove(zipFilePath)
            raise (e)

    ###################################################################################
    def getItems(self, path, r=None, asAdmin=False, overrideListingForbidden=False, overrideNoShow=False):
        if not self.doesItemExists(path): return [], []
        if not overrideListingForbidden and not asAdmin and self.ap.listingForbidden(path): return [], []
        fullPath = self.getFullPath(path)
        items = h.listDirectoryItems(fullPath)
        itemsContainers = []
        for item in items:
            if not os.path.isdir(item): continue
            itemPath = item.replace(self.basePath, "")
            if itemPath.lstrip("/").startswith("_sf"): continue
            isForbidden = self.ap.isForbidden(itemPath)
            if not asAdmin and isForbidden: continue
            showForbidden = self.ap.showForbidden(itemPath)
            if not overrideNoShow and not asAdmin and showForbidden: continue
            if r is not None: protected, requiredPasswords, _, isAuthorized, lowerProtectedPath = self.ap.isAuthorized(itemPath, r)
            else: isAuthorized, requiredPasswords, protected = True, "", False
            if asAdmin: isAuthorized = True
            listingForbidden = self.ap.listingForbidden(itemPath)
            shareForbidden = self.ap.shareForbidden(itemPath)
            addAllowed = self.ap.isAddAllowed(itemPath)
            isTmpFolder = itemPath.lstrip("/") == self.tmpFolder
            itemsContainers.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "nbItems": len(h.listDirectoryItems(item)), "isAuthorized": isAuthorized, "passwords": requiredPasswords, "protected": protected, "forbidden": isForbidden, "showForbidden": showForbidden, "listingForbidden": listingForbidden, "shareForbidden": shareForbidden, "isTmpFolder": isTmpFolder, "addAllowed": addAllowed})
        itemsLeafs = []
        for item in items:
            if not os.path.isfile(item): continue
            itemPath = item.replace(self.basePath, "")
            if itemPath.lstrip("/").startswith("_sf"): continue
            isForbidden = self.ap.isForbidden(itemPath)
            if not asAdmin and isForbidden: continue
            if r is not None: protected, requiredPasswords, _, isAuthorized, lowerProtectedPath = self.ap.isAuthorized(itemPath, r)
            else: isAuthorized, requiredPasswords, protected = True, "", False
            if asAdmin: isAuthorized = True
            itemsLeafs.append({"path": itemPath, "name": os.path.basename(item), "lastModified": os.stat(item).st_mtime, "extension": os.path.splitext(item)[-1].replace(".", ""), "size": os.path.getsize(item), "isAuthorized": isAuthorized, "passwords": requiredPasswords, "protected": protected, "forbidden": isForbidden})
        return itemsContainers, itemsLeafs

    ###################################################################################
    def addLead(self, path, file):
        try:
            bits = list(os.path.splitext(file.filename))
            ext = bits.pop()
            filename = "%s%s" % ( "".join(bits), ext)
            file.save(h.makePath(self.basePath, path, filename))
            return True, filename
        except:
            le, lt = h.getLastExceptionAndTrace()
            return False, le

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
