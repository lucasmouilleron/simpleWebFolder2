###################################################################################
# IMPORTS
###################################################################################
import signal
from threading import Thread
from gevent.wsgi import WSGIServer
from flask import Flask, request, jsonify, send_from_directory, redirect, make_response, send_file, url_for, Response
from flask_cors import CORS
from mako.template import Template
from mako.lookup import TemplateLookup
import helper as h
import itemsProvider as ip
import authProvider as ap
import trackingProvider as tp
import sharesProvider as sp
import os
import time


###################################################################################
###################################################################################
###################################################################################
class Server(Thread):

    ###################################################################################
    def __init__(self, ip: ip.itemsProvider, ap: ap.authProvider, sp: sp.sharesProvider, port, ssl=False, certificateKeyFile=None, certificateCrtFile=None, fullchainCrtFile="", aliases=None, maxUploadSize=None):
        Thread.__init__(self)
        self.app = Flask(__name__)
        self.ip = ip
        self.ap = ap
        self.sp = sp
        self.port = port
        self.ssl = ssl
        self.certificateKeyFile = certificateKeyFile
        self.certificateCrtFile = certificateCrtFile
        self.fullchainCrtFile = fullchainCrtFile
        self.httpServer = None
        self.aliases = aliases
        self.maxUploadSize = maxUploadSize

        if self.maxUploadSize is not None: self.app.config["MAX_CONTENT_LENGTH"] = self.maxUploadSize

        self._addRoute("/hello", self._routeHello, ["GET"])
        self._addRouteRaw("/", self._routeItems, ["GET", "POST"], "index")
        self._addRouteRaw("/<path:path>", self._routeItems, ["GET", "POST"], noCache=True)
        self._addRouteRaw("/_sf_assets/<path:path>", self._routeAssets, ["GET"])
        self._addRouteRaw("/admin", self._routeAdmin, ["GET", "POST"])
        self._addRouteRaw("/noadmin", self._routeNoAdmin, ["GET"])
        self._addRouteRaw("/tracking", self._routeTrackingAdmin, ["GET", "POST"])
        self._addRouteRaw("/share=<path:shareIDAndPath>", self._routeShare, ["GET", "POST"])
        self._addRouteRaw("/shares", self._routeShares, ["GET", "POST"])
        self._addRouteRaw("/remove-share=<shareID>", self._routeShareRemove, ["GET"])
        self._addRouteRaw("/create-share=<path>", self._routeShareAdd, ["GET", "POST"])

        self.tplLookup = TemplateLookup(directories=[h.makePath(h.ROOT_FOLDER, "templates")])

    ###################################################################################
    def run(self):
        CORS(self.app)
        if self.ssl: self.httpServer = WSGIServer(("0.0.0.0", self.port), self.app, log=None, keyfile=self.certificateKeyFile, certfile=self.certificateCrtFile, ca_certs=self.fullchainCrtFile)
        else: self.httpServer = WSGIServer(("0.0.0.0", self.port), self.app, log=None)
        self.httpServer.serve_forever()

    ###################################################################################
    def stop(self):
        self.httpServer.stop()

    ###################################################################################
    def _noCache(self, r=None):
        if r is None: r = make_response()
        if r is not None and type(r) != Response: r = make_response(r)
        headers = dict(r.headers)
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        headers["Pragma"] = "no-cache"
        headers["Expires"] = "0"
        headers["Cache-Control"] = "public, max-age=0"
        r.headers = headers
        return r

    ###################################################################################
    def _addRoute(self, rule, callback, methods=["GET"], endpoint=None, noCache=True):
        def callbackReal(*args, **kwargs):
            try:
                r = jsonify(callback(*args, **kwargs))
                if noCache: r = self._noCache(r)
                return r
            except Exception as e:
                h.logWarning("Error processing request", request.data.decode("utf-8"), request.endpoint, h.formatException(e))
                return jsonify({"result": 500, "hint": h.formatException(e)})

        if endpoint is None: endpoint = h.uniqueID()
        self.app.add_url_rule(rule, endpoint, callbackReal, methods=methods)

    ###################################################################################
    def _addRouteRaw(self, rule, callback, methods, endpoint=None, noCache=False):
        def callbackReal(*args, **kwargs):
            try:
                r = callback(*args, **kwargs)
                if noCache: r = self._noCache(r)
                return r
            except Exception as e:
                le, lt = h.getLastExceptionAndTrace()
                print(le)
                print(lt)
                h.logWarning("Error processing request", request.data.decode("utf-8"), request.endpoint, h.formatException(e))
                return Template(filename=h.makePath(h.ROOT_FOLDER, "templates", "error.mako"), lookup=self.tplLookup).render(e=e, **self._makeBaseNamspace(), le=le, lt=lt)

        if endpoint is None: endpoint = h.uniqueID()
        self.app.add_url_rule(rule, endpoint, callbackReal, methods=methods)

    ###################################################################################
    def _routeHello(self):
        return {"result": 200, "world": h.now(), "version": h.dictionnaryDeepGet(h.CONFIG, "version", default=0)}

    ###################################################################################
    def _routeAssets(self, path):
        return send_from_directory(h.makePath(h.ROOT_FOLDER, "assets"), path)

    ###################################################################################
    def _routeItems(self, path="/"):
        path = self._aliasPath(path.rstrip("/"))

        if self.ap.isAdmin(request): return self._routeAdmin(path)

        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)

        isProtected, requiredPasswords, savedPassword, isAuthorized, lowerProtectedPath = ap.isAuthorized(path, request)

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setUserPassword(lowerProtectedPath, request.form.get("password", ""), request, response)
            return self._redirect(path, response)

        if h.TRACKING: tp.track(path, request, isProtected, isAuthorized, savedPassword)
        if isAuthorized:
            if ip.isItemLeaf(path):
                if self.ap.isForbidden(path): return self._makeTemplate("forbidden", path=path)
                return send_from_directory(h.DATA_FOLDER, path)
            else:
                if self.ap.isForbidden(path): return self._makeTemplate("forbidden", path=path)
                if self.ap.listingForbidden(path): return self._makeTemplate("forbidden", path=path)
                if "download" in request.args and not self.ap.downloadForbidden(path): return self._downloadAndDeleteFile(ip.getZipFile(path, request), "%s.zip" % (os.path.basename(path) if path != "" else "root"))
                alerts = []
                containers, leafs = ip.getItems(path, request)
                readme = ip.getReadme(path)
                return self._makeTemplate("items", containers=containers, leafs=leafs, path=path, readme=readme, downloadAllowed=not self.ap.downloadForbidden(path), currentURLWithoutURI=path, alerts=alerts)
        else: return self._makeTemplate("password", path=path, lowerProtectedPath=lowerProtectedPath)

    ###################################################################################
    def _routeNoAdmin(self):
        response = make_response()
        self.ap.removeAdminPassword(request, response)
        return self._redirect("/", response)

    ###################################################################################
    def _routeAdmin(self, path="/"):
        path = path.rstrip("/")

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setAdminPassword(request.form.get("password", ""), request, response)
            return self._redirect("/admin", response)

        if not self.ap.isAdmin(request): return self._makeTemplate("password-admin")

        return self._routeItemsAdmin(path)

    ###################################################################################
    def _routeItemsAdmin(self, path):
        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)
        if ip.isItemLeaf(path): return send_from_directory(h.DATA_FOLDER, path)
        addAllowed = self.ap.isAddAllowed(path)
        alerts = []
        if request.form.get("add-password-submit", False):
            passwordToAdd = request.form.get("new-password", None)
            if self.ap.addNewPassword(path, passwordToAdd): alerts.append(["Password added", "The password %s has been added." % passwordToAdd])
            else: alerts.append(["Can't add password", "The password %s could not be added." % passwordToAdd])
        if request.form.get("add-leaf", False):
            if not addAllowed: return self._makeTemplate("forbidden", path=path)
            file = request.files["file"]
            result, hint = self.ip.addLead(path, file)
            if not result: alerts.append(["Can't add file", "The file can't be added: %s." % hint])
            else: alerts.append(["File added", "The file %s has been added." % hint])

        isProtected, requiredPasswords, _, _, _ = self.ap.isAuthorized(path, request)
        containers, leafs = ip.getItems(path, request, asAdmin=True)
        isTmpFolder = self.ip.tmpFolder == path
        readme = ip.getReadme(path)
        subAlerts = []
        if isProtected and len(requiredPasswords) > 1: subAlerts.append("Password protected, see passwords below.")
        if isProtected and len(requiredPasswords) == 1: subAlerts.append("Password protected: %s" % requiredPasswords[0])
        if isTmpFolder: subAlerts.append("Tmp folder.")
        if addAllowed: subAlerts.append("Upload allowed.")
        if self.ap.listingForbidden(path): subAlerts.append("Listing not allowed for non admin users.")
        if self.ap.showForbidden(path): subAlerts.append("Folder not shown for non admin users.")
        if self.ap.shareForbidden(path): subAlerts.append("Folder cannot be shared with Sares.")
        if self.ap.downloadForbidden(path) and path != "": subAlerts.append("Folder not downloadable.")
        if len(subAlerts) > 0: alerts.append(["Special folder", "<br/>".join(subAlerts)])
        response = make_response(self._makeTemplate("items-admin", isProtected=isProtected, passwords=sorted(requiredPasswords), containers=containers, leafs=leafs, path=path, readme=readme, alerts=alerts, addAllowed=addAllowed, isTmpFolder=isTmpFolder))
        return response

    ###################################################################################
    def _routeTrackingAdmin(self):
        if not h.TRACKING: return self._redirect("/admin")
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        maxItems, password, item, protected = request.form.get("maxItems", "500"), request.form.get("password", ""), request.form.get("item", ""), request.form.get("protected", "yes")
        return self._makeTemplate("tracking", trackings=tp.getTrackings(password if password != "" else None, item if item != "" else None, protected, h.parseInt(maxItems, None)), password=password, item=item, maxItems=maxItems, protected=protected)

    ###################################################################################
    def _routeShares(self, alerts=None):
        if alerts is None: alerts = []
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        maxShares = 50
        filterShareID = request.form.get("filterShareID", "")
        return self._makeTemplate("shares-admin", shares=self.sp.listShares(filterShareID, maxShares=maxShares), alerts=alerts, maxShares=maxShares, filterShareID=filterShareID)

    ###################################################################################
    def _routeShareRemove(self, shareID):
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        self.sp.removeShare(shareID)
        return self._routeShares(alerts=[["Share removed", "The Share %s has been removed." % shareID]])

    ###################################################################################
    def _routeShareAdd(self, path):
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        if self.ap.shareForbidden(path): return self._makeTemplate("forbidden", path=path)
        alerts = []
        path = h.decode(path)
        shareID = request.form.get("shareID", "")
        defaultShareID = request.form.get("defaultShareID", h.uniqueIDSmall())
        duration = request.form.get("duration", "")
        durationInSecs = h.parseInt(duration, 0) * 24 * 60 * 60
        password = request.form.get("password", "")
        shareSubmit = request.form.get("create-share-submit", False)
        shareForceSubmit = request.form.get("create-share-force-submit", False)
        needForce = False
        addShareIsContainer = self.ip.isItemContainer(path)
        if shareSubmit or shareForceSubmit:
            if shareID == "": shareID = defaultShareID
            shareID = h.clean(shareID)
            if shareID == "": alerts.append(["Can't create Share", "Share ID provided is invalid."])
            else:
                if not sp.shareExists(shareID) or shareForceSubmit:
                    share, hint = self.sp.addShare(shareID, path, durationInSecs, password)
                    if share is not None:
                        alerts.append(["Share created", "The Share %s has been created for %s" % (shareID, path)])
                        return self._routeShares(alerts)
                    else: alerts.append(["Can't create Share", "Share %s could not be created. Hint: %s" % (shareID, hint)])
                else:
                    alerts.append(["Can't create Share", "The Share ID %s is alread used for %s." % (shareID, path)])
                    needForce = True
        return self._makeTemplate("share-add", path=path, defaultShareID=defaultShareID, shareID=shareID, duration=duration, alerts=alerts, needForce=needForce, addShareIsContainer=addShareIsContainer)

    ###################################################################################
    def _routeShare(self, shareIDAndPath):
        shareID = shareIDAndPath.split("/")[0]
        if not self.sp.shareExists(shareID): return self._makeTemplate("not-found", path=shareID)

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setSharePassword(shareID, request.form.get("password", ""), request, response)
            return self._redirect("/share=%s" % shareID, response)

        isAdmin = self.ap.isAdmin(request)
        subPath = os.path.normpath(shareIDAndPath.replace(shareID, "")).lstrip("/").rstrip("/").lstrip(".")
        share, hint = self.sp.getShare(shareID, asAdmin=isAdmin, r=request, subPath=subPath)
        if share is None: raise Exception("Can't get Share %s, %s" % (shareID, hint))

        if isAdmin: return self._makeTemplate("share-admin", shareID=shareID, share=share)

        sharePassword = share.get("password", "")
        shareBasePath = share["file"]
        path = h.makePath(shareBasePath, subPath).rstrip("/")
        displayPath = path.replace(shareBasePath, shareID)
        if sharePassword != "" and not isAdmin and not self.ap.isShareAuthorized(shareID, request): return self._makeTemplate("share-password", displayPath=displayPath, share=share)
        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)
        if ip.isItemLeaf(path): return send_from_directory(h.DATA_FOLDER, path)
        else:
            alerts = []
            containers, leafs = self.ip.getItems(path, overrideListingForbidden=True, overrideNoShow=True)
            return self._makeTemplate("share", displayPath=displayPath, shareBasePath=shareBasePath, subPath=subPath, share=share, containers=containers, leafs=leafs, alerts=alerts, readme=ip.getReadme(path))

    ###################################################################################
    def _makeBaseNamspace(self):
        return {"h": h, "baseURL": "", "rootURL": self._getRootURL(), "tracking": h.TRACKING, "sharing": h.SHARING}

    ###################################################################################
    def _makeTemplate(self, name, **data):
        return Template(filename=h.makePath(h.ROOT_FOLDER, "templates", "%s.mako" % name), lookup=self.tplLookup).render(**data, **self._makeBaseNamspace())

    ###################################################################################
    def _downloadAndDeleteFile(self, path, name):
        result = send_file(path, as_attachment=True, attachment_filename=name)
        os.remove(path)
        return result

    ###################################################################################
    def _redirect(self, path, response=None):
        if response is None: response = make_response()
        response.headers["Location"] = path
        response._status_code = 302
        response._status = "302 FOUND"
        return response

    ###################################################################################
    def _getDomain(self):
        return self._getRootURL().replace("https://", "").replace("http://", "")

    ###################################################################################
    def _getRootURL(self):
        return request.url_root.rstrip("/")

    ###################################################################################
    def _aliasPath(self, path):
        if self.aliases is None: return path
        return self.aliases.get(path, path)


