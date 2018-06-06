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


class EndpointList:
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
    def __init__(self, clientId, secret, endpoint, mode="secret"):
        self._endpoint = endpoint
        self._clientId = clientId
        tokens = self.authenticate(clientId, secret, mode)
        self.updateTokens(tokens)

    @property
    def token(self):
        if(time.time() > self._expiresAt):
            self.refreshToken()
        return self._accessToken

    def updateTokens(self, tokens):
        self._accessToken = tokens["access_token"]
        self._refreshToken = tokens["refresh_token"]
        self._userId = tokens["user_id"]
        self._expiresAt = time.time() + tokens["expires_in"] - 1000

    def authenticate(self, clientId, secret, mode):
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
    def __init__(self, mode="remote", port=27301, clientId=CLIENTID, secret=CLIENTSECRET):
        self.endpoints = EndpointList(mode, port)
        self.session = QSession(clientId, secret, self.endpoints.auth)
    
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
        r = requests.post(self.endpoints.signals, headers=self.getHeaders(), json=data)
        try:
            return json.loads(r.content)["id"]
        except TypeError:
            return json.loads(r.content.decode('utf-8'))["id"]
    
    def batchSignal(self, zones, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None, shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for zone in zones:
            signals.append(self.signal(zone, color, name, effect, message, action, shouldNotify, isRead, isArchived, isMuted))
        return signals
    
    def batchSignalRange(self, x, y, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None, shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for i in range(x[0], x[1]+1):
            for j in range(y[0], y[1]+1):
                signals.append(self.signal("{0},{1}".format(i, j), color, name=name, effect=effect, message=message, action=action, shouldNotify=shouldNotify, isRead=isRead, isArchived=isArchived, isMuted=isMuted))
        return signals
    
    def archive(self, signalId):
        data = {
            "isArchived": True
        }
        return requests.patch("{0}/{1}".format(self.endpoints.signals, signalId), headers=self.getHeaders(), json=data)
    
    def delete(self, signalId):
        return requests.delete("{0}/{1}".format(self.endpoints.signals, signalId), headers=self.getHeaders())