#!coding:utf-8
#!/usr/bin/env python
"""
    @author: ezzze
    @contact: ezzzehxx@gmail.com
"""
from twindow.baseUI import tcloudWindow
import gtk
from autodrawer import AutoDrawer

from tcloudViewer import VNC_Viewer, Spice_Viewer
import logging
from twindow.common import utils, config
from twindow.common.baseTcloudObj import TcloudObject
from twindow.common.resource import res_dict as Resource
from twindow.model.tcloudModel import LabelModel

LOG = logging.getLogger("viewerManager")
conf = config.load_settings()



class viewManager(tcloudWindow):
    def __init__(self,hostname,ip,api,vm_id,
                        connect_info="172.16.10.241:5929",
                        graphic_type="spice",
                        pwd = None,
                        readonly=True):
        tcloudWindow.__init__(self,"view-manager.ui", "tcloud-window")
        w, h = 1024,768
        self.mainwin.set_default_size(w or 550, h or 550)
        self.vm_id = vm_id
        self.hostname = hostname
        self.ip = ip
        self.pwd = pwd
        self.api = api
        #TODO记住之前的位置
        self.prev_position = None
        
        self.viewer_widget = self.widget("viewer-widget")
        self.mainwin.set_title(Resource.MANAGER_LABEL %(self.hostname,self.ip))
        self.pages = self.widget("view-page")
        
        self.readonly = readonly
        self.graphic_type= graphic_type
        self.connect_info = connect_info
        self.fullscreen = False
    	self.init_tool_bar()
        self.enter_fullscreen()
    
    def init_tool_bar(self):
            
    	scroll = self.widget("view-display")
    	self.pages.remove(scroll)
    	
        self.fs_toolbar = gtk.Toolbar()
        self.fs_toolbar.set_show_arrow(False)
        self.fs_toolbar.set_no_show_all(True)
        self.fs_toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)

        # Exit fullscreen button
        # label = LabelModel(Resource.LOGIN_MODE,1,0.5,font=12)
        # button = gtk.ToolButton(gtk.STOCK_LEAVE_FULLSCREEN)
        # button.show()

        self.fs_toolbar.append_item(Resource.TOOLBAR,
                                    Resource.TOOLBAR,
                                    'Private',
                                    None,
                                    self.ignore
                                    )
        shutdown_icon = utils.get_image_from_file('power_off.png')
        self.fs_toolbar.append_item(Resource.SHUTDOWN_VM,
                                    Resource.SHUTDOWN_VM,
                                    'Private',
                                    shutdown_icon,
                                    self.shutdown_vm)
        # button.connect("clicked", self.leave_fullscreen)
        
        self.fs_drawer = AutoDrawer()
        self.fs_drawer.set_active(False)
        self.fs_drawer.set_over(self.fs_toolbar)
        self.fs_drawer.set_under(scroll)
        self.fs_drawer.set_offset(-1)
        self.fs_drawer.set_fill(False)
        self.fs_drawer.set_overlap_pixels(1)
        self.fs_drawer.set_nooverlap_pixels(0)
        self.fs_drawer.show_all()

        self.pages.add(self.fs_drawer)
    def ignore(self,widget=None):
        pass
    def shutdown_vm(self,widget,data=None):
        self.api.shutdown_vm_api({'id':self.vm_id})
        return True


    def leave_fullscreen(self,widget=None):
    	self.fs_toolbar.hide()
        self.fs_drawer.set_active(False)
        self.mainwin.unfullscreen()
        self.fullscreen = False
        self.resize_to_vm()
        self.widget("tcloud-vm").show()
      
    def enter_fullscreen(self,widget=None):
     	self.mainwin.fullscreen()

        self.fs_toolbar.show()
        self.fs_drawer.set_active(True)
        self.fs_toolbar.set_show_arrow(True)
        #self.fs_drawer.set_can_focus(False)
        self.no_scroll()
        self.widget("tcloud-vm").hide()
        self.fullscreen = True

    def _zoom(self,widget,event):
        if event.keyval == gtk.keysyms.F10:
            if self.fullscreen:
                self.mainwin.unfullscreen()
                self.resize_to_vm()
                self.fullscreen = False
            else:
                self.mainwin.fullscreen()
                self.no_scroll()
                self.widget("tcloud-vm").hide()
                self.fullscreen = True
    """
    	打开app
    """  
    def show(self):
        self.mainwin.present()
        
        self.show_view()
        self.binding_event()
    """
    	清除缓存或者其他引用到gobject的对象    
    """
    def clean(self):
        self.clean_up()
    
    def is_visible(self):
        return bool(self.mainwin.flags() & gtk.VISIBLE) 
   
    def change_view(self,graphic_type,connect_info):
        self.old_g_type = self.graphic_type
        self.old_connect_info = self.connect_info
        
        self.graphic_type = graphic_type
        self.connect_info = connect_info
        self.viewer.close()
        LOG.debug("begin to show vnc widget......")
        self.show_view()
    
    def change_back(self):
        
        self.graphic_type = self.old_g_type
        self.connect_info = self.old_connect_info
        self.viewer.close()
        self.show_view()
        
    def show_view(self):

        host,port = self.connect_info.split(":")
        if self.graphic_type == "vnc":
            self.viewer = VNC_Viewer(self,read_only=self.readonly)
        elif self.graphic_type == "spice":
            self.viewer = Spice_Viewer(self,host,port,conf)
        else:
            raise

        self.viewer.connect_host(password=self.pwd)
        
    """
    	call back function: close
    """
    def close(self,widget=None,data=None):
        LOG.debug("Closing manager by widget %s" % widget)

        if self.viewer:
            self.viewer.close()
            self.viewer = None

        if self.mainwin:
            LOG.debug("clean up rc in view manager")
            self.clean_up()


        self.emit("manager-closed")

    def sub_close_view(self,widget=None):
        LOG.debug("Closing manager by viewer using emit")
        self.clean_up()

    """
    	disconnect the spice
    """
    def disconnect(self,widget=None):
        LOG.debug("Disconnect vm")
        if self.viewer:
            self.viewer.close()
    def connected(self,widget=None):
        if self.viewer.is_connect():
            return
        else:
            self.show_view()
    def binding_event(self):
        self.mainwin.connect("destroy",self.close)
        self.viewer.connect('viewer-closed',self.sub_close_view)
        self.widget("vm-fullscreen").connect("clicked",self.enter_fullscreen)
        self.widget("vm-disconnect").connect("clicked",self.sub_close_view)

        self.mainwin.connect("key-press-event", self._zoom)

    def no_scroll(self):
        self.widget("view-display").set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)   
        
    def resize_to_vm(self):
        self.widget("view-display").set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    
TcloudObject.type_register(viewManager)
viewManager.signal_new(viewManager, "manager-closed", [])

if __name__=="__main__":
    t = viewManager()
    t.show()
    gtk.main()   
        