#!/usr/bin/env python
#!coding:utf-8
"""
    @author:jay.han
"""
import gtk,gobject
from twindow.common.baseTcloudObj import TcloudObject
from twindow.common import utils
from twindow.common.resource import res_dict


class ListModel(object):
    
    def __init__(self,rows):
        self.list_store = None
        self.rows = rows
        
    def get_model(self):
        """ Returns the model """
        if self.list_store:
            return self.list_store
        else:
            return None
    def remove_current(self):
        _, _iter = self.view.get_selection().get_selected()
        self.get_model().remove(_iter)
        
    def update_current(self,data_list,selected=False):
        """ update current table row or add new row """
        if selected:
            _, _iter = self.view.get_selection().get_selected()
            for i,data in enumerate(data_list):
                self.get_model().set_value(_iter,i,data)
        else:
            self.get_model().append(data_list) 
        
        
    def get_row(self):
        _, _iter = self.view.get_selection().get_selected()
        return self.get_model().get_path(_iter)[0]
        
    def get_selected(self,nth=0):
        """ Returns selected item in browser """
        model, _iter = self.view.get_selection().get_selected()
        
        if _iter != None:
            return model.get_value(_iter, nth)
        else:
            return None
    
        
    def add_data(self,data_list,selected=False):
        if data_list:
            first = data_list[0]
            if isinstance(first,list):
                for d in data_list:
                    self.update_current(d, selected)
            else:
                self.update_current(data_list, selected)
    #Main method
    def init_data_list(self,widget,data_list):
        for i,head in enumerate(self.head_list):
            column = gtk.TreeViewColumn(head, gtk.CellRendererText(), text=i)   
            column.set_spacing(10)
            widget.append_column(column)
            
        self.add_data(data_list)     
        
    def make_view( self, widget=None ,data_list=None):
        """ Form a view for the Tree Model """
        if not widget:
            self.view = gtk.TreeView()
        else:
            self.view = widget
        self.view.set_model(self.list_store)
        self.init_data_list(self.view,data_list)
        self.view.expand_all()
        return self.view    
    
class TaskModel(ListModel):  
    def __init__(self,rows=None):
        super(TaskModel,self).__init__(rows)
        self.list_store = gtk.ListStore(str,str,gtk.gdk.Pixbuf,str,str)
        self.head_list = ["名称","类型","状态","间隔","开始时间"]
        return
    
    def init_data_list(self,widget,data_list):
        for i,head in enumerate(self.head_list):
            if head == "状态":
                column = gtk.TreeViewColumn(head)
                pix =gtk.CellRendererPixbuf()
                column.pack_start(pix, expand=False)   
                column.add_attribute(pix, 'pixbuf', i)
            else:
                column = gtk.TreeViewColumn(head, gtk.CellRendererText(), text=i)  
            column.set_spacing(10)
            widget.append_column(column)
            
        self.add_data(data_list)
        
class UserModel(ListModel):
    def __init__(self,rows=None):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["学号","用户名","性别","所属院系","电子邮件","联系方式","上次登录ip地址","创建时间"]
        return
    
class ClassModel(ListModel):
    def __init__(self,rows=None):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["系名","系描述","所属系"]
        return
    
class DepartmentModel(ListModel):
    def __init__(self,rows=None):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["系名","系描述","所属院"]
        return
    
class SchoolModel(ListModel):
    def __init__(self,rows=None):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["学院名","学院描述"]
        return
    
class HostListModel(ListModel):
    """ The model class holds the information we want to display """
    def __init__(self,rows):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["主机名","主机ip","状态","所属","负载","cpu","内存","磁盘空间","虚拟机数量"]
        return
    
class DiskListModel(ListModel):
    """ The model class holds the information we want to display """
    def __init__(self,rows):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING)
        self.head_list = ["名称","描述","类型","使用率","大小"]
        
