#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from twindow.model.assist.page_base import PageBase
from twindow.model.tcloudModel import LabelModel

"""Confirmation assistant page.
"""

# GTK+.
import pygtk; pygtk.require("2.0")
import gtk
from gtk import gdk


class PageConfirm(PageBase):


    def __init__(self, assistant, page_name):
        super(PageConfirm, self).__init__(assistant, page_name)
        
        confirm = gtk.VBox()
        
        confirm.pack_start(LabelModel("12312312"),1,1)
        
        self.add(confirm)
        
        self.show_all()


