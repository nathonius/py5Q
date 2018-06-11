import random

BADZONES = [0, 18, 19, 20, 21]


class ZoneList(list):
    """
    A list of zones. Each zone is accessible by id, code, name, and coordinates
    Coordinates can be in "x,y" form or as an (x, y) tuple/list.
    """
    def __getitem__(self, key):
        # Handle tuple
        if hasattr(key, '__iter__') and len(key) == 2 and isinstance(key[0], int) and isinstance(key[1], int):
            return super(ZoneList, self).__getitem__(self.index("{0},{1}".format(key[0], key[1])))
        return super(ZoneList, self).__getitem__(self.index(key))

    def getRange(self, x, y):
        zones = ZoneList()
        for i in range(x[0], x[1] + 1):
            for j in range(y[0], y[1] + 1):
                try:
                    zone = self["{0},{1}".format(i, j)]
                except ValueError:
                    continue
                zones.append(zone)
        return zones

    @property
    def numpad(self):
        return self.getRange((19, 22), (1, 5))

    @property
    def function(self):
        return self.getRange((3, 15), (0, 0))

    @property
    def arrows(self):
        return ZoneList((self["17,4"], self["16,5"], self["17,5"], self["18,5"]))

    @property
    def pipes(self):
        return ZoneList((self[0], self["23,1"]))

    @property
    def random(self):
        return super(ZoneList, self).__getitem__(random.randint(0, len(self) - 1))


class Zone:
    """Represents a single zone/key."""
    def __init__(self, zoneId, zoneCode, zoneName):
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
        # Handle left pipe
        if isinstance(other, str) and str(other).startswith("0,"):
            return self.zoneCoordX == 0 and self.zoneCoordY == 0
        # Handle right pipe
        elif isinstance(other, str) and str(other).startswith("23,") and self.zoneCoordY != 0:
            return self.zoneCoordX == 23 and self.zoneCoordY == 1
        else:
            return other == self.zoneId or other == self.zoneCode or other == self.zoneName or other == self.zoneCoords

    def __str__(self):
        return self.zoneCode

    def __repr__(self):
        return self.zoneCode
