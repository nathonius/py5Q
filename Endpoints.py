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
SHADOW = "{0}/api/1.0/signals/shadows/DK5QPID"


class EndpointList:
    """Keeps all endpoints, sets them to be local or remote."""
    def __init__(self, mode, port):
        if mode != "remote":
            source = LOCAL.format(str(port))
        else:
            source = REMOTE

        self.auth = None
        self.signals = SIGNALS.format(source)
        self.authorized_clients = None
        self.device_definitions = None
        self.devices = None
        self.colors = None
        self.zones = None
        self.effects = None
        self.shadow = None

        if mode is "remote":
            self.auth = AUTH.format(source)
            self.authorized_clients = AUTHORIZED_CLIENTS.format(source)
            self.device_definitions = DEVICE_DEFINITONS.format(source)
            self.devices = DEVICES.format(source)
            self.colors = COLORS.format(source)
            self.zones = ZONES.format(source)
            self.effects = EFFECTS.format(source)
            self.shadow = SHADOW.format(source)