"""
    @todo: 合并这两个model
"""  
class VMListModel(ListModel):  
    def __init__(self,rows):
        """ Sets up and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING,
                                        gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        
        self.head_list = ["实例名","实例ip","状态","镜像","操作系统","cpu","内存","磁盘空间","用户"]

class VMListModelShort(ListModel):
    def __init__(self,rows=None):
        """ VM list short and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gtk.gdk.Pixbuf,gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING)
        
        self.head_list = [res_dict.STATUS,res_dict.VM_NAME,res_dict.VM_TYPE]

    def init_data_list(self,widget,data_list):
        for i,head in enumerate(self.head_list):
            if head == res_dict.STATUS:
                column = gtk.TreeViewColumn(head)
                pix =gtk.CellRendererPixbuf()
                column.pack_start(pix, expand=False)   
                column.add_attribute(pix, 'pixbuf', i)
            else:
                column = gtk.TreeViewColumn(head, gtk.CellRendererText(), text=i)  
            column.set_spacing(10)
            widget.append_column(column)
            
        self.add_data(data_list)


class ModeModel(ListModel):
    def __init__(self,rows=None):
        """ VM list short and populates our gtk.TreeStore """
        ListModel.__init__(self,rows)
        self.list_store = gtk.ListStore(gobject.TYPE_STRING,gobject.TYPE_STRING)

        self.head_list = [res_dict.MODE_NAME]



        
LABEL = gtk.Label
class LabelModel(LABEL):     
    def __init__(self,label,x=0.5,y=0.5,width=117,font=10,height=-1,visible=True):
        # size; 38000 = 38pt (use pt size * 1000)
        self.font_size = font * 1000
        label = "<span size='%s'> %s</span>"  %(self.font_size,label)
        LABEL.__init__(self,label)
        self.x = x or 0.0
        self.y = y or 0.0
        
        self.set_alignment(xalign=self.x,yalign=self.y)
        self.set_size_request(width=width,height=height)
        self.set_use_markup(True)

        #self.set_visible(visible)
    def update_text(self,text):
        label = "<span size='%s'> %s</span>"  %(self.font_size,text)
        self.set_markup(label)

    def error_text(self,text):
        self.set_markup('<span color="red">'+text+'</span>')



class ErrorLabelModel(LabelModel):

    def __init__(self,label,x,y):
        LabelModel.__init__(self,label,x,y,font=6)

    def error_text(self,text):
        self.set_size_request(width=300,height=-1)
        self.set_markup('<span color="red">'+text+'</span>')
    
ENTRY = gtk.Entry
class EditModel(ENTRY):
    def __init__(self,max=0,width=120,vis=True,text=None,visible=True,default=None):
        ENTRY.__init__(self,max)
        self.set_visibility(vis)
        #self.set_visible(visible)
        self.set_width_chars(max)
        self.set_size_request(width=width,height=-1)
        if text:
            self.set_text(text)
        elif default:
            self.set_text(default)
    def disable_text(self,text):
        self.set_text(text if text else "")
        self.set_editable(False)
        
    def is_empty(self):
        return self.get_text().strip() == ""
    
    def not_empty(self):
        return self.get_text().strip() != ""
    
    def clear(self):
        self.set_text("")
        self.set_editable(True)
        
TABLE = gtk.Table
class TableModel(TABLE): 
    def __init__(self,row,col):
        TABLE.__init__(self,row,col,False)
    
    def init_rc_data(self,data,base_x=0,base_y=0):
        for i ,_ in enumerate(data):
            for j,real in enumerate(data[i]):
                self.fill_in(real,base_x+i,base_x+i+1,base_y+j,base_y+j+1,xpadding=4,ypadding=4)
                
    def init_data_fill(self,data):
        for i ,_ in enumerate(data):
            for j,real in enumerate(data[i]):
                self.fill_in(real,i,i+1,j,j+1,gtk.FILL,gtk.FILL,xpadding=5,ypadding=5)
    
    def fill_in(self,obj,lx,rx,ly,ry,xoptions=gtk.EXPAND|gtk.FILL, yoptions=gtk.EXPAND|gtk.FILL, xpadding=5, ypadding=5):
        
        self.attach(obj,lx,rx,ly,ry,xoptions=xoptions, yoptions=yoptions,xpadding=xpadding, ypadding=ypadding)

    def refresh_data(self,data,lx,rx,ly,ry):
        self.fill_in(data,lx,rx,ly,ry)

