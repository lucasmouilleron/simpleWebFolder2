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
    def __init__(self, basePath, maxSize=3000):
        self.basePath = os.path.abspath(basePath)
        self.maxSize = maxSize

    ###################################################################################
    def track(self, path, r, isAuthotirzed, passwordProvided):
        trackingFile = h.makePath(self.basePath, ".tracking")
        lockFile = h.makePath(h.LOCKS_FOLDER, "_sfl_tracking")
        headers = ["path", "authorized", "password", "ip", "date"]
        lh = None
        try:
            lh = h.getLockExclusive(lockFile, 5)
            if h.getFileSize(trackingFile) > self.maxSize:
                datas = h.readCSV(trackingFile)
                nbLines = len(datas)
                offset = int(nbLines / 2)
                if offset > 0: h.writeToCSV(datas[offset:nbLines - offset], trackingFile, headers=headers, append=False)

            h.writeToCSV([[path, isAuthotirzed, passwordProvided, r.remote_addr, h.now()]], trackingFile, headers=headers, append=True)

        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getTrackings(self, password=None, item=None, maxItems=None):
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
                if password is not None and password not in d[2]: continue
                if item is not None and item not in d[0]: continue
                trackings.append({"path": d[0], "authorized": d[1], "password": d[2], "ip": d[3], "date": h.parseInt(d[4], 0)})
                i += 1
                if maxItems is not None and i > maxItems: break
            return trackings
        finally:
            if lh is not None: h.releaseLock(lh)
