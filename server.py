#  coding: utf-8
import os  
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2023 Richeek Mathur
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        
        # Decode and split lines to read the request
        request = self.data.decode().splitlines()
        #print (request)
        request_line = request[0].split()
        
        # request_line is the first line of the request
        # request_line[1] is "/"
        path_requested = os.path.abspath("www" + request_line[1])

        # Accept only GET method/request
        # Otherwise return Error Code with Message : 405
        if not request_line[0] == "GET":
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n".encode())
            return

        # Should not be PUT, POST or DELETE
        # Otherwise return Error Code with Message : 405
        elif request_line[0] == "PUT" or request_line[0] == "POST" or request_line[0] == "DELETE":
            self.request.sendall("HTTP/1.1 405 Method Not Allowed\r\n".encode())
            return

        # Checking if the file is in Directory(www)
        # Otherwise return Error Code with Message : 404
        elif os.path.abspath("www") not in os.path.realpath(path_requested):
            self.request.sendall("HTTP/1.1 404 File Not Found\r\n".encode())
            return
        
        # Checking if valid based on HTTP Request
        # Otherwise return Error Code with Message : 404
        elif '..' in request_line[1]:
            self.request.sendall("HTTP/1.1 404 File Not Found\r\n".encode())
            return

      
        # Checking if "www" is a directory
        elif os.path.isdir("www" + request_line[1]):

            # If it is a directory, check if path ends in "/" 
            # Otherwise return Error Code with Message : 301          
            if not request_line[1] == "/":
                if not request_line[1][-1] == "/":
                    self.request.sendall("HTTP/1.1 301 Moved Permanently\r\n".encode())
                    request_line[1] = request_line[1] + "/"
                    self.request.sendall(('Location: http://127.0.0.1:8080' + request_line[1] + '\n' ).encode())
                    return

            # Check if the file ends with index.html (index.html is in the directory:www)        
            if not request_line[1].__contains__("index.html"):
                request_line[1] = request_line[1] + "index.html"        
       
       # Update the path_requested
        path_requested = os.path.abspath("www" + request_line[1])
       

       # Check if the path_requested is a file
       # Otherwise return Error Code with Message : 404
        if not os.path.isfile(path_requested) or not path_requested.startswith(os.path.abspath("www")):
            self.request.sendall("HTTP/1.1 404 File Not Found\r\n".encode())
            return

        
        # Open the file using the location(path) in read mode
        with open(path_requested, 'r') as file:
            # HTTP Response
            self.request.sendall("HTTP/1.1 200 OK\r\n".encode())
            
            # assigning mimetypes for html and css
            if path_requested.__contains__("html"):
                self.request.sendall("Content-type: text/html; charset=utf-8\r\n".encode())
            else:
                self.request.sendall("Content-type: text/css; charset=utf-8\r\n".encode())

            data = file.read().encode()
            self.request.sendall(("Content-Length: " + str(len(data)) + "\r\n\r\n").encode()+ data)
        


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Server is Starting.....")
    server.serve_forever()