"""
    select box
"""
class SelectWidget(object):
    def __init__(self):
        self.list_store = gtk.ListStore(str,str,str,int)
        self.view = None
        self.first = True
        
    def is_first(self):
        return self.first
    
    def get_model(self):
        """ Returns the model """
        if self.list_store:
            return self.list_store
        else:
            return None
        
    def init_data_list(self,widget,data_list):
        self.first = False
        for d in data_list:
            self.get_model().append(d)    
            
    def get_selected(self,nth):
        _iter = self.view.get_active_iter()
        if _iter:
            return self.get_model().get_value(_iter, nth)
        else:
            return None
    def clear(self):
        self.view.set_active(0)
    
    def select(self):
        pass
    
    def disable_text(self,text):
        self.view.set_active(int(text))
        
        
    def make_view(self,data_list):
        
        self.view = gtk.ComboBox()

        self.view.set_model(self.list_store)
        self.init_data_list(self.view, data_list)
        # self.view.set_text_column(0)
        self.view.set_active(0)
        cell = gtk.CellRendererText()
        cell.set_property('width',200)
        self.view.pack_start(cell, True)

        self.view.add_attribute(cell, "text", 0)
        self.view.show_all()
        return self.view
        
class SimpleSelectWidget(SelectWidget):
    def __init__(self):
        SelectWidget.__init__(self)
        self.list_store = gtk.ListStore(str,int)
        
"""
    ICON Widget
"""
class IconWidget(object):
    
    def __init__(self,name=None,stu_count=0):
        self.model = gtk.ListStore(str,gtk.gdk.Pixbuf,str,str,str)
        self.view = None
        self.count = 0
        self.stu_count_all = stu_count
        self.up_count = 0
        self.stu_count =0
        self.own = name
    
    def get_model(self):
        """ Returns the model """
        if self.model:
            return self.model
        else:
            return None
    def get_stu_more(self):
        return self.stu_count_all - self.stu_count
    def get_stu(self):
        return self.stu_count
    def get_count(self):
        return self.count
    
    def get_up_count(self):
        return self.up_count
    
    def get_off_count(self):
        return self.count - self.up_count
    
    def get_view(self):
        if not self.view:
            self.view = gtk.IconView()
        return self.view
    
    def init_data(self,data):
        
        self.model_clear()
        # self.model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.up_count = 0
        self.count = 0
        self.stu_count = 0
        if data :
            
            for r in data: 
                self.count = self.count + 1
                if r['client_name'] == self.own or r['is_teacher_client']:
                    continue 
                self.up_count = int(r['status']) + self.up_count
                
                if r['status'] and r['user_id']:
                    self.stu_count = self.stu_count + 1
                name = "poweron.ico" if r['status']  else "poweroff.ico"
                pixbuf = utils.get_pixbuf_from_file(name,40)
                #utils.is_up
                self.model.append(["终端 %s " % r['client_name'], pixbuf,r['client_ip'],
                                                r["client_mac"],r["id"]])
                
        return self.model
    
    
        
    def get_selected(self,path,nth):
        
        _iter = self.model.get_iter(path)
        if _iter:
            return self.model.get_value(_iter, nth)
        else:
            return None

    def model_clear(self):
        self.model.clear()

    def make_view(self,data,single=False):
        
        self.view = gtk.IconView(self.init_data(data))
        if not single:
            self.view.set_selection_mode(gtk.SELECTION_MULTIPLE)
        else:
            self.view.set_selection_mode(gtk.SELECTION_SINGLE)
        self.view.set_text_column(0)
        self.view.set_pixbuf_column(1)
        self.view.show_all()
        return self.view
    
