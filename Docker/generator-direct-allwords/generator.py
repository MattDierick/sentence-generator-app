from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import urlparse
import cgi
import requests
import os

from random import seed
from random import randint


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
	parsed_path = urlparse.urlparse(self.path)
	print parsed_path
        self._set_headers()
	generated_name = name_generator()
	self.wfile.write(json.dumps(generated_name))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # add a property to the object, just to mess with data
        message['received'] = 'ok'
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message))

def name_generator():
	NAMESPACE = os.environ.get('NAMESPACE')
        gateway = '.svc.cluster.local'
	generated_name = {}
	attributes_list = ['adjectives', 'animals', 'colors', 'locations']
	for attribute in attributes_list:
		api_size = get_index(NAMESPACE, attribute)
		index = randint(1, api_size)
		name = get_data(NAMESPACE, attribute, index)
		generated_name[attribute] = name
	return generated_name

def get_index(ns, attribute):
    method = 'GET'
    content_type = 'application/json'
    #content_length = len(body)
    uri = 'http://' + attribute + '.' + ns + '/' + attribute

    headers = {
        'content-type': content_type,
    }

    response = requests.get(uri, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print 'Accepted'

        print 'Response: ' + str(response)
	json_data = response.json()
	print json_data
	list_size = len(json_data)	
        print('Size: %i',list_size)

    else:
        print "Response code: {}".format(response.status_code)
    return list_size

def get_data(ns, attribute, index):
    method = 'GET'
    content_type = 'application/json'
    resource = '/'+ attribute
    #content_length = len(body)
    uri = 'http://' + attribute + '.' + ns + '/' + attribute + '/' + str(index)

    headers = {
        'content-type': content_type,
    }
    print "index" + str(index)
    response = requests.get(uri, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        print 'Accepted'
        print 'Response: ' + str(response)
	json_data = response.json()
	print str(json_data)
	name = json_data['name']
	print 'Name: ' + name
    else:
        print "Response code: {}".format(response.status_code)
    return name        

def run(server_class=HTTPServer, handler_class=Server, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print 'Starting httpd on port %d...' % port
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
