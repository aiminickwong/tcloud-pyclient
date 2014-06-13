#!/usr/bin/env python
#!coding:utf-8
# GTK+.
import pygtk; pygtk.require("2.0")
import gtk
from gtk import gdk
import gobject

from twindow.model.assist.page_info import PageIntroduction
from twindow.model.assist.page_prograss import PageProgress
from twindow.model.assist.page_confirm import PageConfirm
from twindow.model.assist.page_detail import PageDetail, PageDetail_Task



"""
    Jay.Han
"""
class Schedule_Assistant(gtk.Assistant):
    """Assistant for installing.
    """
    def __init__(self):
        super(Schedule_Assistant, self).__init__()

        self.current_page = None

        self.set_title("计划任务")
        self.set_modal(True)
        self.is_closed = False
        # Variables that we fill in using the user's input.
        self.action = None
        self.url = None

        
        self.pages = {"intro": "介绍",
                      "confirm":"完成",
                      "detail":"选择任务类型",
                      "task":"描述课堂信息",
                      }
        # Introduction, explain what we are going to do.
        intro = PageIntroduction(self, self.pages['intro'])
        self.append_page(intro)
        intro.type = gtk.ASSISTANT_PAGE_INTRO
        intro.complete = True
        intro.set_title("欢迎使用计划任务向导")
        
        
        detail1 = PageDetail(self, self.pages["detail"])
        self.append_page(detail1)
        detail1.type = gtk.ASSISTANT_PAGE_CONTENT
        detail1.complete = True
        detail1.set_title("任务类型")
        
        self.task = PageDetail_Task(self,self.pages['task'])
        self.append_page(self.task)
        self.task.type = gtk.ASSISTANT_PAGE_CONTENT
        self.task.complete = True
        self.task.set_title("课堂信息")
        
        # Show the progress of the download and install.
        progress = PageProgress(self, "进行中")
        self.append_page(progress)
        progress.type = gtk.ASSISTANT_PAGE_PROGRESS
        
        # Show a summary of the actions that will be performed.d
        confirm = PageConfirm(self, self.pages["confirm"])
        self.append_page(confirm)
        confirm.type = gtk.ASSISTANT_PAGE_CONFIRM
        confirm.title = "完成"
        
        # Show the result of what was done.

       

        self.set_forward_page_func(self.forward_page, None)

        # Connect signal handlers.
        self.connect("delete_event", self.close)
        self.connect("cancel", self.close)
        self.connect("close", self.close)
        self.connect("prepare", self.prepare_action)
        progress.connect("ready", self.progress_page_ready)


    # Event handlers.

    def close(self, *args):
        self.is_closed = True
        self.destroy()

    def prepare_action(self, assistant, page):
        """Called just before `page' will be shown to the user."""
        name = page.page_name
        
        self.current_page = name
        # Reset the cursor. Previous pages may have set it indicate being busy.
        self.window.set_cursor(None)
        if name == self.pages["confirm"]:
            page.complete = True
            print "confirm"
        elif name == "progress":
            print "progress"
        elif name == self.pages["task"]:
            if self.task.is_add():
                self.task.check_input()
                page.complete = False
                print "add"
            else:
                pass
            
    
    def progress_page_ready(self, page):
        """Called when the progress page is shown to the user, and is ready to
           be used.
        """
        self.window.set_cursor(gdk.Cursor(gdk.WATCH))
        gobject.timeout_add(10, self._asyn_api_call)
        
    
    def _asyn_api_call(self,widget=None):
            
        self.set_current_page(self.get_current_page() + 1)
        
        
    # Forward page.
    def forward_page(self, page_number, data):
        """Determine what the next page will be."""
        
        return page_number + 1
    
if __name__=="__main__":
    Schedule_Assistant().show_all()
    gtk.main()