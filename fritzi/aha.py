import hashlib
import http.client
import urllib.parse
import xml.dom.minidom as mdom


class ahaC:
    """fritz Box aha client"""

    _session = None

    def __init__(self, username, password, host = 'fritz.box'):
        self._session = ahaSession(host, username, password)

    def runCommand(self, param = None):
        paramList = {'sid' : self._session.sid}
        if param is not None:
            paramList.update(param)
        params = urllib.parse.urlencode(paramList)
        conn = http.client.HTTPConnection(self._session.host)
        conn.request(method='GET', url='/webservices/homeautoswitch.lua?' + params)
        response = conn.getresponse()
        text = None
        if response.status == 200:
            text = response.read().decode('utf-8')

        return text

    def setSwitchOn(self, ain):
        paramList = {'switchcmd': 'setswitchon', 'ain':ain}
        text = self.runCommand(paramList)
        print(text)

    def setSwitchOff(self, ain):
        paramList = {'switchcmd': 'setswitchoff', 'ain':ain}
        text = self.runCommand(paramList)
        print(text)



class ahaSession:
    """Class to provide a session, login and logoff"""

    sid = ''
    host = ''

    def __init__(self, host, username, password):
        self.host = host
        self.sid = self.login(username, password)

    def login(self, username, password):
        """authenticate and create a new session"""
        sid = ''
        challenge = self.runCommand()['challenge']
        secret = self.createLoginSecret(password, challenge)
        sid = self.runCommand({'username': username, 'response': secret})['sid']
        return sid

    def createLoginSecret(self, password, challenge):
        """creates the secret to authenticate against a fritzbox login.lua"""
        hashv = '{0}-{1}'.format(challenge, password).encode('utf-16le')
        hashs = hashlib.md5(hashv).hexdigest()
        secret = '{0}-{1}'.format(challenge, hashs)
        return secret

    def __del__(self):
        """logoff on destruct"""

    def runCommand(self, param = None):
        """runs a command with get parameters"""
        paramList = {'sid': self.sid}
        params = ''
        if param is not None:
            paramList.update(param)
            params = urllib.parse.urlencode(paramList)
        conn = http.client.HTTPConnection(self.host)
        conn.request('GET', '/login_sid.lua?' + params)
        response = conn.getresponse()
        if response.status == 200:
            resp_content = response.read().decode('utf-8')
            res = self.readLoginResponse(resp_content)
        return res

    def readLoginResponse(self,responseText):
        sid = None
        challenge = None
        blocktime = 0
        dom = mdom.parseString(responseText)
        # add assert
        sessioninfo = dom.getElementsByTagName('SessionInfo')[0]
        sid = sessioninfo.getElementsByTagName('SID')[0].firstChild.nodeValue
        challenge = sessioninfo.getElementsByTagName('Challenge')[0].firstChild.nodeValue
        blocktime = sessioninfo.getElementsByTagName('BlockTime')[0].firstChild.nodeValue
        return {'sid': sid, 'challenge': challenge, 'blocktime': blocktime}