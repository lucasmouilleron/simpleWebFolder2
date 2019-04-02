###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
import requests as rq
import json
import threading


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
    def __init__(self, sharesPath, user=None, locationEnabled=False, locationAPIKey=""):
        self.user = h.getUserID(user)
        self.sharesPath = h.makeDirPath(os.path.abspath(sharesPath))
        if self.user is not None: h.changeFileOwner(self.sharesPath, self.user)
        self.locationEnabled = locationEnabled
        self.locationAPIKey = locationAPIKey

    ###################################################################################
    def _getLocationFromIP(self, ip):
        try:
            if ip in h.IP_LOCATIONS_DONE: return h.IP_LOCATIONS_DONE[ip]
            apiURL = "http://api.ipapi.com/%s?access_key=%s" % (ip, self.locationAPIKey)
            result = rq.get(apiURL, timeout=3)
            result.encoding = "utf8"
            result = json.loads(result.text)
            country, region = result["country_code"], result["region_code"]
            if country is None: location = ip
            else: location = "%s, %s" % (country, region)
            h.IP_LOCATIONS_DONE[ip] = location
            return location
        except: return ip

    ###################################################################################
    def _doAddView(self, s: share, subPath, address, tag):
        views = s.views
        view = {"date": h.now()}
        if address is not None:
            view["ip"] = address
            view["location"] = self._getLocationFromIP(address)
        else:
            view["ip"] = "unk"
            view["location"] = "unk"
        if tag is not None: view["tag"] = tag
        if subPath is not None: view["item"] = h.makePath(s.file, subPath).rstrip("/")
        views.append(view)
        views = sorted(views, key=lambda v: v["date"])[::-1]
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
    def addShare(self, shareID, path, duration, password):
        path = path.lstrip("/").rstrip("/")
        sharePath = h.makePath(self.sharesPath, shareID)
        password = "" if password is None else password
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(shareID))
        try:
            lh = h.getLockExclusive(lf, 5)
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
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(shareID))
        try:
            lh = h.getLockShared(lf, 5)
            shareJson = h.loadJsonFile(sharePath)
            s = share(shareJson["ID"], shareJson["creation"], shareJson["file"], shareJson.get("views", []), shareJson.get("password"), shareJson.get("duration", 0))
            if not asAdmin and s.duration > 0 and s.duration + s.creation < h.now(): rs, rh = None, "Share has expired"
            else: rs, rh = s, "ok"
            h.releaseLock(lh)
            lh = None
            tag = None
            if r is not None: tag = h.getURLParams(r.url).get("t", None)
            if not asAdmin: self.addView(s, subPath, r.remote_addr if r is not None else None, tag)
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
    def addView(self, s: share, subpath, address, tag):
        threading.Thread(target=self._doAddView, args=(s, subpath, address, tag)).start()

    ###################################################################################
    def saveShare(self, s: share):
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_share%s" % h.clean(s.ID))
        try:
            lh = h.getLockExclusive(lf, 5)
            sharePath = h.makePath(self.sharesPath, s.ID)
            h.writeJsonFile(sharePath, {"ID": s.ID, "file": s.file, "creation": s.creation, "views": s.views, "duration": s.duration, "password": s.password})
            if self.user is not None: h.changeFileOwner(sharePath, self.user)
            return True
        except:
            le, lt = h.getLastExceptionAndTrace()
            return False
        finally:
            if lh is not None: h.releaseLock(lh)
