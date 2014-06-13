#!/usr/bin/env python
#!coding:utf-8
"""
    @module:view
    @author: ezzze
    @contact: ezzzehxx@gmail.com
"""
import socket
import sys
import errno
from twindow.common import utils
from twindow.common.baseTcloudObj import TcloudObject
try:
    import SpiceClientGtk as _spice
except:
    sys.stderr.write("Warning. spice python binding is not installed. spice support will be disabled")
    _spice = None
try:
    import gtkvnc as _gtkvnc 
except:
    sys.stderr.write("Warning. vnc python binding is not installed. vnc support will be disabled")
    _gtkvnc = None
    
import gobject
import logging

LOG = logging.getLogger("twindow.viewer")

class View:
    def __init__(self,widget):

        self.window = widget
        self.connected = False
    
    def connect_host(self):
        raise NotImplementedError("connect_host must be implemented in subclass")
    
    def is_connect(self):
        return self.connected
    
class VNC_Viewer(View):
    def __init__(self,widget,host,port,read_only=False,share=False):
        View.__init__(self,widget)
        try:
            self.display = _gtkvnc.Display()
        except:
            LOG.error("ERROR IN init gtkvnc")
        self.read_only = read_only
        self.share = share
        self.sockfd = None
        self.host = host
        self.port = port
        
    def connect_host(self,password=None):
        self.window.viewer_widget.add(self.display)
        self.init_widget()
        self.window.viewer_widget.show_all()
        LOG.debug("connecting to %s" % self.host)
        self.display.open_host(self.host, self.port)
        
    
    def close(self):
        self.connected = False 
        if self.display:
            LOG.debug("Destroying VNC display...")
            self.display.destroy()
        self.display = None
        self.window = None
        if not self.sockfd:
            return
        LOG.debug("CLOSING socket fd")
        self.sockfd.close()
        self.sockfd = None
        

    def is_open(self):
        return self.display.is_open()
    """
        设置键
    """
    def set_grab_keys(self):
        pass
    
    def init_widget(self):
        LOG.debug("init VNC widget.....")
       
        self.set_grab_keys()
        self.display.realize()
        # Make sure viewer doesn't force resize itself
        self.display.set_force_size(False)
        self.display.set_scaling(True)
        self.display.set_shared_flag(True)
        self.display.set_read_only(self.read_only)
            
        #self.display.set_pointer_local(True)
        self.display.set_keyboard_grab(True)
        self.display.set_pointer_grab(True)
        
#        self.display.connect("vnc-pointer-grab", self.vnc_grab)
#        self.display.connect("vnc-pointer-ungrab",self.vnc_ungrab)
#        
        self.display.connect("vnc-connected", self.vnc_connected)
#        self.display.connect("vnc-initialized", self.vnc_initialized)
        self.display.connect("vnc-disconnected", self.vnc_disconnected)
        self.display.connect("vnc-desktop-resize", self._desktop_resize)
        
        
    def get_desktop_size(self):
        return self.desktop_resolution
    #TODO
    def _desktop_resize(self, src_ignore, w, h):
        self.desktop_resolution = (w, h)
        self.window.resize_to_vm()
        
    def vnc_grab(self,src):
        LOG.debug("vnc grabed")

    def vnc_ungrab(self,src):
        LOG.debug("vnc ungrabed")
    
    def vnc_connected(self,src):
        self.connected = True
        LOG.debug("Connected to vnc server")
    
    def vnc_initialized(self,src):
        LOG.debug("Connection initialized")
        
    
    def vnc_disconnected(self,src):
        self.close()
        LOG.debug("Disconnected from vnc server")
        
    def open_fd(self, fd):
        self.display.open_fd(fd)
        
