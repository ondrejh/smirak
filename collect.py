#!/usr/bin/python3

import subprocess
import socket
import os
import json
import uuid

#PS_CODING = 'cp1250'
#PS_CODING = 'utf-8'
PS_CODING = 'ascii'

def get_app_list():
    '''
    Get list of running windowed applications:
    https://stackoverflow.com/questions/54827918/get-list-of-running-windows-applications-using-python
    '''

    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Id,ProcessName,Description'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    applist = []
    cnt = 0
    procP = 0
    descP = 0
    for line in proc.stdout:
        lstr = line.rstrip()
        if lstr and lstr not in (b'Description', b'-----------'):
            if cnt == 0:
                procP = lstr.find(b'ProcessName')
                descP = lstr.find(b'Description')
            if cnt > 1:
                pid = int(lstr[:procP].strip().decode(encoding=PS_CODING, errors='ignore'))
                pname = lstr[procP:descP].strip().decode(encoding=PS_CODING, errors='ignore')
                pdesc = lstr[descP:].strip().decode(encoding=PS_CODING, errors='ignore')
                applist.append([pid, pname, pdesc])
            cnt += 1
    return applist

def get_mac():
    '''
    Get MAC address of the node:
    https://www.codespeedy.com/how-to-get-mac-address-of-a-device-in-python
    '''

    mac = uuid.getnode()
    mhex = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
    return mhex


def get_ip():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip

def get_username():
    user = os.getlogin()
    return user

def get_info():
    apps = get_app_list()
    ip = get_ip()
    mac = get_mac()
    user = get_username()
    info = {'user': user, 'ip': ip, 'mac': mac, 'apps': apps}
    return info

if __name__ == "__main__":
    info = get_info()
    print( json.dumps(info) )
