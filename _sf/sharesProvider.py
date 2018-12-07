###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h


###################################################################################
###################################################################################
###################################################################################
class share:
    def __init__(self, ID, creation, file, views, password, duration):
        self.ID = ID
        self.creation = creation
        self.file = file
        self.views = views
        self.password = password
        self.duration = duration


###################################################################################
###################################################################################
###################################################################################
class sharesProvider():

    ###################################################################################
    def __init__(self, sharesPath, user=None):
        self.user = h.getUserID(user)
        self.sharesPath = h.makeDirPath(os.path.abspath(sharesPath))
        if self.user is not None: h.changeFileOwner(self.sharesPath, self.user)

    ###################################################################################
    def listShares(self, filterID=None, maxShares=None):
        shares = []
        items = h.listDirectoryItems(self.sharesPath, onlyFiles=True)
        for item in items:
            shareID = os.path.basename(item)
            if filterID is not None and filterID.lower() not in shareID.lower(): continue
            shares.append(self.getShare(shareID, asAdmin=True)[0])
        shares = sorted(shares, key=lambda d: d.creation)[::-1]
        if maxShares is not None: return shares[0:min(maxShares, len(shares))]
        else: return shares

    ###################################################################################
    def addShare(self, shareID, path, duration, password):
        path = path.lstrip("/").rstrip("/")
        sharePath = h.makePath(self.sharesPath, shareID)
        password = "" if password is None else password
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % h.clean(shareID)), 5)
            s = share(shareID, h.now(), path, [], password, duration)
            h.writeJsonFile(sharePath, {"ID": s.ID, "file": s.file, "creation": s.creation, "views": s.views, "duration": s.duration, "password": s.password})
            if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return s, "ok"
        except:
            le, lt = h.getLastExceptionAndTrace()
            return None, le
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getShare(self, shareID, r=None, subPath=None, asAdmin=False):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): return None, None
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_share%s" % h.clean(shareID)), 5)
            shareJson = h.loadJsonFile(sharePath)
            s = share(shareJson["ID"], shareJson["creation"], shareJson["file"], shareJson.get("views", []), shareJson.get("password"), shareJson.get("duration", 0))
            if not asAdmin and s.duration > 0 and s.duration + s.creation < h.now(): return None, "Share has expired"
            if not asAdmin:
                views = s.views
                view = {"date": h.now()}
                if r is not None: view["ip"] = r.remote_addr
                if subPath is not None: view["item"] = h.makePath(s.file, subPath)
                views.append(view)
                views = sorted(views, key=lambda v: v["date"])[::-1]
                s.views = views
                h.writeJsonFile(sharePath, {"ID": s.ID, "file": s.file, "creation": s.creation, "views": s.views, "duration": s.duration, "password": s.password})
                if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return s, "ok"
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