class ToolbarItem(object):
    
    def __init__(self,name,tooltip,tooltip_info,image,func,data=None):
        self.name = name
        self.tooltip = tooltip
        self.tooltip_info = tooltip_info
        self.func = func
        self.image = image
        self.data = data
        self.item_list = []
        
    def add_items(self,item):
        self.item_list.append(item)
        
class MenuItem(object):
    def __init__(self,icon,name,key):
        self.icon = icon
        self.name = name
        self.key = key
        self.sub_menu = []
    
    def add_sub_menu(self,sub):
        self.sub_menu.append(sub)
    
    def update_sub_menu(self,sub):
        for s in self.sub_menu:
            if s.key == sub.key:
                s.name = sub.name
                s.icon = sub.icon    
    
        
    
class MenuTree(TcloudObject):
    __gsignals__ = { 
                     'cursor-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_STRING,))
                     }
    def __init__(self,menu,root=None):
        """ Sets up and populates our gtk.TreeStore """
        TcloudObject.__init__(self)
        self.tree_store = gtk.TreeStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.root = self.init_root(root)
        self.menu = menu
        self.first_row  = None
        self.init_menu(self.menu)
        return
    
        
    def update_model(self,data_list):
        self.tree_store.clear()
        self.init_menu(data_list)
        self.view.expand_all()
            
    def init_root(self,root):
        if root:
            return self.tree_store.append(None,(root.icon,root.name,root.key))
        return None
    
    def get_selected(self,nth=2):
        """ Returns selected item in browser """
        model, iter = self.view.get_selection().get_selected()
        if iter != None:
            return model.get_value(iter, nth)
        else:
            return None
    
    def make_firs_elem_selected(self):
        
        _, _iter = self.view.get_selection().get_selected()
        if _iter == None:
            self.view.expand_to_path(self.first_row)
            
            
    """
        callback function
    """
    def cursor_changed(self, treeview):
        """ CALLBACK: a new row has been selected """
        model, _iter = treeview.get_selection().get_selected()
        
        # Send signal with path of expanded row
        
        if _iter == None:
            path = treeview.get_cursor()[0]
            _iter = self.tree_store.get_iter(path)
        
        self.emit('cursor-changed', model.get_value(_iter,2))
        
    """
        menu = MenuItem
    """
    def get_first_selected(self):
        return self.menu[0].name
    
    def init_menu(self,menu):
        if_first = True
        for item in menu:
            if self.root:
                parent = self.tree_store.append( self.root, (item.icon,item.name, item.key) )
            else:
                parent = self.tree_store.append( None, (item.icon,item.name, item.key) )
            ############sub menu ########################################################
            for i in item.sub_menu:
                if if_first:
                    _iter = self.tree_store.append( parent, (i.icon,i.name, i.key))
                    self.first_row  = self.tree_store.get_path(_iter)
                    if_first = False
                else:
                    self.tree_store.append( parent, (i.icon,i.name, i.key))
            
    """ Displays the Info_Model model in a view """
    def make_view( self,expend=True):
        """ Form a view for the Tree Model """
        self.view = gtk.TreeView(self.tree_store)
        self.view.set_headers_visible(False)
     
        self.view.set_reorderable(False)
        col = gtk.TreeViewColumn()   
         
        render_pixbuf = gtk.CellRendererPixbuf()
        col.pack_start(render_pixbuf, expand=False)
        col.add_attribute(render_pixbuf, 'pixbuf', 0)
        
        render_text1 = gtk.CellRendererText()
        col.pack_start(render_text1, expand=True)
        col.add_attribute(render_text1, 'text', 1)
        ############# hidden cell ##################
        render_text2 = gtk.CellRendererText()
        #render_text2.set_visible(False)
        col.pack_start(render_text2, expand=False)
        col.add_attribute(render_text2, 'text', 2)
        
        if expend:
            self.view.expand_all()
        else:
            self.make_firs_elem_selected()
        self.view.connect('cursor-changed', self.cursor_changed)
        
        self.view.append_column(col)
        self.view.show()
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled.add(self.view)
        scrolled.show()
        
        return self.view,scrolled
    
TcloudObject.type_register(MenuTree)
