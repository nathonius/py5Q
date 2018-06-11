import time
import requests
import json
import os

CONFIGPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")


class Session:
    """Gets OAuth token and automatically refreshes token when needed"""
    def __init__(self, clientId, secret, endpoint, mode):
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

    def authenticate(self, clientId, clientSecret, mode):
        # Read from config file if no id/secret given
        if not clientId and not clientSecret:
            with open(CONFIGPATH, 'r') as configFile:
                config = json.load(configFile)
                if config["clientId"] != "" and config["clientSecret"] != "":
                    clientId = config["clientId"]
                    clientSecret = config["clientSecret"]
                    mode = "secret"
                elif config["username"] != "" and config["password"] != "":
                    clientId = config["username"]
                    clientSecret = config["password"]
                    mode = "password"

        # ClientId + Secret auth is preferred
        if mode != "secret":
            return self.authenticateEmailPassword(clientId, clientSecret)
        else:
            return self.authenticateClientSecret(clientId, clientSecret)

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
