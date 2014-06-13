#!coding:utf-8
"""
    @author: jay.han
    
"""
import gudev
from gudev import Client
import gobject
import logging
from twindow.common.baseTcloudObj import TcloudObject

LOG = logging.getLogger("usbDevice")

class usbDevice(TcloudObject):
    """
        python missing
    """
    
    __gsignals__ = {
        'connected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_PYOBJECT,)),
        'disconnected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_PYOBJECT,)),
    }
    
    def __init__(self,subsystems=["usb"]):
        '''
        Create a new DeviceFinder and attach to the udev system to 
        listen for events.
        '''
        TcloudObject.__init__(self)
        
        self.client = gudev.Client(subsystems)
        self.subsystems = subsystems
        self.devices_tree = {}
        self.devices_list = []

        self.client.connect('uevent', self.uevent)


    def get_devices_tree(self):
        return self.devices_tree
        
    def get_devices(self):
        return self.devices_list
     
    def get_device_info(self,device):
        
        subsys = device.get_subsystem()
        if subsys == 'usb':
            
            return 
        else:
            LOG.error("unsupport device now")
        
    def uevent(self, client, action, device):
        '''Handle a udev event'''
        device_name = device.get_property("DEVNAME")
        
        if device_name:
            if action == 'add':
                self.device_added(device)
            elif action == "remove":
                self.device_remove(device)
            elif action == "change":
                pass
            else:
                pass
    """
        unplug device
    """   
    def device_remove(self,device):
        
        LOG.debug("unplug a usb device")
        pass
    """
        plug device
    """
    def device_added(self, device):
        
        LOG.debug("plug a usb device")
        self.get_device_info(device)
        pass

TcloudObject.type_register(usbDevice)

    
if __name__ == '__main__':         
    def connect(finder, device):
        print 11
    
    def discon(finder, device):
        print 22
        
    usb = usbDevice()
    usb.connect("connected",connect)
    usb.connect("disconnected",discon)
#    usb.connect('connected', found)
    gobject.MainLoop().run()