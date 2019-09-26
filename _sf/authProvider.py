###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from flask import request
import sharesProvider as sp
from threading import Lock

###################################################################################
COOKIE_DURATION = 60 * 60 * 24 * 300


###################################################################################
class authProvider():

    ###################################################################################
    def __init__(self, basePath, adminPassword, forbiddenItems):
        self.basePath = os.path.abspath(basePath)
        self.adminPassword = adminPassword
        self.forbiddenItems = set(forbiddenItems)
        self.passwordsCache = {}
        self.passwordsLock = Lock()

    ###################################################################################
    def isAdmin(self, r: request):
        return r.cookies.get("_sf_admin_pass", "_not_set") == self.adminPassword

    ###################################################################################
    def isEditAllowed(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".editallowed"))

    ###################################################################################
    def setEditAllowed(self, path):
        path = h.cleanPath(path)
        h.writeToFile(h.makePath(self.basePath, path, ".editallowed"), "")

    ###################################################################################
    def isForbidden(self, path):
        path = h.cleanPath(path)
        if path.startswith("_sf"): return True
        if os.path.basename(path) in self.forbiddenItems: return True
        return False

    ###################################################################################
    def passwordProtected(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".password"))

    ###################################################################################
    def listingForbidden(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".nolist"))

    ###################################################################################
    def setListingForbidden(self, path):
        path = h.cleanPath(path)
        h.writeToFile(h.makePath(self.basePath, path, ".nolist"), "")

    ###################################################################################
    def showForbidden(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".noshow"))

    ###################################################################################
    def setShowForbidden(self, path):
        path = h.cleanPath(path)
        h.writeToFile(h.makePath(self.basePath, path, ".noshow"), "")

    ###################################################################################
    def downloadForbidden(self, path):
        path = h.cleanPath(path)
        if path == "": return True
        return h.isfile(h.makePath(self.basePath, path, ".nodownload")) or self.showForbidden(path) or self.listingForbidden(path)

    ###################################################################################
    def setDownloadForbidden(self, path):
        path = h.cleanPath(path)
        h.writeToFile(h.makePath(self.basePath, path, ".nodownload"), "")

    ###################################################################################
    def shareForbidden(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".noshare"))

    ###################################################################################
    def passwordEditForbidden(self, path):
        path = h.cleanPath(path)
        return h.isfile(h.makePath(self.basePath, path, ".nopasswordedit"))

    ###################################################################################
    def setShareForbidden(self, path):
        path = h.cleanPath(path)
        h.writeToFile(h.makePath(self.basePath, path, ".noshare"), "")

    ###################################################################################
    def getLowerProtectedPath(self, path):
        path = h.cleanPath(path)
        relativePath = path
        lowerPath = False
        paths = relativePath.split("/")
        for i in range(len(paths)):
            currentPath = h.makePath(*paths[0:len(paths) - i])
            if currentPath == "": currentPath = "/"
            currentRealPath = os.path.abspath(h.makePath(self.basePath, currentPath))
            if os.path.isfile(h.makePath(currentRealPath, ".password")):
                lowerPath = currentRealPath
                break
            if os.path.isfile(h.makePath(currentRealPath, ".nopassword")):
                lowerPath = False
                break
        if lowerPath == False: return False
        return h.cleanPath(lowerPath.replace(self.basePath, ""))

    ###################################################################################
    def addNewPassword(self, path, password):
        path = h.cleanPath(path)
        if password is None: return False
        if self.passwordEditForbidden(path): return False
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_password_%s" % h.clean(path))
        try:
            passwordFile = h.makePath(self.basePath, path, ".password")
            requiredPasswords = list(self.getPasswords(path))
            requiredPasswords.append(password)
            lh = h.getLockExclusive(lf, 5)
            h.writeToFile(passwordFile, "\n".join(list(set(requiredPasswords))))
            return True
        except:
            print(h.getLastExceptionAndTrace())
            return False
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getUserPassword(self, path, r: request):
        path = h.cleanPath(path)
        path = h.clean(path if path != "" else "-")
        cookieKey = "_sf_pass_%s" % path
        if cookieKey in r.cookies: return r.cookies[cookieKey]
        else: return None

    ###################################################################################
    def setUserPassword(self, path, password, r, response=None):
        path = h.cleanPath(path)
        cookieKey = "_sf_pass_%s" % h.clean(path if path != "" else "-")
        r.cookies = dict(r.cookies)
        r.cookies[cookieKey] = password
        if response is not None: response.set_cookie(cookieKey, password, max_age=COOKIE_DURATION)

    ###################################################################################
    def setAdminPassword(self, password, r, response=None):
        cookieKey = "_sf_admin_pass"
        r.cookies = dict(r.cookies)
        r.cookies[cookieKey] = password
        if response is not None: response.set_cookie(cookieKey, password, max_age=COOKIE_DURATION)

    ###################################################################################
    def removeAdminPassword(self, r, response=None):
        cookieKey = "_sf_admin_pass"
        r.cookies = dict(r.cookies)
        r.cookies.pop(cookieKey)
        if response is not None: response.set_cookie(cookieKey, "", max_age=COOKIE_DURATION)

    ###################################################################################
    def getPasswords(self, path):
        path = h.cleanPath(path)
        passwordsFile = h.makePath(self.basePath, path, ".password")
        if not os.path.exists(passwordsFile): return set()
        passwordsCacheKey = h.makeKeyFromArguments(path)
        lh, lf = None, h.makePath(h.LOCKS_FOLDER, "_sfl_password_%s" % h.clean(path))
        try:
            self.passwordsLock.acquire()
            if passwordsCacheKey in self.passwordsCache:
                pc = self.passwordsCache[passwordsCacheKey]
                if h.getFileModified(passwordsFile) == pc["date"]:
                    return pc["passwords"]

            lh = h.getLockShared(lf, 5)
            passwords = set([p for p in h.readFromFile(h.makePath(self.basePath, path, ".password")).split("\n") if p != ""])
            self.passwordsCache[passwordsCacheKey] = {"passwords": passwords, "date": h.getFileModified(passwordsFile)}
            return passwords
        finally:
            self.passwordsLock.release()
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def isAuthorized(self, path, r: request):
        lowerProtectedPath = self.getLowerProtectedPath(path)
        if (lowerProtectedPath == False): return (False, [], "", True, False, False)
        protectedFromParent = path != lowerProtectedPath
        requiredPasswords = self.getPasswords(lowerProtectedPath)
        savedPassword = self.getUserPassword(lowerProtectedPath, r)
        return (True, sorted(requiredPasswords), savedPassword, savedPassword in requiredPasswords, lowerProtectedPath, protectedFromParent)

    ###################################################################################
    def isShareProtected(self, s: sp.share):
        return s.password != ""

    ###################################################################################
    def isShareAuthorized(self, s: sp.share, r: request):
        savedPassword = r.cookies.get("_sf_share_pass_%s" % s.ID, None)
        if s.password == "": return True, savedPassword
        else: return s.password == savedPassword, savedPassword

    ###################################################################################
    def setSharePassword(self, shareID, password, r, response=None):
        cookieKey = "_sf_share_pass_%s" % shareID
        r.cookies = dict(r.cookies)
        r.cookies[cookieKey] = password
        if response is not None: response.set_cookie(cookieKey, password, max_age=COOKIE_DURATION)
