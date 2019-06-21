###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import authProvider as ap
import markdown2
import zipfile
from threading import Thread
import threading
from typing import List


###################################################################################
###################################################################################
###################################################################################
class item:
    def __init__(self, path, name, lastModified, isAuthorized, protected, forbidden, showForbidden, listingForbidden, downloadForbidden, shareForbidden, passwordEditForbidden, isTmpFolder, editAllowed, leaf, container, lowerProtectedPath, nbItems=0, passwords=[], expires=0, size=0, extension="", savedPassword="", protectedFromParent=False):
        self.path = path
        self.name = name
        self.lastModified = lastModified
        self.nbItems = nbItems
        self.isAuthorized = isAuthorized
        self.passwords = passwords
        self.protected = protected
        self.protectedFromParent = protectedFromParent
        self.forbidden = forbidden
        self.showForbidden = showForbidden
        self.listingForbidden = listingForbidden
        self.downloadForbidden = downloadForbidden
        self.passwordEditForbidden = passwordEditForbidden
        self.shareForbidden = shareForbidden
        self.isTmpFolder = isTmpFolder
        self.editAllowed = editAllowed
        self.expires = expires
        self.leaf = leaf
        self.container = container
        self.size = size
        self.extension = extension
        self.savedPassword = savedPassword
        self.lowerProtectedPath = lowerProtectedPath


