#!coding:utf-8
#!/usr/bin/env python#
"""
    @author:Jay.Han
    @TODO 异常处理
"""
import dbus
import socket

from twindow.api.apr_proxy import api as api_proxy
from twindow.common import utils

import logging
import thread
import time
from twindow.common.exception import NetworkException

VERSION = '3.0.0'
LOG = logging.getLogger(__name__)

class ClientDaemon(object):

    def __init__(self,config):
        self.version = VERSION
        self.conf = config
        self.api_debug = self.conf.get_bool('api_debug')
        self.ifname = self.conf['interface']
        self.is_tearcher = self.conf.get_bool('is_tearcher_client')
        self.pool = self.conf['pool']
        self.init()
    #TODO
    def handle_hello_reply(self,r):
        pass
    #TODO
    def handle_hello_error(self,e):
        pass

    def init_dbus_client(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        bus = dbus.SessionBus()
        try:
            self.dbus_obj = bus.get_object("com.tcloud.gtkService","/gtkObject")
        except:
            LOG.exception("error in init remote object")

    def init(self):
        self.hostname = self.get_hostname()
        self.mac = utils.get_mac_address(self.ifname)
        self.os = utils.get_os()
        self.ip = utils.get_interface_ip(self.ifname)
        self.cpu_type=utils.get_cpu_type()
        self.memory = utils.get_memory_mb()
        self.register()

    def get_hostname(self):
        return utils.get_hostname()

    def killSession(self):
        self.init_dbus_client()
        self.dbus_obj.killSession("kill session",dbus_interface='com.tcloud.Interface',
                                  reply_handler=self.handle_hello_reply,
                                  error_handler=self.handle_hello_error)
    def close_manager(self):
        self.init_dbus_client()
        self.dbus_obj.close_manager("close manager",dbus_interface="com.tcloud.Interface",
                                    reply_handler=self.handle_hello_reply,
                                    error_handler=self.handle_hello_error)
    def shutdown(self):
        self.init_dbus_client()
        self.dbus_obj.shutdown("Shutdown",dbus_interface='com.tcloud.Interface',
                               reply_handler=self.handle_hello_reply,
                               error_handler=self.handle_hello_error)


    """
        update the version
    """
    def upgrade(self):
        pass
    
    def start_app(self):
        pass
    
    def stop_app(self):
        pass
    
    def _register(self,is_keep_live=False,client_id=None):

        if is_keep_live:
            LOG.info("tring to keep alive....")
        else:
            LOG.info("register the info.....")

        if is_keep_live:
            return api_proxy.keep_alive({'client_name':self.get_hostname() ,
                                  'client_ip':self.ip,
                                  'client_mac':self.mac,
                                  'client_id':int(client_id)
                                })
        else:
            return api_proxy.register({ 'client_name':self.get_hostname() ,
                                 'client_ip':self.ip,
                                 'client_mac':self.mac,
                                 'client_os':self.os,
                                 'client_cpu':self.cpu_type,
                                 'client_memory':self.memory,
                                 'status':True,
                                 'is_teacher_client':self.is_tearcher,
                                 'pool':self.pool})
        
    def register(self):
        def heartbeat():
            first = True
            id = None
            while 1:
                try:
                    if first:
                        resp = self._register()
                        first = False
                    else:
                        self._register(is_keep_live=True,client_id=resp['id'])
                except NetworkException:
                    LOG.exception('network issue')
                    self.close_manager()
                except:
                    LOG.exception('update service heartbeat error')
                finally:
                    time.sleep(30)
        
        LOG.info('starting periodic task to keep serivice heartbeat')
        thread.start_new_thread(heartbeat,()) 
        