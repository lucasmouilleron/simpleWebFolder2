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
import threading
import time
from threading import Lock
import json
from urllib.parse import urlparse


###################################################################################
###################################################################################
###################################################################################
class Server(Thread):

    ###################################################################################
    def __init__(self, ip: ip.itemsProvider, ap: ap.authProvider, sp: sp.sharesProvider, tp: tp.trackingProvider, port, ssl=False, certificateKeyFile=None, certificateCrtFile=None, fullchainCrtFile="", aliases=None, maxUploadSize=None):
        Thread.__init__(self)
        self.app = Flask(__name__)
        self.ip = ip
        self.ap = ap
        self.sp = sp
        self.tp = tp
        self.port = port
        self.ssl = ssl
        self.certificateKeyFile = certificateKeyFile
        self.certificateCrtFile = certificateCrtFile
        self.fullchainCrtFile = fullchainCrtFile
        self.httpServer = None
        self.aliases = aliases
        self.maxUploadSize = maxUploadSize

        self.firewallIPs = {}
        self.firewallNbHits = 150
        self.firewallWindowSize = 10
        self.firewallLock = Lock()

        if self.maxUploadSize is not None: self.app.config["MAX_CONTENT_LENGTH"] = self.maxUploadSize

        self._addRoute("/_hello", self._routeHello, ["GET"])
        self._addRoute("/_infos", self._routeInfos, ["GET"])
        self._addRoute("/_ping", self._routePing, ["GET"])
        self._addRoute("/_list", self._routeList, ["GET"])
        self._addRoute("/_list/<path:path>", self._routeList, ["GET"])
        self._addRouteRaw("/", self._routeItems, ["GET", "POST"], "index")
        self._addRouteRaw("/<path:path>", self._routeItems, ["GET", "POST"], noCache=True)
        self._addRouteRaw("/_sf_assets/<path:path>", self._routeAssets, ["GET"])
        self._addRouteRaw("/admin", self._routeAdmin, ["GET", "POST"])
        self._addRouteRaw("/noadmin", self._routeNoAdmin, ["GET"])
        self._addRouteRaw("/tracking", self._routeTrackingAdmin, ["GET", "POST"])
        self._addRouteRaw("/share=<path:shareIDAndPath>", self._routeShare, ["GET", "POST"])
        self._addRouteRaw("/shares", self._routeShares, ["GET", "POST"])
        self._addRouteRaw("/remove-share=<shareID>", self._routeShareRemove, ["GET"])
        self._addRouteRaw("/create-share=<paths>", self._routeShareAdd, ["GET", "POST"])

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
    def _firewall(self, r: request):
        if len(self.firewallIPs) > 1000: threading.Thread(target=self._firewallCleanup).start()
        try:
            self.firewallLock.acquire()
            userIP = r.remote_addr
            if not userIP in self.firewallIPs: self.firewallIPs[userIP] = {"banned": 0, "hits": []}
            f = self.firewallIPs[userIP]
            now = h.now()
            banned = f["banned"]
            if now < banned: return False, "Too many requests, banned for %s seconds" % (banned - now)
            hits = f["hits"]
            hits.append(h.now())
            if len(hits) < self.firewallNbHits: return True, ""
            windowStart = now - self.firewallWindowSize
            hits = [hit for hit in hits if hit >= windowStart]
            f["hits"] = hits
            if len(hits) >= self.firewallNbHits:
                f["banned"] = now + 1 * self.firewallWindowSize
                h.logWarning("IP added to firewall", userIP)
                return False, "Too many requests, banned for %s seconds" % (banned - now)
            return True, ""
        except: return True, ""
        finally:
            if self.firewallLock.locked(): self.firewallLock.release()

    ###################################################################################
    def _firewallCleanup(self):
        try:
            self.firewallLock.acquire()
            for k in list(self.firewallIPs):
                ips = self.firewallIPs[k]
                if len(ips) == 0: self.firewallIPs.pop(k)
                elif ips["hits"][-1] < h.now() - self.firewallWindowSize: self.firewallIPs.pop(k)
        finally:
            if self.firewallLock.locked(): self.firewallLock.release()

    ###################################################################################
    def _addRoute(self, rule, callback, methods=["GET"], endpoint=None, noCache=True):
        def callbackReal(*args, **kwargs):
            try:
                passed, hint = self._firewall(request)
                if not passed: return Template(filename=h.makePath(h.ROOT_FOLDER, "templates", "error.mako"), lookup=self.tplLookup).render(e=hint, **self._makeBaseNamspace(), le=None, lt=None)
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
                passed, hint = self._firewall(request)
                if not passed: return Template(filename=h.makePath(h.ROOT_FOLDER, "templates", "error.mako"), lookup=self.tplLookup).render(e=hint, **self._makeBaseNamspace(), le=None, lt=None)
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
    def _routeList(self, path="/"):
        if request.headers.get("password") != ap.adminPassword: return {"result": 403}
        path = h.cleanPath(self._aliasPath(path))
        if not ip.doesItemExists(path): return {"result": 500, "error": "path %s does not exist" % path}
        containers, leafs = ip.getItems(path, request)
        containers, leafs = [c.__dict__ for c in containers], [l.__dict__ for l in leafs]
        return {"result": 200, "path": path, "containers": containers, "leafs": leafs}

    ###################################################################################
    def _routeInfos(self):
        if request.headers.get("password") != ap.adminPassword: return {"result": 403}
        allTrackings = self.tp.getTrackings()
        hitsByItems, _ = h.groupItemsByKey(allTrackings, lambda d: d.path)
        hitsByItems = {k: [hit.date for hit in hitsByItems[k]] for k in hitsByItems}
        hits = [t.date for t in allTrackings]
        return {"result": 200, "version": h.dictionnaryDeepGet(h.CONFIG, "version", default=0), "trackings": [t.__dict__ for t in self.tp.getTrackings(maxItems=5e3)], "hits": hits, "hitsByItems": hitsByItems}

    ###################################################################################
    def _routeAssets(self, path):
        return send_from_directory(h.makePath(h.ROOT_FOLDER, "assets"), path)

    ###################################################################################
    def _routePing(self):
        return {"result": 200, "pong": h.now()}

    ###################################################################################
    def _routeItems(self, path="/"):
        path = h.cleanPath(self._aliasPath(path))

        if self.ap.isAdmin(request): return self._routeAdmin(path)

        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)

        item = self.ip.getItem(path, request)
        if item is None: return self._makeTemplate("error", path=path, e="Can't get item")

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setUserPassword(item.lowerProtectedPath, request.form.get("password", ""), request, response)
            return self._redirect(path, response)

        if h.TRACKING: self.tp.track(path, request, item.protected, item.isAuthorized, item.savedPassword)
        alerts = []
        if item.isAuthorized:
            if ip.isItemLeaf(path):
                if item.forbidden: return self._makeTemplate("forbidden", path=path)
                return send_from_directory(h.DATA_FOLDER, path)
            else:
                if item.forbidden: return self._makeTemplate("forbidden", path=path)
                if item.listingForbidden: return self._makeTemplate("forbidden", path=path)
                if "download" in request.args and not item.downloadForbidden: return self._downloadAndDeleteFile(ip.getZipFile(path, request), "%s.zip" % (os.path.basename(path) if path != "" else "root"))
                containers, leafs = ip.getItems(path, request)
                readme = ip.getReadme(path)
                return self._makeTemplate("items", containers=containers, leafs=leafs, path=path, readme=readme, downloadAllowed=not self.ap.downloadForbidden(path), currentURLWithoutURI=path, alerts=alerts)
        else:
            if item.protected:
                if item.savedPassword is not None and item.savedPassword != "": alerts.append(["Can't authenticate", "The password you provided (%s) is not valid." % item.savedPassword])
                else: alerts.append(["Can't authenticate", "You did not provide a password."])
            return self._makeTemplate("password", path=path, lowerProtectedPath=item.lowerProtectedPath, alerts=alerts)

    ###################################################################################
    def _routeNoAdmin(self):
        response = make_response()
        self.ap.removeAdminPassword(request, response)
        return self._redirect("/", response)

    ###################################################################################
    def _routeAdmin(self, path="/"):
        path = h.cleanPath(path)

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setAdminPassword(request.form.get("password-admin", ""), request, response)
            return self._redirect("/admin", response)

        if not self.ap.isAdmin(request): return self._makeTemplate("password-admin")

        return self._routeItemsAdmin(path)

    ###################################################################################
    def _routeItemsAdmin(self, path):
        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)

        alerts = []

        if request.args.get("deleted") is not None:
            alerts.append(["Item deleted", "The item /%s has been removed." % request.args.get("deleted")])

        if request.args.get("remove") is not None:
            if not self.ap.isEditAllowed(self.ip.getParent(path)): return self._makeTemplate("forbidden", path=path)
            if not self.ip.remove(path): alerts.append(["Can't delete item", "The item /%s can't be removed." % path])
            else: return self._redirect("/%s" % self.ip.getParent(path), queryArgs={"deleted": path})

        if ip.isItemLeaf(path): return send_from_directory(h.DATA_FOLDER, path)

        editAllowed = self.ap.isEditAllowed(path)

        if request.form.get("add-password-submit", False):
            passwordToAdd = request.form.get("new-password", None).strip()
            if self.ap.addNewPassword(path, passwordToAdd): alerts.append(["Password added", "The password %s has been added." % passwordToAdd])
            else: alerts.append(["Can't add password", "The password %s could not be added." % passwordToAdd])

        if request.form.get("add-leaf", False):
            if not editAllowed: return self._makeTemplate("forbidden", path=path)
            file = request.files["file"]
            result, hint = self.ip.addLeaf(path, file)
            if not result: alerts.append(["Can't add file", "The file can't be added: %s." % hint])
            else: alerts.append(["File added", "The file %s has been added." % hint])

        item = self.ip.getItem(path, request)
        containers, leafs = ip.getItems(path, request, asAdmin=True)
        isTmpFolder = self.ip.tmpFolder == path
        readme = ip.getReadmeAdmin(path)
        subAlerts = []
        if item.protected and len(item.passwords) > 1: subAlerts.append("Password protected, see passwords below.")
        if item.protected and len(item.passwords) == 1: subAlerts.append("Password protected: %s" % item.passwords[0])
        if isTmpFolder: subAlerts.append("Tmp folder.")
        if editAllowed: subAlerts.append("Edit/upload allowed.")
        if item.listingForbidden: subAlerts.append("Listing not allowed for non admin users.")
        if item.showForbidden: subAlerts.append("Folder not shown for non admin users.")
        if item.shareForbidden: subAlerts.append("Folder cannot be shared with Sares.")
        if item.downloadForbidden and path != "": subAlerts.append("Folder not downloadable.")
        if item.passwordEditForbidden: subAlerts.append("Can't edit passwords.")
        if len(subAlerts) > 0: alerts.append(["Special folder", "<br/>".join(subAlerts)])
        response = make_response(self._makeTemplate("items-admin", isProtected=item.protected, isProtectedFromParent=item.protectedFromParent, passwords=sorted(item.passwords), containers=containers, leafs=leafs, path=path, readme=readme, alerts=alerts, editAllowed=editAllowed, isTmpFolder=isTmpFolder, passwordEditForbidden=item.passwordEditForbidden))
        return response

    ###################################################################################
    def _routeTrackingAdmin(self):
        if not h.TRACKING: return self._redirect("/admin")
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        maxItems, password, item, protected = request.form.get("maxItems", "500"), request.form.get("password", ""), request.form.get("item", ""), request.form.get("protected", "yes")
        return self._makeTemplate("tracking", trackings=self.tp.getTrackings(password if password != "" else None, item if item != "" else None, protected, h.parseInt(maxItems, None)), password=password, item=item, maxItems=maxItems, protected=protected)

    ###################################################################################
    def _routeShares(self, alerts=None, shareAdded=None):
        if alerts is None: alerts = []
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        maxShares = 50
        filterShareID = request.form.get("filterShareID", "")
        return self._makeTemplate("shares-admin", shares=self.sp.listShares(filterShareID, maxShares=maxShares), alerts=alerts, maxShares=maxShares, filterShareID=filterShareID, shareAdded=shareAdded)

    ###################################################################################
    def _routeShareRemove(self, shareID):
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        self.sp.removeShare(shareID)
        return self._routeShares(alerts=[["Share removed", "The Share %s has been removed." % shareID]])

    ###################################################################################
    def _routeShareAdd(self, paths):
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        if self.ap.shareForbidden(paths): return self._makeTemplate("forbidden", path=paths)
        alerts = []
        paths = h.decode(paths)
        paths = paths.split("@@@")
        shareID = request.form.get("shareID", "")
        defaultShareID = request.form.get("defaultShareID", h.uniqueIDSmall())
        duration = request.form.get("duration", "")
        durationInSecs = h.parseInt(duration, 0) * 24 * 60 * 60
        password = request.form.get("password-share-add", "")
        shareSubmit = request.form.get("create-share-submit", False)
        shareForceSubmit = request.form.get("create-share-force-submit", False)
        needForce = False
        containers = [p for p in paths if self.ip.isItemContainer(p)]
        if shareSubmit or shareForceSubmit:
            if shareID == "": shareID = defaultShareID
            shareID = h.clean(shareID)
            if shareID == "": alerts.append(["Can't create Share", "Share ID provided is invalid."])
            else:
                if not sp.shareExists(shareID) or shareForceSubmit:
                    share, hint = self.sp.addShare(shareID, paths, durationInSecs, password)
                    if share is not None:
                        # alerts.append(["Share created", "The Share %s has been created for %s" % (shareID, path)])
                        return self._routeShares(alerts, shareAdded=share)
                    else: alerts.append(["Can't create Share", "Share %s could not be created. Hint: %s" % (shareID, hint)])
                else:
                    alerts.append(["Can't create Share", "The Share ID %s is already used for %s." % (shareID, ", ".join(paths))])
                    needForce = True
        return self._makeTemplate("share-add", paths=paths, defaultShareID=defaultShareID, shareID=shareID, duration=duration, alerts=alerts, needForce=needForce, containers=containers)

    ###################################################################################
    def _routeShare(self, shareIDAndPath):
        shareID = shareIDAndPath.split("/")[0]
        query = str(request.query_string, "utf8")
        if not self.sp.shareExists(shareID): return self._makeTemplate("not-found", path=shareID)

        if request.form.get("password-submit", False):
            response = make_response()
            self.ap.setSharePassword(shareID, request.form.get("password-share", ""), request, response)
            return self._redirect(h.makeURL("/share=%s" % shareID, query), response)

        isAdmin = self.ap.isAdmin(request)
        subPath = h.cleanPath(os.path.normpath(shareIDAndPath.replace(shareID, ""))).lstrip(".")

        s, hint = self.sp.getShare(shareID, asAdmin=isAdmin, r=request)
        if s is None: raise Exception("Can't get Share %s, %s" % (shareID, hint))

        baseFilesIndexes = {s.files[i].split("/")[-1]: i for i in range(len(s.files))}
        subPathBits = subPath.split("/")
        if not isAdmin and len(s.files) == 1 and subPath == "": return self._redirect(h.makeURL("/share=%s/%s" % (shareID, s.files[0].split("/")[-1]), query))
        elif subPath == "": baseFile, indexFile = None, -1
        else:
            baseFile = subPathBits.pop(0)
            indexFile = baseFilesIndexes.get(baseFile, -2)

        isAuthorized, savedPassword = self.ap.isShareAuthorized(s, request)
        if not isAdmin: self.sp.addView(s, h.makePath(*subPathBits), baseFile, request.remote_addr if request is not None else None, s.tag, isAuthorized)
        if indexFile == -2: return self._makeTemplate("not-found", path="%s" % shareID)
        if isAdmin and request.args.get("view") is None: return self._makeTemplate("share-admin", shareID=shareID, share=s)

        if indexFile == -1: path, displayPath, shareBasePath = "", shareID, ""
        else:
            shareBasePath = s.files[indexFile]
            path = h.cleanPath(h.makePath(shareBasePath, *subPathBits))
            if baseFile is not None: shareBasePath = shareBasePath.replace(baseFile, "")
            displayPath = shareID
            if baseFile is not None: displayPath = h.makePath(displayPath, baseFile)
            if subPath != "": displayPath = h.makePath(displayPath, *subPathBits)

        if h.TRACKING and not isAdmin: self.tp.track(path, request, ap.isShareProtected(s), isAuthorized, savedPassword, shareID, s.tag)
        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=displayPath)
        if not isAdmin and not isAuthorized: return self._makeTemplate("share-password", displayPath=displayPath, share=s)

        if indexFile == -1:
            isLeaf, readme = False, None
            containers, leafs = [], []
            for file in s.files:
                item = ip.getItem(file)
                item.path = item.path.split("/")[-1]
                if ip.isItemContainer(file): containers.append(item)
                else: leafs.append(item)
        else:
            isLeaf = ip.isItemLeaf(path)
            if not isLeaf:
                containers, leafs = self.ip.getItems(path, overrideListingForbidden=True, overrideNoShow=True)
                readme = ip.getReadme(path)
            else: containers, leafs, readme = None, None, None
        if isLeaf: return send_from_directory(h.DATA_FOLDER, path)
        else: return self._makeTemplate("share", displayPath=displayPath, shareBasePath=shareBasePath, subPath=subPath, share=s, containers=containers, leafs=leafs, alerts=[], readme=readme, indexFile=indexFile)

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
    def _redirect(self, path, response=None, queryArgs=None):
        if response is None: response = make_response()
        if queryArgs is None: queryArgs = {}
        if len(queryArgs) > 0: path = h.updateQueryParams(path, queryArgs)
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
        path = h.cleanPath(path)
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

tp = tp.trackingProvider(h.DATA_FOLDER, user=h.USER, locationEnabled=h.TRACKING_IP_GEOLOC, locationAPIKey=h.CONFIG.get("ip geoloc api key", ""))
h.logInfo("Tracking provider built")

sp = sp.sharesProvider(h.makePath(h.DATA_FOLDER, "_sf_shares"), user=h.USER, locationEnabled=h.TRACKING_IP_GEOLOC, locationAPIKey=h.CONFIG.get("ip geoloc api key", ""))
h.logInfo("Shares provider built")

ip = ip.itemsProvider(ap, h.DATA_FOLDER, tmpFolder=h.CONFIG.get("tmp folder", None), tmpFolderDuratioInDaysn=h.CONFIG.get("tmp folder duration in days", None), user=h.USER, hiddenItems=h.HIDDEN_ITEMS)
h.logInfo("Items provider built")

server = Server(ip, ap, sp, tp, h.PORT, h.SSL, h.CERTIFICATE_KEY_FILE, h.CERTIFICATE_CRT_FILE, h.FULLCHAIN_CRT_FILE, aliases=h.CONFIG.get("aliases", None), maxUploadSize=h.CONFIG.get("max upload size", 20e6))
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
    tp.stop()
