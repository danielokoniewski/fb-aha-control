import sys
from fritzi import aha


if __name__ == '__main__':
    # set sesion is
    # use sesionid for calls
    fritz = aha.ahaC(username=sys.argv[1] , password=sys.argv[2])
    if sys.argv[3] == 'on':
        for ain in sys.argv[4].split(','):
            fritz.setSwitchOn(ain)
    elif sys.argv[3] == 'off':
        for ain in sys.argv[4].split(','):
            fritz.setSwitchOff(ain)