#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from threading import Thread
from time import sleep
import os
import requests
import click

from collect import get_info

host = "localhost"
port = 8080
url = "http://" + str(host) + ":" + str(port)

serverOnly = False

info = {}#get_info()
files = {}

def readFiles():
    ld = os.listdir('www')
    for fn in ld:
        if fn[-1] != b'~':
            with open('www/{}'.format(fn), 'rb') as f:
                files[fn] = f.read()

def getHeader(fname):
    ext = fname.split(b'.')[-1]
    if ext == 'ico':
        return 'image/x-icon'
    if ext == 'css':
        return 'text/html'
    if ext == 'js':
        return 'text/javascript'
    return 'text/html'

class InfoPoller(Thread):
    def __init__(self, period):
        Thread.__init__(self)
        self.period = period
        self.stopped = False
    def get(self):
        global info
        info = get_info()
        try:
            x = requests.post(url, json=info)
            info['con'] = (x == 200)
        except:
            info['con'] = False
        #print(x.text)
        #print(info)
    def stop(self):
        self.stopped = True
    def run(self):
        while not self.stopped:
            sleep(self.period)
            self.get()


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip('/')
        if path == 'info.json':
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif path in files:
            self.send_response(200)
            self.send_header("Content-type", getHeader(files[path]))
            self.end_headers()
            self.wfile.write(files[path])
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b'<html><head><title>Info</title></head><body>')
            self.wfile.write(bytes('<p>Request: %s</p>' % self.path, 'utf-8'))
            self.wfile.write(b'</body></html>')
    def do_POST(self):
        path = self.path.strip('/')
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            data = json.loads(post_data)
            self.wfile.write('OK'.encode('utf-8'))
        except json.decoder.JSONDecodeError:
            data = None
            self.wfile.write('ERROR'.encode('utf-8'))
            print("Decode error: {}".format(post_data))
        if data is not None:
            if serverOnly:
                print(json.dumps(data, indent=2))


@click.command()
@click.option('--server', is_flag=True, default=False, help='Run server part only (no local data aquisition).')
def run(server):
    global serverOnly
    serverOnly = server
    if serverOnly:
        print('Run server only (no local data aquisition).')
        url = "http://192.168.1.108:" + str(port)

    global info

    readFiles()

    if not serverOnly:
        info = get_info()
        infoPoller = InfoPoller(5.0)
        infoPoller.start()
    else:
        global host
        host = '0.0.0.0'

    webServer = HTTPServer((host, port), MyServer)
    print("Server started http://%s:%s" %(host, port))

    try:
        webServer.serve_forever()
    except Exception as exc:
        print("Caught: {}: {}".format(exc.__class__.__name__, exc))

    webServer.server_close()
    if not serverOnly:
        infoPoller.stop()

    print("Server stopped")


if __name__ == "__main__":
    run()
