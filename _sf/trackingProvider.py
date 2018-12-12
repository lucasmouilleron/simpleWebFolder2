###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from typing import List
import requests as rq
import json
import threading


###################################################################################
###################################################################################
###################################################################################
class tracking:
    def __init__(self, path, password, authorized, ip, date, protected, location=None):
        self.path = path
        self.password = password
        self.authorized = authorized
        self.ip = ip
        self.date = date
        self.protected = protected
        self.location = location
        if self.location is None: self.location = self.ip


###################################################################################
###################################################################################
###################################################################################
class trackingProvider():

    ###################################################################################
    def __init__(self, basePath, maxSize=3e6, user=None, locationEnabled=False, locationAPIKey=""):
        self.basePath = os.path.abspath(basePath)
        self.maxSize = maxSize
        self.user = h.getUserID(user)
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
    def _doTrack(self, path, address, isProtected, isAuthotirzed, passwordProvided):
        trackingFile = h.makePath(self.basePath, ".tracking")
        headers = ["path", "authorized", "password", "ip", "date", "protected", "location"]
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_tracking")
        try:
            lh = h.getLockExclusive(lf, 5)
            trackingFileSize = h.getFileSize(trackingFile)
            if trackingFileSize > self.maxSize:
                h.logInfo("Tracking file too big, splitting in 2", trackingFileSize, self.maxSize)
                datas = h.readCSV(trackingFile)
                nbLines = len(datas)
                offset = int(nbLines / 2)
                if offset > 0: h.writeToCSV(datas[offset:nbLines - offset], trackingFile, headers=headers, append=False)

            if self.locationEnabled: location = self._getLocationFromIP(address)
            else: location = address
            h.writeToCSV([[path, isAuthotirzed, passwordProvided if passwordProvided is not None else "", address, h.now(), isProtected, location]], trackingFile, headers=headers, append=True)
            if self.user is not None: h.changeFileOwner(trackingFile, self.user)

        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def track(self, path, r, isProtected, isAuthotirzed, passwordProvided):
        threading.Thread(target=self._doTrack, args=(path, r.remote_addr, isProtected, isAuthotirzed, passwordProvided)).start()

    ###################################################################################
    def getTrackings(self, password=None, item=None, protected=None, maxItems=None) -> List[tracking]:
        trackingFile = h.makePath(self.basePath, ".tracking")
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_tracking")
        try:
            lh = h.getLockShared(lf, 5)
            if not os.path.exists(trackingFile): return []
            datas = h.readCSV(trackingFile)
            trackings = []
            i = 0
            for d in datas[::-1]:
                if protected is not None:
                    tProtected = h.parseBool(d[5], False, trueValue="True")
                    if protected == "yes" and not tProtected: continue
                    if protected == "no" and tProtected: continue
                if password is not None and password.lower() not in d[2].lower(): continue
                if item is not None and item.lower() not in d[0].lower(): continue
                trackings.append(tracking(d[0], d[2], h.parseBool(d[1], False, trueValue="True"), d[3], h.parseInt(d[4], 0), h.parseBool(d[5], False, trueValue="True"), d[6]))
                i += 1
                if maxItems is not None and i > maxItems: break
            return trackings
        finally:
            if lh is not None: h.releaseLock(lh)
