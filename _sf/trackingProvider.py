###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from typing import List
import requests as rq
import json
import threading
from threading import Thread, Lock


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
    def __init__(self, basePath, maxSize=5e5, user=None, locationEnabled=False, locationAPIKey=""):
        self.basePath = os.path.abspath(basePath)
        self.maxSize = maxSize
        self.user = h.getUserID(user)
        self.locationEnabled = locationEnabled
        self.locationAPIKey = locationAPIKey
        self.trackings = []  # type: List[tracking]
        self.trackingsSaved = True
        self.trackingsLock = Lock()
        self.saveTrackingsThread = SaveTrackings(self, 500)

        self._loadTrackings()
        self.saveTrackingsThread.start()

    ###################################################################################
    def stop(self):
        self._saveTrackings()
        if self.saveTrackingsThread is not None: self.saveTrackingsThread.interrupt()

    ###################################################################################
    def _loadTrackings(self):
        try:
            self.trackingsLock.acquire()
            trackingFile = h.makePath(self.basePath, ".tracking")
            datas = h.readCSV(trackingFile)
            for d in datas: self.trackings.append(tracking(d[0], d[2], h.parseBool(d[1], False, trueValue="True"), d[3], h.parseInt(d[4], 0), h.parseBool(d[5], False, trueValue="True"), d[6]))
            h.logDebug("Trackings loaded from file", trackingFile, len(self.trackings))
        except:
            le, lt = h.getLastExceptionAndTrace()
            h.logWarning("Can't load trackings", le)
        finally: self.trackingsLock.release()

    ###################################################################################
    def _saveTrackings(self):
        if self.trackingsSaved: return
        try:
            self.trackingsLock.acquire()
            trackingFile = h.makePath(self.basePath, ".tracking")
            tmpTrackingFile = h.makePath(self.basePath, ".tracking.tmp")
            h.logDebug("Saving trackings saved to file", len(self.trackings), trackingFile)
            headers, datas = ["path", "authorized", "password", "ip", "date", "protected", "location"], []
            for t in self.trackings: datas.append([t.path, t.authorized, t.password, t.ip, t.date, t.protected, t.location])
            h.writeToCSV(datas, tmpTrackingFile, headers=headers, append=True)
            h.delete(trackingFile)
            os.rename(tmpTrackingFile, trackingFile)
            if self.user is not None: h.changeFileOwner(trackingFile, self.user)
            self.trackingsSaved = True
            h.logDebug("Trackings saved to file", len(self.trackings), trackingFile)
        except:
            le, lt = h.getLastExceptionAndTrace()
            h.logWarning("Can't save trackings", le)
        finally: self.trackingsLock.release()

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
    def _doTrack(self, path, address, isProtected, isAuthotirzed, passwordProvided, shareID, shareTag):
        try:
            self.trackingsLock.acquire()
            path = h.cleanPath(path)
            if shareID is not None: path = "%s - sid: %s" % (path, shareID)
            if shareTag is not None: path = "%s - stag: %s" % (path, shareTag)
            if self.locationEnabled: location = self._getLocationFromIP(address)
            else: location = address
            self.trackings.append(tracking(path, passwordProvided if passwordProvided is not None else "", isAuthotirzed, address, h.now(), isProtected, location))
            if len(self.trackings) > self.maxSize:
                nbLines = len(self.trackings)
                offset = int(nbLines - self.maxSize / 2)
                if offset > 0: self.trackings = self.trackings[offset:nbLines]
                h.logDebug("Trimed trackings", nbLines, len(self.trackings))
            self.trackingsSaved = False
        finally: self.trackingsLock.release()

    ###################################################################################
    def track(self, path, r, isProtected, isAuthotirzed, passwordProvided, shareID=None, shareTag=None):
        threading.Thread(target=self._doTrack, args=(path, r.remote_addr, isProtected, isAuthotirzed, passwordProvided, shareID, shareTag)).start()

    ###################################################################################
    def getTrackings(self, password=None, item=None, protected=None, maxItems=None) -> List[tracking]:
        try:
            self.trackingsLock.acquire()
            finalTrackings = []
            i = 0
            for t in self.trackings[::-1]:
                if protected is not None:
                    if protected == "yes" and not t.protected: continue
                    if protected == "no" and t.protected: continue
                if password is not None and password.lower() not in t.password.lower(): continue
                if item is not None and item.lower() not in t.path.lower(): continue
                finalTrackings.append(t)
                i += 1
                if maxItems is not None and i >= maxItems: break
            return finalTrackings
        finally: self.trackingsLock.release()


###################################################################################
###################################################################################
###################################################################################
class SaveTrackings(Thread):

    ###################################################################################
    def __init__(self, tp: trackingProvider, frequencyInSecs):
        Thread.__init__(self)
        self._interrupt = False
        self._exitEvent = threading.Event()
        self.frequency = frequencyInSecs
        self.tp = tp

    ###################################################################################
    def run(self):
        while not self._interrupt and not self._exitEvent.isSet():
            try: self.tp._saveTrackings()
            except: print(h.getLastExceptionAndTrace())
            finally: self._exitEvent.wait(self.frequency)
        h.logDebug("SaveTracking thread finished")

    ###################################################################################
    def interrupt(self):
        self._interrupt = True
        self._exitEvent.set()
