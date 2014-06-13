#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
from twindow.model.assist.page_base import PageBase

"""Introduction assistant page.
"""

# GTK+.
import pygtk; pygtk.require("2.0")
import gtk

# Base page.

class PageIntroduction(PageBase):
    """Introduction."""

    def __init__(self, assistant, page_name):
        super(PageIntroduction, self).__init__(assistant, page_name)
        
        # Header.
        label = self.header(page_name)
        self.add(label)

        # Introduction text.
        alignment = gtk.Alignment(xscale=1.0)
        alignment.set_padding(0, 0, 40, 0)
        vbox_labels = gtk.HBox(False,10)

        label = self.label("你可以在这里创建一些定时任务来确保系统能稳定运行 ")
        vbox_labels.pack_start(label,0,0)
        alignment.add(vbox_labels)
        self.add(alignment)

        self.show_all()