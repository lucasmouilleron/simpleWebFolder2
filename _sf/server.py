###################################################################################
# IMPORTS
###################################################################################
import signal
from threading import Thread
from gevent.wsgi import WSGIServer
from flask import Flask, request, jsonify, send_from_directory, redirect, make_response
from flask_cors import CORS
from mako.template import Template
from mako.lookup import TemplateLookup
import helper as h
import itemsProvider as ip
import authProvider as ap


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
        self._addRouteRaw("/", self._routeUser, ["GET", "POST"])
        self._addRouteRaw("/<path:path>", self._routeUser, ["GET", "POST"])
        self._addRouteRaw("/sf_assets/<path:path>", self._routeAssets, ["GET", "POST"])

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
    def _routeUser(self, path="/"):
        path = path.rstrip("/")
        if ip.doesItemExists(path):
            isProtected, requiredPasswords, savedPassword, isAuthorized = ap.isAuthorized(path, request)
            if isAuthorized:
                if ip.isItemLeaf(path):
                    return send_from_directory(h.DATA_FOLDER, path)
                else:
                    containers, leafs = ip.getItems(path, request)
                    # todo check listing allowed
                    # hide not show
                    downloadAllowed = True
                    currentURLWithoutURI = path

                    return Template(filename=h.makePath(h.ROOT_FOLDER, "templates", "items.mako"), lookup=self.tplLookup).render(containers=containers, leafs=leafs, path=path, downloadAllowed=downloadAllowed, currentURLWithoutURI=currentURLWithoutURI, **self._makeBaseNamspace())
            else:
                return "not authorized"
        else:
            return "does not exist"

        # response = make_response("")
        # response.set_cookie("test","test2")
        # return response

    ###################################################################################
    def _makeBaseNamspace(self):
        return {"baseURL": "", "h": h}


###################################################################################
# MAIN
###################################################################################
h.displaySplash()

ap = ap.authProvider(h.DATA_FOLDER)
h.logInfo("Auth provider built")

ip = ip.itemsProvider(ap, h.DATA_FOLDER, h.FORBIDEN_ITEMS)
h.logInfo("Items provider built")

server = Server(ip, ap, h.dictionnaryDeepGet(h.CONFIG, "server", "port", default=5000), h.dictionnaryDeepGet(h.CONFIG, "server", "ssl", default=False), h.CERTIFICATE_KEY_FILE, h.CERTIFICATE_CRT_FILE, h.FULLCHAIN_CRT_FILE)
server.start()
h.logInfo("Server started", server.port, server.ssl)

signal.pause()
server.stop()
