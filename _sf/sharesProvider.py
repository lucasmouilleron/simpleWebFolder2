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
class sharesProvider():

    ###################################################################################
    def __init__(self, ap: ap.authProvider, sharesPath):
        self.sharesPath = os.path.abspath(sharesPath)
        self.ap = ap

    ###################################################################################
    def listShares(self, filterID=None):
        shares = []
        items = h.listDirectoryItems(self.sharesPath, onlyFiles=True)
        for item in items:
            shareID = os.path.basename(item)
            if filterID is not None and filterID not in shareID: continue
            shares.append(self.getShare(shareID))
        return shares

    ###################################################################################
    def getShare(self, shareID):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): raise Exception("Unknown share", shareID)
        lh = None
        try:
            lockFile = h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % shareID)
            lh = h.getLockShared(lockFile, 5)
            return h.loadJsonFile(sharePath)
        finally:
            if lh is not None: h.releaseLock(lh)
