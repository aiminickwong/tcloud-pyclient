#!coding:utf-8
#!/usr/bin/env python#
"""
    @author: jay.han
    @module:RPCServerThread
"""
import json
import threading
import SocketServer
from SocketServer import TCPServer
import logging
from twindow.common import utils

LOG = logging.getLogger(__name__)

class RPCServerThread(threading.Thread):
    "RPC server-proxy "
    rpcobj = None
    server_address = None
    server_port = None
    
    def __init__(self):
        super(RPCServerThread,self).__init__()
        self._stop=threading.Event()
        
    def run(self):
        server = TcloudTCPServer((self.server_address, self.server_port),TcloudTCPHandler,self.rpcobj)
        LOG.info("SocketServer listening on %s:%d" % (self.server_address, self.server_port))
        server.serve_forever()
        
    def stop(self):
        self._stop.set()
        
    def stopped(self):
        return self._stop.is_set()

class TcloudTCPServer(TCPServer):

    def __init__(self, server_address, RequestHandlerClass,gtkobj):
        """Constructor.  May be extended, do not override."""
        TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.gtkobj = gtkobj



class TcloudTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        method = json.loads(self.data)
        if 'shutdown' in method:
            if method['shutdown'] == 1:
                self.shutdown()
            elif method['shutdown'] == 2:
                self.killChannel()
        elif 'changecomputername' in method:
            self.change_hostname(method['changecomputername'])

        # just send back the same data, but upper-cased
        self.request.sendall('ok')

    def shutdown(self):
        self.server.gtkobj.shutdown()
        utils.execute("poweroff",run_as_root=True)
        return True

    def restart(self):
        utils.execute("reboot",run_as_root=True)
        return True

    def change_hostname(self,name):
        utils.execute('sed','-i','1s/.*/%s/g'%name,'/etc/hostname')
        utils.execute('hostname','-b',name)
        self.server.gtkobj._register()
        return True

    def killChannel(self):
        self.server.gtkobj.close_manager()
        return True





    