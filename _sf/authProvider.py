###################################################################################
# IMPORTS
###################################################################################
import os
import helper as h
from flask import request


###################################################################################
class authProvider():

    ###################################################################################
    def __init__(self, basePath):
        self.basePath = os.path.abspath(basePath)

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
        cookieKey = "_sf_pas_%s" % path
        if cookieKey in r.cookies: return True
        else: return None

    ###################################################################################
    def isAuthorized(self, path, r: request):
        lowerProtectedPath = self.getLowerProtectedPath(path)
        if (lowerProtectedPath == False): return (False, "", "", True)
        requiredPasswords = h.readFromFile(h.makePath(self.basePath, lowerProtectedPath, ".password")).split("\n")
        savedPassword = self.getUserPassword(lowerProtectedPath, r)
        return (True, requiredPasswords, savedPassword, savedPassword in requiredPasswords)
