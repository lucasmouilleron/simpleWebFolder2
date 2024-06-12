###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import json
import threading

###################################################################################
###################################################################################
###################################################################################
class share:
    def __init__(self, ID, creation, files, views, password, duration, tag=None):
        self.ID = ID
        self.creation = creation
        self.files = files
        self.views = views
        self.password = password
        self.duration = duration
        self.tag = tag

###################################################################################
###################################################################################
###################################################################################
class sharesProvider:

    ###################################################################################
    def __init__(self, sharesPath, user=None, locationEnabled=False, locationAPIKey="", viewsEnabled=True, maxViews=2000):
        self.user = h.getUserID(user)
        self.sharesPath = h.makeDirPath(os.path.abspath(sharesPath))
        if self.user is not None: h.changeFileOwner(self.sharesPath, self.user)
        self.locationEnabled = locationEnabled
        self.locationAPIKey = locationAPIKey
        self.viewsEnabled = viewsEnabled
        self.maxViews = maxViews

    ###################################################################################
    def _doAddView(self, s: share, subPath, baseFile, address, tag, isAuthorized):
        views = s.views
        view = {"date": h.now()}
        if address is not None:
            view["ip"] = address
            view["location"] = h.getLocationFromIP(address, self.locationAPIKey) if self.locationEnabled else address
        else:
            view["ip"] = "unk"
            view["location"] = "unk"
        if tag is not None: view["tag"] = tag
        if subPath is not None: view["item"] = h.makePath(baseFile if baseFile is not None else "", subPath).rstrip("/")
        view["authorized"] = isAuthorized
        views.append(view)
        views = sorted(views, key=lambda v: v["date"])[::-1]
        if len(views) > self.maxViews:
            nbLines = len(views)
            offset = int(nbLines - self.maxViews / 2)
            if offset > 0: views = views[offset:nbLines]
            h.logDebug("Trimed views", s.ID, nbLines, len(views))
        s.views = views
        self.saveShare(s)

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
    def addShare(self, shareID, paths, duration, password):
        paths = [path.lstrip("/").rstrip("/") for path in paths]
        sharePath = h.makePath(self.sharesPath, shareID)
        password = "" if password is None else password
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(shareID))
        try:
            lh = h.getLockExclusive(lf, 5)
            s = share(shareID, h.now(), paths, [], password, duration)
            h.writeJsonFile(sharePath, {"ID": s.ID, "files": s.files, "creation": s.creation, "views": s.views, "duration": s.duration, "password": s.password})
            if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return s, "ok"
        except:
            le, lt = h.getLastExceptionAndTrace()
            return None, le
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getShare(self, shareID, r=None, asAdmin=False):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): return None, None
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(shareID))
        try:
            lh = h.getLockShared(lf, 5)
            shareJson = h.loadJsonFile(sharePath)
            files = shareJson.get("files", None)
            if files is None:
                files = shareJson.get("file", None)
                if files is not None: files = [files]
            s = share(shareJson["ID"], shareJson["creation"], files, shareJson.get("views", []), shareJson.get("password"), shareJson.get("duration", 0))
            if not asAdmin and s.duration > 0 and s.duration + s.creation < h.now(): rs, rh = None, "Share has expired"
            else: rs, rh = s, "ok"
            if rs is None: return rs, rh
            if r is not None: rs.tag = h.getURLParams(r.url).get("t", None)
            return rs, rh
        except:
            le, lt = h.getLastExceptionAndTrace()
            return None, le
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def removeShare(self, shareID):
        sharePath = h.makePath(self.sharesPath, shareID)
        if not os.path.exists(sharePath): raise Exception("Unknown share", shareID)
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(shareID))
        try:
            lh = h.getLockExclusive(lf, 5)
            os.remove(sharePath)
            return True
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def shareExists(self, shareID):
        return os.path.exists(h.makePath(self.sharesPath, shareID))

    ###################################################################################
    def addView(self, s: share, subpath, baseFile, address, tag, isAuthorized):
        if not self.viewsEnabled: return
        self._doAddView(s, subpath, baseFile, address, tag, isAuthorized)
        # threading.Thread(target=self._doAddView, args=(s, subpath, baseFile, address, tag, isAuthorized)).start()

    ###################################################################################
    def saveShare(self, s: share):
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(s.ID))
        try:
            lh = h.getLockExclusive(lf, 5)
            sharePath = h.makePath(self.sharesPath, s.ID)
            h.writeJsonFile(sharePath, {"ID": s.ID, "files": s.files, "creation": s.creation, "views": s.views, "duration": s.duration, "password": s.password})
            if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return True
        except:
            le, lt = h.getLastExceptionAndTrace()
            return False
        finally:
            if lh is not None: h.releaseLock(lh)
