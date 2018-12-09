###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from flask import request
import sharesProvider as sp

###################################################################################
COOKIE_DURATION = 60 * 60 * 24 * 300


###################################################################################
class authProvider():

    ###################################################################################
    def __init__(self, basePath, adminPassword, forbiddenItems):
        self.basePath = os.path.abspath(basePath)
        self.adminPassword = adminPassword
        self.forbiddenItems = set(forbiddenItems)

    ###################################################################################
    def isAdmin(self, r: request):
        return r.cookies.get("_sf_admin_pass", "_not_set") == self.adminPassword

    ###################################################################################
    def isAddAllowed(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".addallowed"))

    ###################################################################################
    def setAddAllowed(self, path):
        h.writeToFile(h.makePath(self.basePath, path, ".addallowed"), "")

    ###################################################################################
    def isForbidden(self, path):
        path = path.lstrip("/")
        if path.startswith("_sf"): return True
        if os.path.basename(path) in self.forbiddenItems: return True
        return False

    ###################################################################################
    def passwordProtected(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".password"))

    ###################################################################################
    def listingForbidden(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".nolist"))

    ###################################################################################
    def setListingForbidden(self, path):
        h.writeToFile(h.makePath(self.basePath, path, ".nolist"), "")

    ###################################################################################
    def showForbidden(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".noshow"))

    ###################################################################################
    def setShowForbidden(self, path):
        h.writeToFile(h.makePath(self.basePath, path, ".noshow"), "")

    ###################################################################################
    def downloadForbidden(self, path):
        if path == "": return True
        return h.isfile(h.makePath(self.basePath, path, ".nodownload")) or self.showForbidden(path) or self.listingForbidden(path)

    ###################################################################################
    def setDownloadForbidden(self, path):
        h.writeToFile(h.makePath(self.basePath, path, ".nodownload"), "")

    ###################################################################################
    def shareForbidden(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".noshare"))

    ###################################################################################
    def setShareForbidden(self, path):
        h.writeToFile(h.makePath(self.basePath, path, ".noshare"), "")

    ###################################################################################
    def getLowerProtectedPath(self, path):
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
        return lowerPath.replace(self.basePath, "")

    ###################################################################################
    def addNewPassword(self, path, password):
        if password is None: return False
        lh = None
        try:
            lh = h.getLockExclusive(h.makePath(h.LOCKS_FOLDER, "_sf_password_%s" % h.clean(path)), 5)
            passwordFile = h.makePath(self.basePath, path, ".password")
            if os.path.exists(passwordFile): requiredPasswords = [p for p in h.readFromFile(passwordFile).split("\n") if p != ""]
            else: requiredPasswords = []
            requiredPasswords.append(password)
            h.writeToFile(passwordFile, "\n".join(list(set(requiredPasswords))))
            return True
        except: return False
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def getUserPassword(self, path, r: request):
        path = h.clean(path if path != "" else "-")
        cookieKey = "_sf_pass_%s" % path
        if cookieKey in r.cookies: return r.cookies[cookieKey]
        else: return None

    ###################################################################################
    def setUserPassword(self, path, password, r, response=None):
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
    def isAuthorized(self, path, r: request):
        lowerProtectedPath = self.getLowerProtectedPath(path)
        if (lowerProtectedPath == False): return (False, [], "", True, False)
        lh = None
        try:
            lh = h.getLockShared(h.makePath(h.LOCKS_FOLDER, "_sf_password_%s" % h.clean(path)), 5)
            requiredPasswords = sorted([p for p in h.readFromFile(h.makePath(self.basePath, lowerProtectedPath, ".password")).split("\n") if p != ""])
            savedPassword = self.getUserPassword(lowerProtectedPath, r)
            return (True, requiredPasswords, savedPassword, savedPassword in requiredPasswords, lowerProtectedPath)
        finally:
            if lh is not None: h.releaseLock(lh)

    ###################################################################################
    def isShareAuthorized(self, s: sp.share, r: request):
        return s.password == r.cookies.get("_sf_share_pass_%s" % s.ID, "_no_set")

    ###################################################################################
    def setSharePassword(self, shareID, password, r, response=None):
        cookieKey = "_sf_share_pass_%s" % shareID
        r.cookies = dict(r.cookies)
        r.cookies[cookieKey] = password
        if response is not None: response.set_cookie(cookieKey, password, max_age=COOKIE_DURATION)
