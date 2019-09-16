import socket
import time
import sys
from requests import get
import datetime
import uuid

def getLocalIP():
    try:
        hostName = socket.gethostname()
        localIP = socket.gethostbyname(hostName)
        # print("Local IP retrieved")
        return localIP
    except:
        print("Unable to get local IP")
        return None
    
def getExternalIP():
    try:
        externalIP = get('https://api.ipify.org').text
        # print("External IP retieved")
        return externalIP
    except:
        print("Unable to get external IP")
        
def getMacAddress():
    macAddress = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
    for ele in range(0,8*6,8)][::-1])
    return macAddress
 
def checkInternet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        # print("Connected")
        return True
    except:
        print(ex)
        return False
    
isConnected = checkInternet()
connectionTryCount = 0

while isConnected != True:
    time.sleep(5)
    connectionTryCount += 1
    print("Connection Attempt: " + str(connectionTryCount))
    isConnected = checkInternet()
    print(isConnected)
    
    if connectionTryCount == 10:
        print("Failed to Connect")
        sys.exit("Failed to Connect")

piID = 1
deviceName = socket.gethostname()
localIP = getLocalIP()
externalIP = getExternalIP()
macAddress = getMacAddress()
LotID = 1
FloorNumber = 1
UpdateDate = datetime.datetime.now()

print(str(piID) + " " + deviceName + " " + str(localIP) + " " + str(externalIP) + " " + str(macAddress) + " " + str(UpdateDate))