class Spice_Viewer(TcloudObject):
    
    def __init__(self,widget,host,port,conf):
        TcloudObject.__init__(self)
        self.disp_console = widget
        self.session = None
        self.conf = conf
        self.display = None
        self.main_channel = None
        self.audio = None
        self.display_channel = None
        self.connected = False
        self.usbManager = _spice.UsbDeviceManager()
        self.host= host
        self.port = port
    def is_connect(self):
        return self.connected

    def settings(self):
        self.session = _spice.Session()
        uri = "spice://"
        uri += str(self.host) + "?port=" + str(self.port)
        self.session.set_property("uri",uri)
        
    def is_open(self):
        return self.session != None
    
    def set_grab_keys(self):
        #TODO
        pass
    
    def _init_widget(self):
        self.set_grab_keys()
        self.display.realize()
        self.display.set_property('grab-mouse',True)
        # resize guest == true
        self.display.set_property('resize-guest',True)
        self.display.show()
        
    def open_fd(self, fd, password=None):
        self.session = _spice.Session()
        if password:
            self.session.set_property("password", password)
        gobject.GObject.connect(self.session, "channel-new",
                                self._channel_new)
        self.session.open_fd(fd)

    def _is_port_still_open(self,host,port):
        flag = True
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host,port))
            data = s.recv(1024)
        except socket.timeout:
            LOG.exception('socket timeout......')
            flag = True
        except socket.error, v:
            errorcode=v[0]
            if errorcode==errno.ECONNREFUSED:
                flag = False
            elif errorcode == errno.ECONNRESET:
                flag = False
            else:
                LOG.exception("unknown exception accurs %s" % v[0])
                flag = False
        except:
            LOG.exception('unknown exception accurs')
            flag = True
        finally:
            LOG.debug("is port still open %s" % flag)
            s.close()

        return flag
    def _main_channel_event(self, channel, event):

        if not self.disp_console:
            return

        if event == _spice.CHANNEL_CLOSED:
            LOG.debug("channel closed.......")
            if self.display:
                LOG.debug("try to detect the port is open....")
                if self._is_port_still_open(self.host,int(self.port)):
                    self.close_rc()
                else:
                    self._close_rc()
                    #if not self.conf.get_bool('shutdown_vm_not_poweroff'):
                    #    utils.execute("poweroff",run_as_root=True)

        elif event == _spice.CHANNEL_ERROR_AUTH:
            LOG.debug("channel not auth")
            self.on_error("非法连接,请检查客户端版本",self.on_error_callback_close)

        elif event == _spice.CHANNEL_ERROR_CONNECT:
            LOG.debug("channel not connected. is host available now?")
            #TODO pop a dialog?
        elif event == _spice.CHANNEL_ERROR_IO:
            LOG.debug("error in IO")
            #TODO pop a dialog?
        elif event == _spice.CHANNEL_ERROR_LINK:
            LOG.debug("error in channel link")

        elif event == _spice.CHANNEL_OPENED:
            LOG.debug('open channel ')
        else:
            LOG.debug('event %s ' % event)
    def _agent_connected_cb(self,widget,ignore):

        LOG.debug('agent connected')

    def _channel_new(self, session, channel):
        
        if type(channel) == _spice.MainChannel and \
            not self.main_channel:

            self.main_channel = channel
            self.main_channel.connect_after("channel-event",
                                            self._main_channel_event)
            self.main_channel.connect_after("notify::agent-connected",
                                            self._agent_connected_cb)
            return

        if type(channel) == _spice.DisplayChannel and \
            not self.display:
            channel_id = channel.get_property("channel-id")

            if channel_id != 0:
                LOG.debug("Spice multi-head unsupported")
                return

            self.display_channel = channel
            self.display = _spice.Display(self.session, channel_id)  
            self.disp_console.viewer_widget.add(self.display)     
            self._init_widget()
            self.connected = True
            return

        if (type(channel) in [_spice.PlaybackChannel, _spice.RecordChannel] and
            not self.audio):

            try:
                self.audio = _spice.Audio(self.session)
                LOG.debug("audio channel is establish")
            except Exception as e:
                LOG.debug("SPICE AUDIO OBJECT could not create %s" % e)
            finally:
                return
        
        if type(channel) == _spice.UsbredirChannel:
            LOG.debug("usb channel is establish")
            u = _spice.spice_usb_device_manager_get(self.session)
            u.set_property("auto_connect",self.auto_detect_usb_rediect())
            u.connect("auto-connect-failed",
                                        self._usbdev_redirect_error)
            u.connect("device-error",
                                        self._usbdev_redirect_error)
            return

    def _usbdev_redirect_error(self,spice_usbdev_widget, spice_usb_device,
                               errstr):
        ignore_widget = spice_usbdev_widget
        ignore_device = spice_usb_device

        LOG.debug("error in usb redirect %s " % errstr)

    def auto_detect_usb_rediect(self):
        return True

    # outside method
    def close(self):
        LOG.debug("closing spice view......")
        self._close_rc()

    def _close_rc(self):
        self.connected = False
        LOG.debug("closing spice view resource......")

        if self.session:
            self.session.disconnect()
            self.session = None
        self.audio = None

        if self.display:
            LOG.debug("Destroy spice view display......")
            self.display.destroy()

        self.display = None
        self.main_channel = None
        self.display_channel = None


    def on_error_callback_close(self,widget,ignore):
        widget.destroy()
        self.close_rc()


    def close_rc(self):
        LOG.debug("close spice rc by channel closed....")
        self._close_rc()
        self.emit("viewer-closed")


    def connect_host(self,password=None):
        self.settings()
        if password:
            self.session.set_property("password", password)
            
        gobject.GObject.connect(self.session, "channel-new",
                                self._channel_new)
        self.session.connect()

TcloudObject.type_register(Spice_Viewer)
Spice_Viewer.signal_new(Spice_Viewer, "viewer-closed", [])
    
if __name__ == '__main__':
    pass
