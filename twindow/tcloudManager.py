#!coding:utf-8
#!/usr/bin/env python#
import logging
import gtk
from twindow.baseUI import  tcloudWidget
from twindow.model.tcloudModel import VMListModel, MenuTree,\
    MenuItem, DiskListModel, ToolbarItem, LabelModel, TableModel
import sys

try:
    import vte as _vte
except:
    sys.stderr.write("Warning. vte python binding is not installed. vte support will be disabled")
    _vte = None
    
from twindow.common import utils

MENU_ROOT = "tcloud"
LOG = logging.getLogger("twindow.manager")
#ubuntu 比较坑爹 会吞掉菜单栏
import os
os.environ['UBUNTU_MENUPROXY'] = '0'

class tManager(tcloudWidget):
    def __init__(self):
        
        self.rows = {}
        """
			read from config
		"""
        self.pane_position = 250
        """
            basic 
        """
        self.selected_host = None
        self.selected_vm = None
        self.current_page = None
        
    def make_view(self):
        #################
        ### gtk Vbox
        #################
        sys_contents = gtk.VBox()
        logo = gtk.HBox()
        
        self.main_box = gtk.HPaned()
#        title_paned.pack_start(logo,0,0)
        ######################## left tree ##########################################
        left_tree = self.init_left_tree()
        left_tree.connect("cursor-changed",self.select_host)
        self.left_tree_view,left_tree_window = left_tree.make_view(expend=False)
        self.left_tree_view.connect('button_press_event', self.show_popup_menu)
        self.create_popup()
        
        self.current_page = self.init_host_page()
        self.main_box.set_position(self.pane_position)
        self.main_box.pack1(left_tree_window,resize=True, shrink=False)
        self.main_box.pack2(self.current_page,resize=True, shrink=False)
        
        sys_contents.pack_start(logo,0,0)
        sys_contents.pack_start(self.main_box,1,1)
 
        return sys_contents
    
    def init_host_page(self):
        ######################### host ###############################################
        
        host_pages = gtk.Notebook()
        host_pages.set_tab_pos(gtk.POS_TOP)
        
        host_page_label = LabelModel("服务器概览",0.5,0.5)
        host_page_label.set_can_focus(False)
        host_console_box = self.init_host_console_page()
        host_pages.append_page(host_console_box,host_page_label)
        ########################### cosole  ###########################################
        console_page_label = LabelModel("控制台",0.5,0.5)
        console_page_label.set_can_focus(False)
        
        console = _vte.Terminal()
        console.set_cursor_blinks(True)
        console.set_emulation("xterm")
        console.set_scrollback_lines(1000)
        console.set_audible_bell(False)
        console.set_visible_bell(True)
        # XXX python VTE binding has bug failing to register constants
        #self.terminal.set_backspace_binding(vte.ERASE_ASCII_BACKSPACE)
        console.set_backspace_binding(1)
        #command = "exec ssh -q -t %s" % "tcloud@172.16.10.64"
        # fork_command() will run a command, in this case it shows a prompt
        console.fork_command()
