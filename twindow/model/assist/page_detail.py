#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
from twindow.model.assist.page_base import PageBase
from twindow.model.tcloudModel import TableModel, LabelModel, SimpleSelectWidget,\
    EditModel
from twindow.api import t_api


"""
    Detail assistant page.
"""

# GTK+.
import pygtk; pygtk.require("2.0")
import gtk

# Base page.

class PageDetail(PageBase):
    """Detail"""
    def __init__(self, assistant, page_name):
        super(PageDetail, self).__init__(assistant, page_name)
        
        # Header.
        label = self.header(page_name)
        self.add(label)

        # Introduction text.
        alignment = gtk.Alignment(xscale=1.0)
        alignment.set_padding(0, 0, 40, 0)
        vbox_labels = gtk.VBox(False,10)

        
        #Detail content
        self.select = SimpleSelectWidget()
        self.select.make_view(self._pop_mission_up())
        
        vbox_labels.pack_start(self.select.view,1,1)
        # end of detail
        
        alignment.add(vbox_labels)
        self.add(alignment)

        self.show_all()
    
    def get_select(self):
        return self.select.get_selected(1)
    
    def _pop_mission_up(self):
        return [["排课排任务",0],["系统任务",1]]
    
class PageDetail_Task(PageBase):
    """Task."""
    def __init__(self, assistant, page_name):
        super(PageDetail_Task, self).__init__(assistant, page_name)
        # Header.
        label = self.header(page_name)
        self.add(label)
        
        
        # Introduction text.
        alignment = gtk.Alignment(xscale=1.0)
        alignment.set_padding(0, 0, 40, 0)
        vbox_labels = gtk.VBox(False,10)
        
        table = TableModel(5,2)
        self.select = SimpleSelectWidget()
        
        self.teacher = EditModel(max=25)
        self.class_info = EditModel(max=25)
        self.class_desc = EditModel(max=25)
        self.user_count = EditModel(max=25)
        self.class_time = EditModel(max=25)
        
        
        data = [[LabelModel("课堂信息: ",0.5,0),
                 LabelModel("授课老师: ",0.5,0),
                 LabelModel("课程信息: ",0.5,0),
                 LabelModel("课程备注: ",0.5,0),
                 LabelModel("人数: ",0.5,0),
                 LabelModel("上课时间: ",0.5,0)],
                [self.select.make_view(self._pop_class_up()),
                 self.teacher,
                 self.class_info,
                 self.class_desc,
                 self.user_count,
                 self.class_time,
                 ]]
        
        self.select.view.connect("changed",self._change_value)
        table.init_rc_data(data)
        vbox_labels.pack_start(table,1,1)
        # end of detail
        
        alignment.add(vbox_labels)
        self.add(alignment)

        self.show_all()
    
    def check_input(self):
        print self.teacher.is_empty()
        
    def is_add(self):
        return self.select.get_selected(1) == 0
    
    def _change_value(self,src):
        select = self.select.get_selected(1)
        if select:
            result = t_api(method="dict_teaching_get",data={"teaching_id":select}) 
            
            self.teacher.disable_text(result['teacher'])
            self.class_info.disable_text(result['class_name'])
            self.class_desc.disable_text(result['class_desc'])
            self.user_count.disable_text(str(result['user_count']))
            self.class_time.disable_text(result['teaching_time'])
            
    
    def _pop_class_up(self):
        return [["新增",0],["autocad 教学",1],["photoshop 教学",2]]
    
    