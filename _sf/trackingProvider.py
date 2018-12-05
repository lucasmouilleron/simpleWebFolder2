###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h


###################################################################################
###################################################################################
###################################################################################
class trackingProvider():

    ###################################################################################
    def __init__(self, basePath, maxSize=3e6, user=None):
        self.basePath = os.path.abspath(basePath)
        self.maxSize = maxSize
        self.user = h.getUserID(user)

    ###################################################################################
    def track(self, path, r, isProtected, isAuthotirzed, passwordProvided):
        trackingFile = h.makePath(self.basePath, ".tracking")
        headers = ["path", "authorized", "password", "ip", "date", "protected"]
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sfl_tracking"), 5)
            trackingFileSize = h.getFileSize(trackingFile)
            if trackingFileSize > self.maxSize:
                h.logInfo("Tracking file too big, splitting in 2", trackingFileSize, self.maxSize)
                datas = h.readCSV(trackingFile)
                nbLines = len(datas)
                offset = int(nbLines / 2)
                if offset > 0: h.writeToCSV(datas[offset:nbLines - offset], trackingFile, headers=headers, append=False)

            h.writeToCSV([[path, isAuthotirzed, passwordProvided if passwordProvided is not None else "", r.remote_addr, h.now(), isProtected]], trackingFile, headers=headers, append=True)
            if self.user is not None: h.changeFileOwner(trackingFile, self.user)

        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getTrackings(self, password=None, item=None, protected=None, maxItems=None):
        trackingFile = h.makePath(self.basePath, ".tracking")
        lockFile = h.makePath(h.LOCKS_FOLDER, "_sfl_tracking")
        lh = None
        try:
            lh = h.getLockShared(lockFile, 5)
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
                trackings.append({"path": d[0], "authorized": d[1], "password": d[2], "ip": d[3], "date": h.parseInt(d[4], 0), "protected": d[5]})
                i += 1
                if maxItems is not None and i > maxItems: break
            return trackings
        finally:
            if lh is not None: h.releaseLock(lh)
