import time
import requests
import json
import os

CONFIGPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
TOKENCACHEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tokens.json")


class Session:
    """Gets OAuth token and automatically refreshes token when needed"""
    def __init__(self, clientId, secret, endpoint, mode, cacheTokens=True):
        self._cacheTokens = cacheTokens
        self._endpoint = endpoint
        self._clientId = clientId
        tokens = self.authenticate(clientId, secret, mode)
        if tokens:
            self.updateTokens(tokens)

    @property
    def token(self):
        """Get the token, unless it has expired. Then, get a new token."""
        if(time.time() > self._expiresAt):
            self.refreshToken()
        return self._accessToken

    def updateTokens(self, tokens, cache=True):
        """Set properties from server response."""
        self._accessToken = tokens["access_token"]
        self._refreshToken = tokens["refresh_token"]
        self._userId = tokens["user_id"]
        if "expires_in" in tokens.keys():
            self._expiresAt = time.time() + tokens["expires_in"] - 1000
        elif "expires_at" in tokens.keys():
            self._expiresAt = tokens["expires_at"]

        # Save tokens
        if self._cacheTokens and cache:
            with open(TOKENCACHEPATH, 'w') as tokenFile:
                tokens = {"access_token": self._accessToken, "refresh_token": self._refreshToken,
                          "user_id": self._userId, "expires_at": self._expiresAt}
                json.dump(tokens, tokenFile)

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

        # Check for existing access/refresh tokens. Does not work with email + password auth.
        if self._cacheTokens:
            with open(TOKENCACHEPATH, 'r') as tokenFile:
                tokens = json.load(tokenFile)
                # token is still valid
                if "expires_at" in tokens.keys() and time.time() < tokens["expires_at"]:
                    self.updateTokens(tokens, cache=False)
                    return None
                # use refresh token
                elif "refresh_token" in tokens.keys():
                    self.refreshToken(clientId=clientId, refreshToken=tokens["refresh_token"])
                    return None

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
        if r.status_code != 200:
            raise AuthenticationException("Response Code: {0}".format(r.status_code), r.content)
        try:
            return json.loads(r.content)
        except TypeError:
            return json.loads(r.content.decode('utf-8'))

    def refreshToken(self, clientId=None, refreshToken=None):
        if not clientId:
            clientId = self._clientId
        if not refreshToken:
            refreshToken = self._refreshToken
        data = {
            "client_id": clientId,
            "refresh_token": refreshToken,
            "grant_type": "refresh_token"
        }
        tokens = self.getTokens(data)
        self.updateTokens(tokens)


class AuthenticationException(Exception):
    pass
