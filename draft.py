import http.client
import xml.dom.minidom as mdom

base_url='fritz.box'

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def getSessionID(base_url):
    sid = None
    challenge = None
    #ask for new sid
    conn = http.client.HTTPConnection(base_url)
    conn.request('GET', '/login_sid.lua')
    response = conn.getresponse()
    if response.status == 200:
        resp_content = response.read()
        #read result
        dom = mdom.parseString(resp_content)
        # add assert
        sessioninfo = dom.getElementsByTagName('SessionInfo')[0]
        sid = sessioninfo.getElementsByTagName('SID')[0].firstChild.nodeValue
        challenge = sessioninfo.getElementsByTagName('Challenge')[0].firstChild.nodeValue

    return {sid, challenge}


def doThings():
    print ("hallo")


if __name__ == '__main__':
    # set sesion is
    # use sesionid for calls
    sid, challenge = getSessionID(base_url)
    print(sid)
    print(challenge)