#        console.feed_child(command)
        console.connect("child-exited",self.exit_terminal)
        host_pages.append_page(console,console_page_label)
        ########################### 硬盘  ###########################################
        disk_page_label = LabelModel("ISO 位置",0.5,0.5)
        disk_page_label.set_can_focus(False)
        
        disk_console = self.init_disk_console_page()
        host_pages.append_page(disk_console,disk_page_label)
        ########################### 监控  ###########################################
        monitor_page_label = LabelModel("监控",0.5,0.5)
        monitor_page_label.set_can_focus(False)
        
        monitor_console = self.init_disk_console_page()
        host_pages.append_page(monitor_console,monitor_page_label)
        
        ########################### 监控  ###########################################
        return host_pages
    
    def init_vm_page(self):
        vm_pages = gtk.Notebook()
        vm_page_label = gtk.Label("实例")
        vm_page_label.set_can_focus(False)
        vm_console_box = self.init_vm_console_page()
        vm_pages.append_page(vm_console_box,vm_page_label)
        
        snapshot_label = gtk.Label("快照管理")
        
        return vm_pages
        
    def init_left_tree(self):
        menu_root = MenuItem(None,"tcloud","None")
        menu_item = MenuItem(None,"tcloud245","host-0000001")
        sub_menu_item1 = MenuItem(None,"test1","i-0000001")
        sub_menu_item2 = MenuItem(None,"test2","i-0000002")
        
        menu_item.add_sub_menu(sub_menu_item1)
        menu_item.add_sub_menu(sub_menu_item2)
        
        menu_item2 = MenuItem(None,"tcloud242","host-0000002")
        sub_menu_item11 = MenuItem(None,"test1","i-0000004")
        sub_menu_item22 = MenuItem(None,"test2","i-0000005")
        
        menu_item2.add_sub_menu(sub_menu_item11)
        menu_item2.add_sub_menu(sub_menu_item22)
        
        return  MenuTree([menu_item,menu_item2],root=menu_root)
    def init_disk_console_page(self,data=None):
        disk_list = ["26","172.16.10.26","ISO","64%","8G"]
        
        view = DiskListModel(self.rows).make_view(data_list=disk_list)
        return self.init_disk_box(view)
        
    def init_host_console_page(self,data=None):
        general_info_box = gtk.VBox()
        
        general_info_table = TableModel(5,3)
        
        data = [[LabelModel("服务器名",0,0.5),
                 LabelModel("IP",0,0.5),
                 LabelModel("负载",0,0.5),
                 LabelModel("cpu负载",0,0.5),
                 LabelModel("内存使用率",0,0.5),
                 LabelModel("硬盘使用率",0,0.5)],
                [LabelModel("tcloud245",0,0.5),
                LabelModel("172.16.10.245",0,0.5),
               LabelModel("3.0",0,0.5),
               LabelModel("49%",0,0.5),
               LabelModel("10%",0,0.5),
               LabelModel("10%",0,0.5)],
                []]
        general_info_table.init_rc_data(data)
        
        detail_info_table = TableModel(5,3)
        
        data2 = [[LabelModel("软件版本",0,0.5),
                  LabelModel("活跃实例数",0,0.5),
                  LabelModel("cpu名称",0,0.5),
                  LabelModel("cpu核数",0,0.5),
                  LabelModel("内存大小",0,0.5),
                  LabelModel("硬盘大小",0,0.5)],
                 [LabelModel("2.1",0,0.5),
                  LabelModel("3",0,0.5),
                  LabelModel(utils.get_cpu_type(),0,0.5),
                  LabelModel("4",0,0.5),
                  LabelModel("16G",0,0.5),
                  LabelModel("490G",0,0.5)]]
        
        detail_info_table.init_rc_data(data2)
        title = LabelModel(" 概览",0,0.5,font=30)
        
        general_info_box.pack_start(title,0,1,padding=10)
        general_info_box.pack_start(gtk.HSeparator(),0,1)
        general_info_box.pack_start(general_info_table,1,1)
        general_info_box.pack_start(gtk.HSeparator(),0,1)
        general_info_box.pack_start(detail_info_table,1,1)
        return general_info_box
    
    def init_vm_console_page(self,data=None):
        vm_list = ["test","172.16.10.233","up","img-044","WINXP","1","8G","60G","admin"]
        self.vm_list = VMListModel(self.rows).make_view(data_list=vm_list)
        
        return self.init_vm_box(self.vm_list)
    
    def init_disk_box(self,box_detail):
        items = [ToolbarItem("新增存储",           # button label
                            "新增存储", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("add", 20),             # i         con widget
                            self.add_disk)
                 
                 ,ToolbarItem("删除",           # button label
                            "删除一个存储位置", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("remove", 20),             # icon widget
                            self.delete_disk)]
        
        return self.init_toolbar_box(box_detail, items)
    
    def init_vm_box(self,box_detail):   
        items = [ToolbarItem("开机",           # button label
                            "开机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("gtk-media-play-ltr", 20),             # i         con widget
                            self.start_vm)
                 ,ToolbarItem("关机",           # button label
                            "关机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("system-shutdown", 20),             # icon widget
                            self.shutdown_vm)
                 ,ToolbarItem("重启",           # button label
                            "重启主机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("system-restart", 20),             # icon widget
                            self.reboot_vm)
                 ,ToolbarItem("更新",           # button label
                              "更新一个用户", # this button's tooltip
                              "Private",         # tooltip private info
                              self.get_image_by_name("gtk-edit", 20),             # icon widget
                              self.update_vm)
                 ,ToolbarItem("快照",           # button label
                            "进行快照", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("gtk-edit", 20),             # icon widget
                            self.update_vm)]
        return self.init_toolbar_box(box_detail, items)
    
    def init_host_box(self,box_detail):
        items = [ToolbarItem("开机",           # button label
                            "开机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("gtk-media-play-ltr", 20),             # i         con widget
                            self.start_host),
                 ToolbarItem("关机",           # button label
                            "关机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("system-shutdown", 20),             # icon widget
                            self.shutdown_host),
                 ToolbarItem("重启",           # button label
                            "重启主机", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("system-restart", 20),             # icon widget
                            self.reboot_host),
                 ToolbarItem("更新",           # button label
                            "更新一个用户", # this button's tooltip
                            "Private",         # tooltip private info
                            self.get_image_by_name("gtk-edit", 20),             # icon widget
                            self.update_host)]
        
        return self.init_toolbar_box(box_detail, items)
    
    ############################################################
    #########  call back
    ############################################################
    def select_host(self,widget,data):
        self.main_box.remove(self.current_page)
        
        if "i-0" in data:
            self.current_page = self.init_vm_page()
        else:
            self.current_page = self.init_host_page()
            
        self.main_box.pack2(self.current_page,resize=True, shrink=False)
        self.main_box.show_all()
        
    def show_popup_menu(self,widget,event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.left_tree_view.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                """
                    @todo focus on this
                """
                self.popup.popup( None, None, None, event.button, time)
            return 1
    
    def create_popup(self):
        """ Create popup menu for right click """
        self.popup = gtk.Menu()

        menu_item = gtk.ImageMenuItem("新建实例")
        menu_item2 = gtk.ImageMenuItem("新建ISO位置")
        
        self.popup.append(menu_item)
        self.popup.append(menu_item2)
        """
            @todo binding the action
        """
        #menu_item.connect('toggled', self.show_hidden_toggled)
        self.popup.show_all()
        
    def exit_terminal(self,widget):
        print "exit terminal"
        
    def add_disk(self,widget):
        print "add disk"
    
    def delete_disk(self,widget):
        print "delete disk"
    ##################################
    def start_host(self,widget):
        print "start host"
    
    def shutdown_host(self,widget):
        print "shutdown host"
    
    def reboot_host(self,widget):
        print "reboot host"
    
    def update_host(self,widget):
        print "update host"
    ##################################
    def start_vm(self,widget):
        print "start vm"
    
    def shutdown_vm(self,widget):
        print "shutdown vm"
    def reboot_vm(self,widget):
        print "reboot vm"
    
    def update_vm(self,widget):
        print "update vm"
    
    def delete_vm(self,widget):
        print "delete vm"
        
    def show(self):
        self.bind_events()
        
    def close(self,widget,data=None):
        gtk.main_quit()
    
    def bind_events(self):
        pass
    

