import requests
import json
import time

LOCAL = "http://localhost:{0}"
REMOTE = "https://q.daskeyboard.com"

AUTH = "{0}/oauth/1.4/token"
SIGNALS = "{0}/api/1.0/signals"
AUTHORIZED_CLIENTS = "{0}/api/1.0/users/authorized_clients"
DEVICE_DEFINITONS = "{0}/api/1.0/device_definitions"
DEVICES = "{0}/api/1.0/devices"
COLORS = "{0}/api/1.0/colors"
ZONES = "{0}/api/1.0/DK5QPID/zones"
EFFECTS = "{0}/api/1.0/DK5QPID/effects"

CLIENTID = "YOUR_ID"
CLIENTSECRET = "YOUR_SECRET"

BADZONES = [0, 18, 19, 20, 21]


class Zone:
    """Represents a single zone/key."""
    def __init__(self, zoneId, zoneCode, zoneName):
        print(zoneId)
        self.zoneId = zoneId
        self.zoneCode = zoneCode
        self.zoneName = zoneName
        if zoneId not in BADZONES:
            self.zoneCoordX = zoneId % 24
            self.zoneCoordY = (zoneId - 24) // 24
        elif zoneId != 0:
            tempId = zoneId + 25
            self.zoneCoordX = tempId % 24
            self.zoneCoordY = (tempId - 24) // 24
        else:
            self.zoneCoordX = 0
            self.zoneCoordY = 0
        self.zoneCoords = "{0},{1}".format(self.zoneCoordX, self.zoneCoordY)
    
    def __eq__(self, other):
        if isinstance(other, str) and str(other).startswith("0,"):
            return self.zoneId == 0
        return other == self.zoneId or other == self.zoneCode or other == self.zoneName or other == self.zoneCoords

    def __str__(self):
        return self.zoneId


class EndpointList:
    """Keeps all endpoints, sets them to be local or remote."""
    def __init__(self, mode, port):
        if mode != "remote":
            source = LOCAL.format(str(port))
        else:
            source = REMOTE

        self.auth = AUTH.format(source)
        self.signals = SIGNALS.format(source)
        self.authorized_clients = AUTHORIZED_CLIENTS.format(source)
        self.device_definitions = DEVICE_DEFINITONS.format(source)
        self.devices = DEVICES.format(source)
        self.colors = COLORS.format(source)
        self.zones = ZONES.format(source)
        self.effects = EFFECTS.format(source)


class QSession:
    """Gets OAuth token and automatically refreshes token when needed"""
    def __init__(self, clientId, secret, endpoint, mode="secret"):
        self._endpoint = endpoint
        self._clientId = clientId
        tokens = self.authenticate(clientId, secret, mode)
        self.updateTokens(tokens)

    @property
    def token(self):
        """Get the token, unless it has expired. Then, get a new token."""
        if(time.time() > self._expiresAt):
            self.refreshToken()
        return self._accessToken

    def updateTokens(self, tokens):
        """Set properties from server response."""
        self._accessToken = tokens["access_token"]
        self._refreshToken = tokens["refresh_token"]
        self._userId = tokens["user_id"]
        self._expiresAt = time.time() + tokens["expires_in"] - 1000

    def authenticate(self, clientId, secret, mode):
        """ClientId + Secret auth is preferred"""
        if mode != "secret":
            return self.authenticateEmailPassword(clientId, secret)
        else:
            return self.authenticateClientSecret(clientId, secret)

    def authenticateClientSecret(self, clientId, secret):
        data = {
            "client_id": clientId,
            "client_secret": secret,
            "grant_type": "client_credentials"
        }
        return self.getTokens(data)

    def authenticateEmailPassword(self, email, password):
        data = {
            "email": email,
            "password": password,
            "grant_type": "password"
        }
        return self.getTokens(data)

    def getTokens(self, data):
        headers = {"Content-Type": "application/json"}
        r = requests.post(self._endpoint, json=data, headers=headers)
        try:
            return json.loads(r.content)
        except TypeError:
            return json.loads(r.content.decode('utf-8'))

    def refreshToken(self):
        data = {
            "client_id": self._clientId,
            "refresh_token": self._refreshToken,
            "grant_type": "refresh_token"
        }
        tokens = self.getTokens(data)
        self.updateTokens(tokens)


class pyQ:
    """Main class. Handles creating the session and creating signals."""
    def __init__(self, mode="remote", port=27301, clientId=CLIENTID, secret=CLIENTSECRET):
        self.endpoints = EndpointList(mode, port)
        self.session = QSession(clientId, secret, self.endpoints.auth)
        self.zones = self._getZones()

    def _getZones(self):
        """Returns a list of Zone objects"""
        zones = []
        r = requests.get(self.endpoints.zones, headers=self.getHeaders())
        try:
            jsonZones = json.loads(r.content)
        except TypeError:
            jsonZones = json.loads(r.content.decode('utf-8'))
        for jsonZone in jsonZones:
            zones.append(Zone(jsonZone["id"], jsonZone["code"], jsonZone["name"]))
        return zones

    def getHeaders(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(self.session.token)
        }

    def signal(self, zone, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None, shouldNotify=None,
               isRead=None, isArchived=None, isMuted=None):
        data = {
            "pid": "DK5QPID",
            "name": name,
            "zoneId": zone,
            "color": color,
            "effect": effect,
            "message": message,
            "action": action,
            "shouldNotify": shouldNotify,
            "isRead": isRead,
            "isArchived": isArchived,
            "isMuted": isMuted
        }
        r = requests.post(self.endpoints.signals,
                          headers=self.getHeaders(), json=data)
        try:
            return json.loads(r.content)["id"]
        except TypeError:
            return json.loads(r.content.decode('utf-8'))["id"]

    def batchSignal(self, zones, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None,
                    shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for zone in zones:
            signals.append(self.signal(zone, color, name, effect, message,
                                       action, shouldNotify, isRead, isArchived, isMuted))
        return signals

    def batchSignalRange(self, x, y, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None,
                         shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for i in range(x[0], x[1] + 1):
            for j in range(y[0], y[1] + 1):
                signals.append(self.signal("{0},{1}".format(i, j), color, name=name, effect=effect, message=message,
                                           action=action, shouldNotify=shouldNotify, isRead=isRead,
                                           isArchived=isArchived, isMuted=isMuted))
        return signals

    def archive(self, signalId):
        data = {
            "isArchived": True
        }
        return requests.patch("{0}/{1}".format(self.endpoints.signals, signalId), headers=self.getHeaders(), json=data)

    def delete(self, signalId):
        return requests.delete("{0}/{1}".format(self.endpoints.signals, signalId), headers=self.getHeaders())