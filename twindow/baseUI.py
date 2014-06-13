#!/usr/bin/env python
#!coding:utf-8
"""
    @module: base ui
    @author: ezzze
    @contact: ezzzehxx@gmail.com
"""
import os
import logging
import pygtk
from twindow.common import utils

from twindow.common.baseTcloudObj import TcloudObject
from twindow.common.resource import res_dict as Resource


pygtk.require("2.0")
import gtk

basepath =os.path.abspath(os.path.dirname(__file__))
LOG = logging.getLogger(__name__)



class BaseWidget(TcloudObject):
    def __init__(self):
        TcloudObject.__init__(self)
        self.base = basepath
    """
        for testing
    """

    def init_diag(self,title,width,height):
        dialog = gtk.Dialog(title,buttons=None)
        dialog.set_default_size(width,height)

        dialog.add_buttons(Resource.BUTTON_CANCEL, gtk.RESPONSE_CLOSE)
        dialog.add_buttons(Resource.BUTTON_OK, gtk.RESPONSE_APPLY)
        return dialog

    def get_image_by_name(self,name,size=20):
        
        image = gtk.Image()
        image.set_from_pixbuf(utils.get_icon_by_name(name, size))
        return image
    
        
    def init_toolbar_box(self,box_detail=None,toolbaritems=None,h_align=False):
        manager_page_vbox = gtk.VBox()
        manager_page_tool_bar = gtk.Toolbar()
        
        if h_align:
            manager_page_tool_bar.set_orientation(gtk.ORIENTATION_VERTICAL)
            
        for i in toolbaritems:
            manager_page_tool_bar.append_item(i.name,i.tooltip,i.tooltip_info,i.image,i.func,i.data)
            manager_page_tool_bar.append_space()
        manager_page_vbox.pack_start(manager_page_tool_bar,0,0)
        
        if box_detail:
            manager_page_vbox.pack_start(box_detail,1,1)
        return manager_page_vbox
    
    def init_toolbar_direct(self,toolbaritems,h_align=False):
        manager_page_tool_bar = gtk.Toolbar()
        
        if h_align:
            manager_page_tool_bar.set_orientation(gtk.ORIENTATION_VERTICAL)
            manager_page_tool_bar.set_style(gtk.TOOLBAR_BOTH )
        for i in toolbaritems:
            button = manager_page_tool_bar.append_item(i.name,i.tooltip,i.tooltip_info,i.image,i.func,i.data)
            button.set_focus_on_click(True)
            manager_page_tool_bar.append_space()

        return manager_page_tool_bar
    
    def init_scroll_window(self,view=None,policy=gtk.POLICY_AUTOMATIC):
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(policy, policy)
        scrolled.set_shadow_type(gtk.SHADOW_NONE)
        scrolled.set_border_width(0)
        if view:
            scrolled.add_with_viewport(view)
        scrolled.show()
        return scrolled
    
    def right_align(self):
        return gtk.Alignment(1, 0, 0, 0)

    def left_align(self):
        return gtk.Alignment(0,1,0,0)
    
    def check_before_up_del(self,view=None,multi=False,nth=0):
        if not view:
            is_selected = self.curent_view.get_selected(nth)
        elif view and multi:
            is_selected = view.get_selected_items()
        else:
            is_selected = view.get_selected(nth)
            
        if not is_selected:
            self.on_error(Resource.NOT_SELECTED)
    
        return is_selected
     
        
    def _info_apply(self,widget,response_id=None):
        
        if response_id == gtk.RESPONSE_APPLY:
            self.info_answer = True
        widget.destroy()
        
    def on_ask(self,msg,call_back=None):
        self.info_answer = False
        info_dialog = gtk.MessageDialog(parent=None,flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                                        type=gtk.MESSAGE_INFO,buttons=gtk.BUTTONS_NONE,message_format=msg)
        info_dialog.add_buttons(Resource.BUTTON_CANCEL, gtk.RESPONSE_CLOSE)
        info_dialog.add_buttons(Resource.BUTTON_OK, gtk.RESPONSE_APPLY)
        if not call_back:
            info_dialog.connect("response", self._info_apply)
        else:
            info_dialog.connect("response", call_back)
        info_dialog.run()

        
class tcloudWidget(BaseWidget):
    def __init__(self):
        super(tcloudWidget,self).__init__()
        self.hpane_position = 250
        self.info_answer = False
    
    def make_view(self):
        raise NotImplementedError("show must be implemented in subclass")
    
    def close(self):
        pass
    
    def clean_up(self):
        self.close()
        
    def on_info(self,msg,master=None):
        info_dialog = gtk.MessageDialog(master,gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_INFO,gtk.BUTTONS_CLOSE,msg)
        
        
        info_dialog.connect("response", self._info_diag_call_back)
        info_dialog.run()
        

    def _info_diag_call_back(self,widget=None,data=None):
        widget.destroy()
    
    def get_icon(self,size=100,type=gtk.STOCK_FILE):
        icon_theme = gtk.icon_theme_get_default()
        icon = icon_theme.load_icon(type, size, 0)
        return icon
    
    def get_normal_icon(self):
        return self.get_icon(20, "gdu-smart-healthy")
        
    def get_test_icon(self):
        return self.get_icon(20, gtk.STOCK_FILE)
    
class tcloudWindow(BaseWidget):
    def __init__(self, filename, windowname):
        super(tcloudWindow,self).__init__()
        self.windowname = windowname
        self.builder = None
        self.mainwin = None
        self.ui_file = None
        if filename:
            self.ui_file = os.path.join(os.path.dirname(basepath),"ui",filename)
            self.builder = gtk.Builder()          
            self.builder.add_from_string(
                self.check_gtkbuilder(self.ui_file))
            self.builder.connect_signals(self)
            self.mainwin = self.widget(self.windowname)
            self.mainwin.hide()
    
   
    def on_info(self,msg,master=None):
        info_dialog = gtk.MessageDialog(master,gtk.DIALOG_DESTROY_WITH_PARENT,
                                        gtk.MESSAGE_INFO,gtk.BUTTONS_CLOSE,msg)
        info_dialog.connect("response", self._info_diag_call_back)
        info_dialog.run()
        

    def _info_diag_call_back(self,widget=None,data=None):
        widget.destroy()
        
    def clean_up(self):

        if self.mainwin:
            self.mainwin.destroy()
            self.mainwin = None
            self.uifile = None
        
        
    def widget(self, name):
        return self.builder.get_object(name)
    
    def show(self):
        raise NotImplementedError("show must be implemented in subclass")
    
    def close(self,widget=None,data=None):
        pass
    
    def check_gtkbuilder(self,filename):
        """
        If on an old GTK version, raise a problem
        """
        ver = gtk.gtk_version
        xml = file(filename).read()
        
        if (ver[0] > 2 or
            (ver[0] == 2 and ver[1] > 18)):
            # Skip altering for gtk > 2.18
            return xml
        else:
            LOG.error("not support %s gtk version" % ver)