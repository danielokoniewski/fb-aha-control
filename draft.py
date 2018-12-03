import time
import hashlib
import sys
import http.client
import urllib.parse
import xml.dom.minidom as mdom

base_url='fritz.box'

def readLoginResponse(responseText):
    sid = None
    challenge = None
    blocktime = 0
    dom = mdom.parseString(responseText)
    # add assert
    sessioninfo = dom.getElementsByTagName('SessionInfo')[0]
    sid = sessioninfo.getElementsByTagName('SID')[0].firstChild.nodeValue
    challenge = sessioninfo.getElementsByTagName('Challenge')[0].firstChild.nodeValue
    blocktime = sessioninfo.getElementsByTagName('BlockTime')[0].firstChild.nodeValue
    return {'sid':sid, 'challenge':challenge, 'blocktime': blocktime}


def getChallenge(base_url):
    sid = None
    challenge = None
    #ask for new sid
    conn = http.client.HTTPConnection(base_url)
    conn.request('GET', '/login_sid.lua')
    response = conn.getresponse()
    if response.status == 200:
        resp_content = response.read()
        res = readLoginResponse(resp_content)
        challenge = res['challenge']
        # wait bock time
        blocktime = int(res['blocktime'])
        time.sleep(blocktime/1000.0)
    return challenge

def getResponse(challenge, password):
    bstring = '-'.join([challenge, password]).encode('utf-16le')
    bstringHash = hashlib.md5(bstring).hexdigest()
    response = '-'.join([challenge,bstringHash])
    return response

def getSessionID(base_url, username, password):
    sid = None
    challenge = getChallenge(base_url)
    response = getResponse(challenge, password)
    conn = http.client.HTTPConnection(base_url)
    params = urllib.parse.urlencode({'username':username, 'response':response})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn.request('POST', '/login_sid.lua', params, headers )
    response = conn.getresponse()
    if response.status == 200:
        response_text = response.read()
        res= readLoginResponse(response_text)
        sid=res['sid']
    return sid

def runGetCommand(paramList):
    #"http://fritz.box/home/home.lua?sid=<sid>"
    #https: // fritz.box / webservices / homeautoswitch.lua?ain = 012340000123 & switchcmd = setswitchon & sid = 9c977765016899f8
    conn = http.client.HTTPConnection(base_url)
    params = urllib.parse.urlencode(paramList)
    conn.request(method='GET', url='/webservices/homeautoswitch.lua?'+params)
    response = conn.getresponse()
    text=''
    if response.status == 200:
        text = response.read().decode('utf-8')

    return {response.status, text}

def doThings(sid):
    paramList = {'switchcmd': 'getswitchlist', 'sid': sid}
    status, text = runGetCommand(paramList)
    print(status, text)

    if status == 200:
        for ain in text.replace("\n",'').split(','):
            paramList = {'switchcmd': 'getswitchname', 'sid': sid, 'ain':ain}
            print(runGetCommand(paramList))

def setOn(sid, ain):
    paramList = {'switchcmd': 'setswitchon', 'sid': sid, 'ain':ain}
    status, text = runGetCommand(paramList)
    print(status, text)

def setOff(sid, ain):
    paramList = {'switchcmd': 'setswitchoff', 'sid': sid, 'ain':ain}
    status, text = runGetCommand(paramList)
    print(status, text)

def getTemp(sid, ain):
    paramList = {'switchcmd': 'gettemperature', 'sid': sid, 'ain': ain}
    status, text = runGetCommand(paramList)
    if status == 200:
        print('temp: {0} °C'.format(float(text)/10.0))
    else:
        print('error #{0}'.format(status))


def logout(sid):
    conn = http.client.HTTPConnection(base_url)
    params = urllib.parse.urlencode({'logout': 1, 'sid': sid})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn.request('POST', '/login_sid.lua', params, headers)
    response = conn.getresponse()


if __name__ == '__main__':
    # set sesion is
    # use sesionid for calls
    sid = getSessionID(base_url, username=sys.argv[1] , password=sys.argv[2])
    print(sid)
    #doThings(sid)
    getTemp(sid, sys.argv[3])
    logout(sid)