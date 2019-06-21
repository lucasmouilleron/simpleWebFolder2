###################################################################################
import datetime
import os
import coloredlogs
import json
import logging.handlers
import logging
from threading import Thread, Event
import zlib
import binascii
import dateutil
import arrow
import csv
import uuid
from os import listdir
from os.path import isfile
import re
import urllib.parse
import traceback
import collections
import portalocker
import time
import base64
import pwd
import urllib.parse as urlparse
from urllib.parse import urlencode
import shutil
from collections import OrderedDict
from urllib import parse

###################################################################################
SERVER_TIMEZONE = "Europe/Paris"
FORBIDEN_ITEMS = [".", "..", ".tracking", ".password", ".nopassword", ".nolist", ".noshow", ".nodownload", ".DS_Store", "Icon\r", ".htaccess", "README.md", "README.admin.md", ".git", ".idea", ".gitignore"]
HIDDEN_ITEMS = ["robots.txt"]
EXTENSIONS_CLASSES = {"default": "fas fa-file", "html": "fas fa-file-code", "jpg": "fas fa-file-image", "gif": "fas fa-file-image", "png": "fas fa-file-image", "pdf": "fas fa-file-pdf", "ppt": "fas fa-file-powerpoint", "pptx": "fas fa-file-powerpoint", "doc": "fas fa-file-word", "docx": "fas fa-file-word", "xls": "fas fa-file-excel", "xlsx": "fas fa-file-excel", "avi": "fas fa-file-video", "mov": "fas fa-file-video", "mp4": "fas fa-file-video", "wav": "fas fa-file-audio", "mp3": "fas fa-file-audio", "zip": "fas fa-file-archive", "tgz": "fas fa-file-archive"}
###################################################################################
ROOT_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = ROOT_FOLDER + "/../"
CONFIG_FOLDER = ROOT_FOLDER + "/config"
CONFIG_FILE = CONFIG_FOLDER + "/config.json"
###################################################################################
if os.path.exists(CONFIG_FILE): CONFIG = json.load(open(CONFIG_FILE))
else: CONFIG = {}
###################################################################################
PORT = CONFIG.get("port", 5000)
SSL = CONFIG.get("ssl", False)
CERTIFICATE_KEY_FILE = CONFIG_FOLDER + "/ssl/server.key"
CERTIFICATE_CRT_FILE = CONFIG_FOLDER + "/ssl/server.crt"
FULLCHAIN_CRT_FILE = CONFIG_FOLDER + "/ssl/fullchain.crt"
###################################################################################
DEBUG = CONFIG.get("debug", False)
NAME = CONFIG.get("name", "SWF2")
CREDITS = CONFIG.get("credits", "Lucas Mouilleron")
MAIL = CONFIG.get("mail", "lucas.mouilleron@me.com")
TRACKING = CONFIG.get("tracking", False)
TRACKING_IP_GEOLOC = CONFIG.get("ip geoloc", False)
SHARING = CONFIG.get("sharing", False)
TMP_FOLDER = CONFIG.get("tmp folder", "/tmp")
LOCKS_FOLDER = CONFIG.get("locks folder", TMP_FOLDER + "/_sf_locks")
USER = CONFIG.get("user", None)
###################################################################################
LOG_FORMAT = "%(asctime)-15s - %(levelname)-7s - %(message)s"
LOG_LOGGER = "main"
LOG_FOLDER = DATA_FOLDER + "/_sf_log"
LOG_FILENAME = LOG_FOLDER + "/all.log"
SPLASH_FILE = ROOT_FOLDER + "/config/splash.txt"
STORE_LOG = CONFIG.get("store log", False)
###################################################################################
CSV_SEP = ";"
CSV_SEP_SAFE = "---"

###################################################################################
IP_LOCATIONS_DONE = {}