###################################################################################
###################################################################################
###################################################################################
class RedirectServer(Thread):
    ###################################################################################
    def __init__(self, port, mainServer: Server):
        Thread.__init__(self)
        self.app = Flask(__name__)
        self.port = port
        self.httpServer = None
        self.mainServer = mainServer

    ###################################################################################
    def run(self):
        self.httpServer = WSGIServer(("0.0.0.0", self.port), self.mainServer.app, log=None)
        self.httpServer.serve_forever()

    ###################################################################################
    def stop(self):
        self.httpServer.stop()


###################################################################################
# MAIN
###################################################################################
h.displaySplash()

ap = ap.authProvider(h.DATA_FOLDER, h.CONFIG.get("admin password", ""), h.FORBIDEN_ITEMS)
h.logInfo("Auth provider built")

tp = tp.trackingProvider(h.DATA_FOLDER, user=h.USER)
h.logInfo("Tracking provider built")

sp = sp.sharesProvider(ap, h.makePath(h.DATA_FOLDER, "_sf_shares"), user=h.USER)
h.logInfo("Shares provider built")

ip = ip.itemsProvider(ap, h.DATA_FOLDER, tmpFolder=h.CONFIG.get("tmp folder", None), tmpFolderDuratioInDaysn=h.CONFIG.get("tmp folder duration in days", None), user=h.USER)
h.logInfo("Items provider built")

server = Server(ip, ap, sp, h.PORT, h.SSL, h.CERTIFICATE_KEY_FILE, h.CERTIFICATE_CRT_FILE, h.FULLCHAIN_CRT_FILE, aliases=h.CONFIG.get("aliases", None), maxUploadSize=h.CONFIG.get("max upload size", 20e6))
server.start()
h.logInfo("Server started", server.port, server.ssl)

secondaryServer, secondaryPort = None, h.CONFIG.get("secondary port", None)
if secondaryPort is not None:
    time.sleep(1)
    secondaryServer = RedirectServer(secondaryPort, server)
    secondaryServer.start()
    h.logInfo("Secondary server started", secondaryPort)

try: signal.pause()
except:
    server.stop()
    if secondaryServer is not None: secondaryServer.stop()
    ip.stop()