###################################################################################
###################################################################################
###################################################################################
class itemsProvider():

    ###################################################################################
    def __init__(self, ap: ap.authProvider, basePath, maxZipSize=50e6, tmpFolder=None, tmpFolderDuratioInDaysn=7, user=None, hiddenItems=None):
        if hiddenItems is None: hiddenItems = []
        self.hiddenItems = set(hiddenItems)
        self.basePath = os.path.abspath(basePath)
        self.maxZipSize = maxZipSize
        self.tmpFolder = tmpFolder.lstrip("/")
        self.tmpFolderDuration = tmpFolderDuratioInDaysn * 24 * 60 * 60
        self.user = h.getUserID(user)
        self.ap = ap
        self.cleanTmpThread = None

        if self.tmpFolder is not None:
            tmpPath = h.makePath(self.basePath, self.tmpFolder)
            if not os.path.exists(tmpPath):
                h.makeDir(tmpPath)
                if self.user is not None: h.changeFileOwner(tmpPath, self.user)
            ap.setListingForbidden(self.tmpFolder)
            ap.setDownloadForbidden(self.tmpFolder)
            ap.setShowForbidden(self.tmpFolder)
            ap.setShareForbidden(self.tmpFolder)
            ap.setEditAllowed(self.tmpFolder)
            self.cleanTmpThread = CleanTmp(tmpPath, self.tmpFolderDuration)
            self.cleanTmpThread.start()

    ###################################################################################
    def stop(self):
        if self.cleanTmpThread is not None: self.cleanTmpThread.interrupt()

    ###################################################################################
    def _isFullPathWithinBaseFolder(self, fullPath):
        return h.cleanPath(self.basePath) in fullPath

    ###################################################################################
    def getFullPath(self, path):
        path = h.cleanPath(path)
        fullPath = os.path.abspath(h.makePath(self.basePath, path))
        if not self._isFullPathWithinBaseFolder(fullPath): return self.basePath
        return fullPath

    ###################################################################################
    def getReadme(self, path):
        path = h.cleanPath(path)
        readmeFile = h.makePath(self.getFullPath(path), "README.md")
        if not os.path.exists(readmeFile): return None
        return markdown2.markdown(h.readFromFile(readmeFile))

    ###################################################################################
    def getReadmeAdmin(self, path):
        path = h.cleanPath(path)
        readmeFile = h.makePath(self.getFullPath(path), "README.admin.md")
        if not os.path.exists(readmeFile): return self.getReadme(path)
        return markdown2.markdown(h.readFromFile(readmeFile))

    ###################################################################################
    def getZipFile(self, path, r):
        path = h.cleanPath(path)
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
    def getItem(self, path, r=None, asAdmin=False) -> item:
        path = h.cleanPath(path)
        if not self.doesItemExists(path): return None
        fullPath = h.makePath(self.basePath, path)
        isLeaf = self.isItemLeaf(path)
        isContainer = not isLeaf
        if r is not None: protected, requiredPasswords, savedPassword, isAuthorized, lowerProtectedPath, protectedFromParent = self.ap.isAuthorized(path, r)
        else: isAuthorized, requiredPasswords, protected, savedPassword, lowerProtectedPath, protectedFromParent = True, "", False, "", "", False
        if asAdmin: isAuthorized = True
        if isLeaf:
            extension = os.path.splitext(path)[-1].replace(".", "")
            size = os.path.getsize(fullPath)
            nbItems = 0
            isTmpFolder = False
        else:
            extension = ""
            size = 0
            nbItems = len(h.listDirectoryItems(fullPath))
            isTmpFolder = path.lstrip("/") == self.tmpFolder
        isForbidden = self.ap.isForbidden(path)
        listingForbidden = self.ap.listingForbidden(path)
        shareForbidden = self.ap.shareForbidden(path)
        showForbidden = self.ap.showForbidden(path)
        editAllowed = self.ap.isEditAllowed(path)
        downloadForbidden = self.ap.downloadForbidden(path)
        passwordEditForbidden = self.ap.passwordEditForbidden(path)
        expires = h.getFileModified(h.makePath(self.basePath, path)) + self.tmpFolderDuration

        return item(path, os.path.basename(path), os.stat(fullPath).st_mtime, isAuthorized, protected, isForbidden, showForbidden, listingForbidden, downloadForbidden, shareForbidden, passwordEditForbidden, isTmpFolder, editAllowed, isLeaf, isContainer, lowerProtectedPath, nbItems, requiredPasswords, expires, size, extension, savedPassword, protectedFromParent)

    ###################################################################################
    def getItems(self, path, r=None, asAdmin=False, overrideListingForbidden=False, overrideNoShow=False) -> (List[item], List[item]):
        path = h.cleanPath(path)
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
            i = self.getItem(itemPath, r, asAdmin)
            if i is not None: itemsContainers.append(i)
        itemsLeafs = []
        for item in items:
            if not os.path.isfile(item): continue
            if self.isHiddenForListings(item): continue
            itemPath = item.replace(self.basePath, "")
            if itemPath.lstrip("/").startswith("_sf"): continue
            isForbidden = self.ap.isForbidden(itemPath)
            if not asAdmin and isForbidden: continue
            i = self.getItem(itemPath, r, asAdmin)
            if i is not None: itemsLeafs.append(i)
        return itemsContainers, itemsLeafs

    ###################################################################################
    def isHiddenForListings(self, item):
        return os.path.basename(item) in self.hiddenItems

    ###################################################################################
    def getPotentialLeafName(self, file):
        bits = list(os.path.splitext(file.filename))
        ext = bits.pop()
        filename = "%s%s" % ("".join(bits), ext)
        return filename

    ###################################################################################
    def addLeaf(self, path, file):
        path = h.cleanPath(path)
        try:
            if not self.doesItemExists(path): return False, "Container does not exists"
            filename = self.getPotentialLeafName(file)
            if self.isItemLeaf(h.makePath(path, filename)): return False, "Item already exists"
            if self.isItemContainer(h.makePath(path, filename)): return False, "Item already exists"

            file.save(h.makePath(self.basePath, path, filename))
            return True, filename
        except:
            le, lt = h.getLastExceptionAndTrace()
            return False, le

    ###################################################################################
    def remove(self, path):
        path = h.cleanPath(path)
        if self.doesItemExists(path) and self.ap.isEditAllowed(self.getParent(path)):
            h.delete(self.getFullPath(path))
            return True
        else: return False

    ###################################################################################
    def doesItemExists(self, path):
        path = h.cleanPath(path)
        return os.path.exists(self.getFullPath(path))

    ###################################################################################
    def isItemLeaf(self, path):
        path = h.cleanPath(path)
        fullPath = self.getFullPath(path)
        if not os.path.exists(fullPath): return False
        return os.path.isfile(fullPath)

    ###################################################################################
    def isItemContainer(self, path):
        path = h.cleanPath(path)
        fullPath = self.getFullPath(path)
        if not os.path.exists(fullPath): return False
        return os.path.isdir(self.getFullPath(path))

    ###################################################################################
    def getParent(self, path):
        path = h.cleanPath(path)
        return os.path.dirname(path)


###################################################################################
###################################################################################
###################################################################################
class CleanTmp(Thread):

    ###################################################################################
    def __init__(self, tmpFolder, tmpDuration):
        Thread.__init__(self)
        self._interrupt = False
        self._exitEvent = threading.Event()
        self.tmpFolder = tmpFolder
        self.tmpDuration = tmpDuration

    ###################################################################################
    def run(self):
        while not self._interrupt and not self._exitEvent.isSet():
            try:
                items = h.listDirectoryItems(self.tmpFolder)
                for item in items:
                    if h.getFileModified(item) + self.tmpDuration < h.now():
                        h.delete(item)
                        h.logInfo("Item too old deleted %s" % item)
            except:
                print(h.getLastExceptionAndTrace())
            finally: self._exitEvent.wait(500)

        h.logDebug("CleanTmp thread finished")

    ###################################################################################
    def interrupt(self):
        self._interrupt = True
        self._exitEvent.set()
