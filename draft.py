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

def doThings(sid):
    #"http://fritz.box/home/home.lua?sid=<sid>"
    print ("hallo")


if __name__ == '__main__':
    # set sesion is
    # use sesionid for calls
    sid = getSessionID(base_url, username=sys.argv[1] , password=sys.argv[2])
    print(sid)