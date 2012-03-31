
import tornado.httpserver
import tornado.ioloop
import tornado.web

import sys
from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

import logging
import hmac
import hashlib
import base64
import urllib
import socket
import traceback
import simplejson
import re

'''
Log Catcher: receives put request and sends them to scribe.

Example endpoint:
http://<your_server_dns_name_or_ip>/put_logs?category=application1&message=this%20is%20a%20test&hash=RWPzriPjiX202eF3LbCb0xB5zIw=
'''

LOGGING_SHARED_SECRET = "<your logging secret key>"
SERVER_HOSTNAME = "none"
try:
    SERVER_HOSTNAME = socket.gethostbyname(socket.gethostname())
except:
    pass
logging.basicConfig(level=logging.WARN)


scribe_transport = None
scribe_client = None

SCRIBE_HOST = '127.0.0.1'
SCRIBE_PORT = 1463

# Init scribe
socket = TSocket.TSocket(host=SCRIBE_HOST, port=int(SCRIBE_PORT))
scribe_transport = TTransport.TFramedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(trans=scribe_transport, strictRead=False, strictWrite=False)
scribe_client = scribe.Client(iprot=protocol, oprot=protocol)


class LogCatcherHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Server: " + SERVER_HOSTNAME + "<br>\n")
        self.write("(get) logging request received.<br>\n")
        self.get_params_and_process_message()

    def post(self):
        self.write("Server: " + SERVER_HOSTNAME + "<br>\n")
        self.write("(post) logging request received.<br>\n")
        self.get_params_and_process_message()
        
    def get_params_and_process_message(self):
        try:
#            logging.info("get_params_and_call_scribe()")
            try:
                self.category = self.get_argument('category')
            except:
                message = None
                try: message = self.get_argument('message').encode("utf-8")
                except: pass
                logging.error("Category argument missing. Message was: " + str(message))
                
            self.message = self.get_argument('message').encode("utf-8")
            self.hash = self.get_argument('hash').replace(' ', '+')
     
            if not self.category or not self.message or not self.hash:
                self.write("Error: Must contain category and message and hash.<br>\n")
                logging.error("Must contain category and message and hash.")
                return
            
            message_for_hash = self.message
            
            # Calc valid hash
            digest = hmac.new(LOGGING_SHARED_SECRET, message_for_hash, hashlib.sha1).digest()
            calculated_hash = base64.encodestring(digest)
            
            # Test if hash matches
            hash_matches = (self.hash[:28] == calculated_hash[:28])
            
            if hash_matches:
                self.write("hash matched, logging to scribe.<br>\n")
#                logging.info("hash matched, logging to scribe.")
                forward_message(self.category, self.message)
            else:
                self.write("nothing was logged.<br>\n")
#                logging.warn("last char: " + str(ord(self.message[len(self.message)-1])))
                logging.warn("calculated hash = " + str(calculated_hash))
                logging.warn("  provided hash = " + str(self.hash))
                logging.warn("hash_matches: " + str(hash_matches))
                try:
                    logging.warn("nothing was logged. message[0:500]: " + self.message[:500])
                except:
                    logging.warn("nothing was logged.")
        except:
            logging.error("Error processing request.")
            traceback.print_exc()


########################
# Register Handlers
########################

def forward_message(category, message):
    send_records_to_scribe(category, message)
    # Add other handlers here


########################   
# Scribe
########################

def send_records_to_scribe(category, message):
    try:
        global scribe_transport
        global scribe_client
        
        if not scribe_transport or not scribe_client:
            # Re-init scribe
            logging.warn("Had to re-init scribe")
            socket = TSocket.TSocket(host=SCRIBE_HOST, port=int(SCRIBE_PORT))
            scribe_transport = TTransport.TFramedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(trans=scribe_transport, strictRead=False, strictWrite=False)
            scribe_client = scribe.Client(iprot=protocol, oprot=protocol)
        
        scribe_transport.open()
        
        lines = message.split("\n")
        log_entries = []
        for line in lines:
            log_entry = scribe.LogEntry(category=category, message=line)
            log_entries.append(log_entry)
        
        result = scribe_client.Log(messages=log_entries)
        
        scribe_transport.close()
        
        if result == scribe.ResultCode.OK:
            pass
        elif result == scribe.ResultCode.TRY_LATER:
            logging.error("TRY_LATER. Result: " + str(result))
        else:
            logging.error("Unknown error code." + str(result))
    except:
        logging.error("Error sending records to scribe.")
        traceback.print_exc()



class HeartbeatHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Web server is up...")


application = tornado.web.Application([
        (r"/put_logs", LogCatcherHandler),
        (r"/index.html", HeartbeatHandler),
    ])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
