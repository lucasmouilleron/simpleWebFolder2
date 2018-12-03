###################################################################################
# IMPORTS
###################################################################################
import signal
from threading import Thread
from gevent.wsgi import WSGIServer
from flask import Flask, request, jsonify, send_from_directory, redirect, make_response, send_file, url_for
from flask_cors import CORS
from mako.template import Template
from mako.lookup import TemplateLookup
import helper as h
import itemsProvider as ip
import authProvider as ap
import trackingProvider as tp
import os
import mimetypes


###################################################################################
###################################################################################
###################################################################################
class Server(Thread):

    ###################################################################################
    def __init__(self, ip: ip.itemsProvider, ap: ap.authProvider, port, ssl=False, certificateKeyFile=None, certificateCrtFile=None, fullchainCrtFile=""):
        Thread.__init__(self)
        self.app = Flask(__name__)
        self.ip = ip
        self.ap = ap
        self.port = port
        self.ssl = ssl
        self.certificateKeyFile = certificateKeyFile
        self.certificateCrtFile = certificateCrtFile
        self.fullchainCrtFile = fullchainCrtFile
        self.httpServer = None

        self._addRoute("/hello", self._routeHello, ["GET"])
        self._addRouteRaw("/", self._routeItems, ["GET", "POST"], "index")
        self._addRouteRaw("/<path:path>", self._routeItems, ["GET", "POST"])
        self._addRouteRaw("/_sf_assets/<path:path>", self._routeAssets, ["GET", "POST"])
        self._addRouteRaw("/admin", self._routeAdmin, ["GET", "POST"])
        self._addRouteRaw("/noadmin", self._routeNoAdmin, ["GET"])
        self._addRouteRaw("/tracking", self._routeTrackingAdmin, ["GET", "POST"])
        self._addRouteRaw("/shares", self._routeSharesAdmin, ["GET", "POST"])
        self._addRouteRaw("/share", self._routeShare, ["GET", "POST"])

        self.tplLookup = TemplateLookup(directories=[h.makePath(h.ROOT_FOLDER, "templates")])

    ###################################################################################
    def run(self):
        CORS(self.app)
        if self.ssl: self.httpServer = WSGIServer(("0.0.0.0", self.port), server.app, log=None, keyfile=self.certificateKeyFile, certfile=self.certificateCrtFile, ca_certs=self.fullchainCrtFile)
        else: self.httpServer = WSGIServer(("0.0.0.0", self.port), server.app, log=None)
        self.httpServer.serve_forever()

    ###################################################################################
    def stop(self):
        self.httpServer.stop()

    ###################################################################################
    def _addRoute(self, rule, callback, methods=["GET"], endpoint=None):
        def callbackReal(*args, **kwargs):
            try: return jsonify(callback(*args, **kwargs))
            except Exception as e:
                h.logWarning("Error processing request", request.data.decode("utf-8"), request.endpoint, h.formatException(e))
                return jsonify({"result": 500, "hint": h.formatException(e)})

        if endpoint is None: endpoint = h.uniqueID()
        self.app.add_url_rule(rule, endpoint, callbackReal, methods=methods)

    ###################################################################################
    def _addRouteRaw(self, rule, callback, methods, endpoint=None):
        def callbackReal(*args, **kwargs):
            try: return callback(*args, **kwargs)
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
        return send_from_directory(h.makePath(h.DATA_FOLDER, "_sf_assets"), path)

    ###################################################################################
    def _routeItems(self, path="/"):
        path = path.rstrip("/")
        if ap.isAdmin(request): return self._routeAdmin(path)

        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)
        if request.form.get("password-submit", False):
            response = make_response()
            ap.setUserPassword(path, request.form.get("password", ""), request, response)
            return self._redirect(path, response)

        isProtected, requiredPasswords, savedPassword, isAuthorized = ap.isAuthorized(path, request)
        if h.TRACKING: tp.track(path, request, isAuthorized, savedPassword)
        if isAuthorized:
            if ip.isItemLeaf(path):
                if self.ap.isForbidden(path): return self._makeTemplate("forbidden", path=path)
                return send_from_directory(h.DATA_FOLDER, path)
            else:
                if self.ap.isForbidden(path): return self._makeTemplate("forbidden", path=path)
                if ap.listingForbidden(path): return self._makeTemplate("forbidden", path=path)
                if "download" in request.args: return self._downloadAndDeleteFile(ip.getZipFile(path, request), "%s.zip" % (os.path.basename(path) if path != "" else "root"))
                alerts = []
                containers, leafs = ip.getItems(path, request)
                readme = ip.getReadme(path)
                return self._makeTemplate("items", containers=containers, leafs=leafs, path=path, readme=readme, downloadAllowed=not self.ap.downloadForbidden(path), currentURLWithoutURI=path, alerts=alerts)
        else: return self._makeTemplate("password", path=path)

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
            ap.setAdminPassword(request.form.get("password", ""), request, response)
            return self._redirect("/", response)

        if not self.ap.isAdmin(request): return self._makeTemplate("password-admin")

        return self._routeItemsAdmin(path)

    ###################################################################################
    def _routeItemsAdmin(self, path):
        if not ip.doesItemExists(path): return self._makeTemplate("not-found", path=path)
        if ip.isItemLeaf(path): return send_from_directory(h.DATA_FOLDER, path)
        alerts = []
        isProtected, requiredPasswords, _, _ = ap.isAuthorized(path, request)
        containers, leafs = ip.getItems(path, request)
        readme = ip.getReadme(path)
        response = make_response(self._makeTemplate("items-admin", passwords=requiredPasswords, containers=containers, leafs=leafs, path=path, readme=readme, downloadAllowed=not self.ap.downloadForbidden(path), alerts=alerts))
        return response

    ###################################################################################
    def _routeTrackingAdmin(self):
        if not h.TRACKING: return self._redirect("/admin")
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        return self._makeTemplate("tracking", trackings=[], password="", item="")

    ###################################################################################
    def _routeSharesAdmin(self):
        if not self.ap.isAdmin(request): return self._redirect("/admin")
        return "shares"

    ###################################################################################
    def _routeShare(self):
        return "share"

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
    def _getRootURL(self):
        return request.url_root.rstrip("/")


###################################################################################
# MAIN
###################################################################################
h.displaySplash()

ap = ap.authProvider(h.DATA_FOLDER, h.CONFIG.get("admin password", ""), h.FORBIDEN_ITEMS)
h.logInfo("Auth provider built")

tp = tp.trackingProvider(h.DATA_FOLDER)
h.logInfo("Tracking provider built")

ip = ip.itemsProvider(ap,  h.DATA_FOLDER)
h.logInfo("Items provider built")

server = Server(ip, ap, h.PORT, h.SSL, h.CERTIFICATE_KEY_FILE, h.CERTIFICATE_CRT_FILE, h.FULLCHAIN_CRT_FILE)
server.start()
h.logInfo("Server started", server.port, server.ssl)

signal.pause()
server.stop()
