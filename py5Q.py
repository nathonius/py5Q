import requests
import json
from Zones import ZoneList, Zone
from Endpoints import EndpointList
from Sessions import Session


class py5Q:
    """Main class. Handles creating the session and creating signals."""
    def __init__(self, mode="remote", port=27301, clientId=None, clientSecret=None, authMode="secret"):
        self.endpoints = EndpointList(mode, port)
        self.session = Session(clientId, clientSecret, self.endpoints.auth, mode=authMode)
        self.zones = self._getZones()

    def _getZones(self):
        """Returns a list of Zone objects"""
        zones = ZoneList()
        r = requests.get(self.endpoints.zones, headers=self._getHeaders())
        try:
            jsonZones = json.loads(r.content)
        except TypeError:
            jsonZones = json.loads(r.content.decode('utf-8'))
        for jsonZone in jsonZones:
            zones.append(Zone(jsonZone["id"], jsonZone["code"], jsonZone["name"]))
        return zones

    def _doSignal(self, zone, color, name, effect, message, action, shouldNotify, isRead, isArchived, isMuted):
        data = {
            "pid": "DK5QPID",
            "name": name,
            "zoneId": str(zone),
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
                          headers=self._getHeaders(), json=data)
        try:
            return json.loads(r.content)["id"]
        except TypeError:
            return json.loads(r.content.decode('utf-8'))["id"]

    def _getHeaders(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(self.session.token)
        }

    def signal(self, zone, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None, shouldNotify=None,
               isRead=None, isArchived=None, isMuted=None):
        return self._doSignal(zone, color, name, effect, message, action, shouldNotify, isRead, isArchived, isMuted)

    def batchSignal(self, zones, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None,
                    shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for zone in zones:
            signals.append(self._doSignal(zone, color, name, effect, message,
                                          action, shouldNotify, isRead, isArchived, isMuted))
        return signals

    def batchSignalRange(self, x, y, color, name="pyQ Signal", effect="SET_COLOR", message=None, action=None,
                         shouldNotify=None, isRead=None, isArchived=None, isMuted=None):
        signals = []
        for i in range(x[0], x[1] + 1):
            for j in range(y[0], y[1] + 1):
                signals.append(self._doSignal("{0},{1}".format(i, j), color, name=name, effect=effect, message=message,
                               action=action, shouldNotify=shouldNotify, isRead=isRead, isArchived=isArchived,
                               isMuted=isMuted))
        return signals

    def archive(self, signalId):
        data = {
            "isArchived": True
        }
        return requests.patch("{0}/{1}".format(self.endpoints.signals, signalId), headers=self._getHeaders(), json=data)

    def delete(self, signalId):
        return requests.delete("{0}/{1}".format(self.endpoints.signals, signalId), headers=self._getHeaders())

    def deleteAll(self):
        shadow = self.getShadow()
        for signal in shadow["content"]:
            self.delete(signal["id"])

    def getShadow(self):
        r = requests.get(self.endpoints.shadow, headers=self._getHeaders())
        try:
            return json.loads(r.content)
        except TypeError:
            return json.loads(r.content.decode('utf-8'))
