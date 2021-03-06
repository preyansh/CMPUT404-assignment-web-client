#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust , Preyanshu Kumar, Ryan Satyabrata
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # If address doesnt have a port, handle this case, e.g. check for ":" in url
        # cuz getRootUrl only returns the IP and NOT port. i cutt of the port
        urlRootPort = self.splitPortUrl(url)
        if(len(urlRootPort) == 2 and urlRootPort[1]!=""):
            return int(urlRootPort[1])
        else:
            return 80
    
    def connect(self, host, port):
        # Using Sockets from the OS to make clients. From Lab2
        # socket.AF_INET means use this socket to communicate to the internet
        # socket.SOCK_STREAM means we want to use TCP!
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host, port))
        return clientSocket

    def get_code(self, data):
        # Extract the code from the HTTP/1.1 xxx ????
        return int(data.split(" ")[1])

    def get_headers(self,data):
        # extract the response body, splits by CR+LF then joins the latter half.
        return "".join(data.split("\r\n\r\n")[0])

    def get_body(self, data):
        # extract the response body, splits by CR+LF then joins the latter half.
        return "".join(data.split("\r\n\r\n")[1:])

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def splitUrl(self, str):
        stringy = str.split("/")
        # Skip http: / _ /
        if(stringy[0].lower()=="http:"):
            return stringy[2:]
        return stringy
        
    # if ":" was found, returns a list of length 2, otherwise returns the string of the str.
    def splitPortUrl(self, str):
        parsed = self.splitUrl(str)
        if(":" in parsed[0]):
            return parsed[0].split(":")
        return [parsed[0], ""]
        
    def getRootUrl(self, url):
        return self.splitPortUrl(url)[0]
        
    def getLocUrl(self,url):
        parsed = self.splitUrl(url)
        return "/" + "/".join(parsed[1:])
        
    def GET(self, url, args=None):
        urlRoot= self.getRootUrl(url)
        urlPort = self.get_host_port(url)
        urlLoc = self.getLocUrl(url)
        clientSock = self.connect(urlRoot,urlPort)
        urlArgs = ""
        if (args!=None):
            if(urlLoc[-1] == "/"):
                urlLoc = urlLoc[0:-1]
            urlArgs= "?" + urllib.urlencode(args)
        getHTTPHost = "GET " +urlLoc+urlArgs+" HTTP/1.1\r\nHost: " + urlRoot+"\r\n\r\n"
        clientSock.sendall(getHTTPHost)
        response = self.recvall(clientSock)
        code = self.get_code(response)
        body = self.get_body(response)
        print(response)
        return HTTPResponse(code, body)
        
    def POST(self, url, args=None):
        urlRoot = self.getRootUrl(url)
        urlPort = self.get_host_port(url)
        urlLoc = self.getLocUrl(url)
        clientSock = self.connect(urlRoot, urlPort)
        postHttpHost = "POST " + urlLoc + " HTTP/1.1\r\nHost: " + urlRoot + "\r\n"
        argsEncoded = ""
        if(args != None):
            argsEncoded = urllib.urlencode(args)
        contTyp = "content-type: application/x-www-form-urlencoded\r\n"
        # contLen = "content-length: " + str(sys.getsizeof(argsEncoded)) + "\r\n"
        contLen = "content-length: " + str(len(argsEncoded)) + "\r\n"
        toSend = postHttpHost + contLen + contTyp + "\r\n" + argsEncoded + "\r\n\r\n"
        clientSock.sendall(toSend);
        response = self.recvall(clientSock)
        code = self.get_code(response)
        body = self.get_body(response)
        print(response)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        httpResponse = client.command( sys.argv[2], sys.argv[1] )
        print(httpResponse)
    else:
        print client.command( sys.argv[1] )