###################################################################################
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(coloredlogs.ColoredFormatter(fmt="%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger(LOG_LOGGER).addHandler(consoleHandler)
logging.getLogger(LOG_LOGGER).setLevel(logging.DEBUG)
if STORE_LOG:
    if not os.path.exists(LOG_FOLDER): os.mkdir(LOG_FOLDER)
    fileHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10e6, backupCount=5)
    fileHandler.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger(LOG_LOGGER).addHandler(fileHandler)

################################################################################
if not os.path.exists(DATA_FOLDER): os.mkdir(DATA_FOLDER)
if not os.path.exists(LOCKS_FOLDER): os.mkdir(LOCKS_FOLDER)


################################################################################
def readFromFile(filePath):
    f = open(filePath, 'r')
    text = f.read()
    f.close()
    return text


################################################################################
def writeToFile(filePath, text, append=False):
    if append:  f = open(filePath, 'a+')
    else: f = open(filePath, 'w+')
    f.write(text)
    f.close()


###################################################################################
def displaySplash():
    try: print(open(SPLASH_FILE, encoding="utf-8").read())
    except: pass


################################################################################
def uniqueID():
    return str(uuid.uuid4())


################################################################################
def uniqueIDSmall():
    return str(uuid.uuid4())[:8]


###################################################################################
def logInfo(*args):
    logging.getLogger(LOG_LOGGER).info(" - ".join(str(a) for a in args))


###################################################################################
def logWarning(*args):
    logging.getLogger(LOG_LOGGER).warning(" - ".join(str(a) for a in args))


###################################################################################
def logDebug(*args):
    if CONFIG.get("debug", False):
        logging.getLogger(LOG_LOGGER).debug(" - ".join(str(a) for a in args))


###################################################################################
def objectToString(object):
    return str(object.__dict__)


###################################################################################
def timestampToDatetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d %H:%M:%S')


###################################################################################
def timestampToTime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')


###################################################################################
def timestampToDay(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d')


###################################################################################
class AbortInterrupt(Exception):
    pass


###################################################################################
class InterruptibleThread(Thread):
    def __init__(self, stopEvent=None, abortEvent=None, **kwargs):
        Thread.__init__(self, **kwargs)
        if stopEvent is None: stopEvent = Event()
        self.stopEvent = stopEvent
        if abortEvent is None: abortEvent = Event()
        self.abortEvent = abortEvent

    def join(self, timeout=None):
        Thread.join(self, timeout)

    def sleep(self, time):
        self.abortEvent.wait(time)

    def abort(self):
        self.abortEvent.set()

    def shutdown(self):
        self.stopEvent.set()
        self.join()

    def abortBreakoutPoint(self):
        if self.checkAbortEvent(): raise AbortInterrupt("user requested abort")

    def checkAbortEvent(self):
        return self.abortEvent.isSet()

    def checkStopEvent(self):
        return self.stopEvent.isSet()


################################################################################
def removeLineBreaks(string):
    return string.replace('\n', ' ').replace('\r', ' ')


################################################################################
def writeToCSV(data, filePath, csvSEP=CSV_SEP, append=False, debug=False, noEmptyLastLine=False, headers=[], convertNan=True, replaceSeparatorInCells=True, removeLineBreakss=True, omitNoneRows=False, convertToStr=True):
    mode = "w"
    if append: mode = "a"
    fileSize = getFileSize(filePath)
    csvFile = open(filePath, mode, encoding="utf-8")
    isIterable = True
    if len(data) > 0: isIterable = isinstance(data[0], collections.Iterable)
    if len(headers) > 0 and (not append or fileSize == 0): csvFile.write(csvSEP.join(headers) + "\n")
    for i in range(len(data)):
        line = data[i]
        if omitNoneRows and line is None: continue
        lineString = ""
        first = True
        if not isIterable: line = [line]
        for item in line:
            if not first: lineString += csvSEP
            else: first = False
            if convertToStr: item = str(item)
            if removeLineBreakss: item = removeLineBreaks(item)
            if replaceSeparatorInCells: item = item.replace(csvSEP, CSV_SEP_SAFE)
            lineString += item
        if noEmptyLastLine and i == len(data) - 1: csvFile.write(lineString)
        else: csvFile.write(lineString + "\n")
    csvFile.close()


################################################################################
def readCSV(filePath, csvSEP=";", hasHeaders=True, encoding="utf-8"):
    try:
        f = open(filePath, "r", encoding=encoding)
        reader = csv.reader(f, delimiter=csvSEP)
        rows = []
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                if hasHeaders: continue
            rows.append(row)
        return rows
    except:
        return []


###################################################################################
def formatException(e):
    return str(e).replace("\n", "////")


################################################################################
def dictionnaryDeepGet(dic, *keys, default=None):
    for key in keys:
        if isinstance(dic, dict): dic = dic.get(key, default)
        else: return default
    return dic


################################################################################
def dictionnaryDeepSet(dic, value, *keys):
    for key in keys[:-1]: dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


################################################################################
def compressString(string, asString=False):
    compressed = zlib.compress(string.encode("utf8"))
    if asString: compressed = binascii.hexlify(compressed)
    return compressed


################################################################################
def decompressString(string, asString=False):
    if asString: string = binascii.unhexlify(string)
    return zlib.decompress(string).decode("utf8")


################################################################################
def getDateTimeFromTimestamp(timestamp, timezone):
    return datetime.datetime.fromtimestamp(timestamp, tz=dateutil.tz.gettz(timezone))


################################################################################
def parseDate(dateString, dateFormat, timezone=SERVER_TIMEZONE):
    if not timezone: return arrow.get(dateString, dateFormat).timestamp
    else: return arrow.get(dateString, dateFormat).replace(tzinfo=dateutil.tz.gettz(timezone)).timestamp


################################################################################
def parseBool(theBool, defaultValue=False, trueValue="true"):
    try:
        if theBool == trueValue: return True
        else: return False
    except:
        return defaultValue


################################################################################
def formatTimestamp(timestamp, dateFormat, timezone=SERVER_TIMEZONE):
    if dateFormat == "iso": return arrow.get(timestamp).to(timezone).isoformat()
    return arrow.get(timestamp).to(timezone).format(dateFormat)


################################################################################
def getDaysList(dayFromTS, dayToTS, timezone):
    dayFrom = getDateTimeFromTimestamp(dayFromTS, timezone)
    dayTo = getDateTimeFromTimestamp(dayToTS, timezone)
    dateTimes, days, daysIndexes, naiveDateTimes = [], [], {}, []
    index = 0
    for currentDayArrow in arrow.Arrow.range("day", dayFrom, dayTo):
        currentDay = int(currentDayArrow.strftime('%Y%m%d'))
        days.append(currentDay)
        dateTimes.append(currentDayArrow.date())
        naiveDateTimes.append(currentDayArrow.naive)
        daysIndexes[currentDay] = index
        index += 1
    return days, daysIndexes, dateTimes, naiveDateTimes


################################################################################
def makeKeyFromArguments(*args):
    return "--".join(str(arg) for arg in args)


################################################################################
def makePath(*args):
    args = [arg.rstrip("/") for arg in args]
    return '/'.join(str(x) for x in args)


################################################################################
def makeDir(path):
    if not os.path.isdir(path): os.makedirs(path)
    return path


###############################################################################
def makeDirPath(*args):
    return makeDir(makePath(*args))


################################################################################
def now():
    return arrow.now().timestamp


################################################################################
def parseInt(intString, defaultValue):
    try:
        return int(intString)
    except ValueError:
        return defaultValue


################################################################################
def delete(fileOrFolder):
    if os.path.exists(fileOrFolder):
        if os.path.isfile(fileOrFolder): os.remove(fileOrFolder)
        else: shutil.rmtree(fileOrFolder)


################################################################################
def listDirectoryItems(folder, onlyFiles=False, omitHiddenFiles=True, forbbidenItems=None):
    if forbbidenItems is None: forbbidenItems = {}

    def validItem(folder, file):
        if onlyFiles and not isfile(makePath(folder, file)): return False;
        if omitHiddenFiles and file.startswith("."): return False;
        if file in forbbidenItems: return False
        return True

    return [makePath(folder, f) for f in sorted(listdir(folder)) if validItem(folder, f)]


################################################################################
def clean(string):
    return re.compile("[^A-Za-z0-9\-]").sub("", string.replace(" ", "-"))


################################################################################
def floatFormat(number, decimals=2, fast=True):
    if decimals == 0: return "%d" % number
    else:
        if fast: return '%.*f' % (decimals, number)
        else: return ("{:.%sf}" % decimals).format(round(number, ndigits=decimals))


################################################################################
def encode(s):
    return str(base64.b64encode(s.encode('utf-8')), encoding="utf-8")


################################################################################
def decode(b):
    return str(base64.b64decode(b), encoding="utf-8")


################################################################################
def urlEncode(path):
    return urllib.parse.quote(path).replace("%3D", "=").replace("%3A", ":").replace("%2F", "/")


################################################################################
def getLastExceptionAndTrace():
    return traceback.format_exc(), traceback.format_stack()


################################################################################
def getFileSize(filePath):
    if not os.path.exists(filePath): return 0
    return os.path.getsize(filePath)


################################################################################
def getFileModified(filePath):
    if not os.path.exists(filePath): return 0
    return os.path.getmtime(filePath)


################################################################################
def getLockShared(filePath, waitForUnlockInSecs=None):
    try:
        f = open(filePath, "w")
        portalocker.lock(f, portalocker.LOCK_SH | portalocker.LOCK_NB)
        return f
    except:
        if waitForUnlockInSecs is not None:
            time.sleep(waitForUnlockInSecs)
            return getLockExclusive(filePath, waitForUnlockInSecs=None)
        else: return None


################################################################################
def getLockExclusive(filePath, waitForUnlockInSecs=None):
    try:
        f = open(filePath, "w")
        portalocker.lock(f, portalocker.LOCK_EX | portalocker.LOCK_NB)
        return f
    except:
        if waitForUnlockInSecs is not None:
            time.sleep(waitForUnlockInSecs)
            return getLockExclusive(filePath, waitForUnlockInSecs=None)
        else: return None


################################################################################
def releaseLock(lockHandler):
    if lockHandler is None: return
    portalocker.unlock(lockHandler)


################################################################################
def loadJsonFile(filePath):
    if not os.path.exists(filePath): raise Exception("The json file does not exists", filePath)
    try:
        return json.loads(open(filePath).read())
    except: raise Exception("The json file syntax is not valid", filePath)


################################################################################
def writeJsonFile(filePath, dictionnary, sortKeys=False, indent=4, compact=False):
    try:
        fp = open(filePath, "w")
        if compact: separators = (",", ":")
        else: separators = None
        json.dump(dictionnary, fp, sort_keys=sortKeys, indent=indent, separators=separators)
        fp.close()
    except:
        raise Exception("The json object could not be saved to file", filePath)


################################################################################
def cleanURL(url):
    return url.replace('//', '/', 1)


################################################################################
def getUserID(user):
    try: return pwd.getpwnam(user).pw_uid
    except: return None


################################################################################
def changeFileOwner(path, uid=-1, gid=-1):
    if os.path.exists(path):
        os.chown(path, uid, gid)


################################################################################
def updateQueryParams(url, params):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)


###################################################################################
def cleanPath(path):
    return path.lstrip("/").rstrip("/").replace('//', '/', 1)


################################################################################
def groupItemsByKey(items, keyFunction):
    itemsDict = OrderedDict()
    itemsWithIndexesDict = OrderedDict()
    for index in range(len(items)):
        item = items[index]
        itemKey = keyFunction(item)
        if not itemKey in itemsDict: itemsDict[itemKey] = []
        if not itemKey in itemsWithIndexesDict: itemsWithIndexesDict[itemKey] = []
        itemsDict[itemKey].append(item)
        itemsWithIndexesDict[itemKey].append({"item": item, "index": index})
    return itemsDict, itemsWithIndexesDict


################################################################################
def getYearMonthDayFromTimestamp(timestamp, timezone=SERVER_TIMEZONE):
    tsDateTime = datetime.datetime.fromtimestamp(timestamp, tz=dateutil.tz.gettz(timezone))
    return 10000 * tsDateTime.year + 100 * tsDateTime.month + tsDateTime.day


################################################################################
def getURLParams(url):
    try: return dict(parse.parse_qsl(parse.urlsplit(url).query))
    except: return {}
