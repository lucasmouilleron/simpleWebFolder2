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
