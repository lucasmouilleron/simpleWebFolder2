###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import authProvider as ap


###################################################################################
###################################################################################
###################################################################################
class sharesProvider():

    ###################################################################################
    def __init__(self, ap: ap.authProvider, sharesPath, user=None):
        self.user = h.getUserID(user)
        self.sharesPath = h.makeDirPath(os.path.abspath(sharesPath))
        if self.user is not None: h.changeFileOwner(self.sharesPath, self.user)
        self.ap = ap

    ###################################################################################
    def listShares(self, filterID=None, maxShares=None):
        shares = []
        items = h.listDirectoryItems(self.sharesPath, onlyFiles=True)
        for item in items:
            shareID = os.path.basename(item)
            if filterID is not None and filterID not in shareID: continue
            shares.append(self.getShare(shareID, asAdmin=True)[0])
        shares = sorted(shares, key=lambda d: d["creation"])[::-1]
        if maxShares is not None: return shares[0:min(maxShares, len(shares))]
        else: return shares

    ###################################################################################
    def addShare(self, shareID, path, duration, password):
        path = path.lstrip("/").rstrip("/")
        sharePath = h.makePath(self.sharesPath, shareID)
        duration = h.parseInt(duration, 0)
        password = "" if password is None else password
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % h.clean(shareID)), 5)
            share = {"ID": shareID, "file": path, "duration": duration, "password": password, "creation": h.now()}
            h.writeJsonFile(sharePath, share)
            if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return share, "ok"
        except:
            le, lt = h.getLastExceptionAndTrace()
            return None, le
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getShare(self, shareID, r=None, subPath=None, asAdmin=False):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): return None
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % h.clean(shareID)), 5)
            share = h.loadJsonFile(sharePath)
            if not asAdmin:
                views = share.get("views", [])
                view = {"date": h.now()}
                if r is not None: view["ip"] = r.remote_addr
                if subPath is not None: view["item"] = h.makePath(share["file"], subPath)
                views.append(view)
                share["views"] = views
                h.writeJsonFile(sharePath, share)
                if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return share, "ok"
        except:
            le, lt = h.getLastExceptionAndTrace()
            return None, le
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def removeShare(self, shareID):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): raise Exception("Unknown share", shareID)
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % h.clean(shareID)), 5)
            os.remove(sharePath)
            return True
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def shareExists(self, shareID):
        return os.path.exists(h.makePath(self.sharesPath, shareID))
