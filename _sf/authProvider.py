###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from flask import request


###################################################################################
class authProvider():

    ###################################################################################
    def __init__(self, basePath, adminPassword, forbiddenItems):
        self.basePath = os.path.abspath(basePath)
        self.adminPassword = adminPassword
        self.forbiddenItems = set(forbiddenItems)

    ###################################################################################
    def isAdmin(self, r: request):
        cookieKey = "_sf_admin_pass"
        if cookieKey in r.cookies: return r.cookies[cookieKey] == self.adminPassword
        else: return False

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
    def showForbidden(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".noshow"))

    ###################################################################################
    def downloadForbidden(self, path):
        return h.isfile(h.makePath(self.basePath, path, ".nodownload")) or self.showForbidden(path) or self.listingForbidden(path)

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
        if response is not None: response.set_cookie(cookieKey, password)

    ###################################################################################
    def setAdminPassword(self, password, r, response=None):
        cookieKey = "_sf_admin_pass"
        r.cookies = dict(r.cookies)
        r.cookies[cookieKey] = password
        if response is not None: response.set_cookie(cookieKey, password)

    ###################################################################################
    def removeAdminPassword(self, r, response=None):
        cookieKey = "_sf_admin_pass"
        r.cookies = dict(r.cookies)
        r.cookies.pop(cookieKey)
        if response is not None: response.set_cookie(cookieKey, "")

    ###################################################################################
    def isAuthorized(self, path, r: request):
        lowerProtectedPath = self.getLowerProtectedPath(path)
        if (lowerProtectedPath == False): return (False, "", "", True)
        requiredPasswords = h.readFromFile(h.makePath(self.basePath, lowerProtectedPath, ".password")).split("\n")
        requiredPasswords = [p for p in requiredPasswords if p != ""]
        savedPassword = self.getUserPassword(lowerProtectedPath, r)
        return (True, requiredPasswords, savedPassword, savedPassword in requiredPasswords)
