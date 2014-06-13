#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
from twindow.model.assist.page_base import PageBase
from twindow.model.tcloudModel import LabelModel

"""
     assistant page.
"""

# GTK+.
import pygtk; pygtk.require("2.0")
import gtk
from gtk import gdk

class PageProgress(PageBase):
    
    status_labels = dict()

    def __init__(self, assistant, page_name):
        super(PageProgress, self).__init__(assistant, page_name)
        
        # Header.
        label = self.header(page_name)
        self.add(label)
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_pulse_step(0.001)
        self.add(self.progress_bar)
        vbox_status = gtk.VBox(False, 5)
        label = LabelModel("Downloading stroke data")
        vbox_status.pack_start(label)
        self.status_labels["download"] = label
        label = LabelModel("Installing stroke data")
        vbox_status.pack_start(label)
        self.status_labels["install"] = label
        self.add(vbox_status)

        self.show_all()

    def hide_label(self, name):
        try:
            self.status_labels[name].hide_all()
        except KeyError:
            print "Label not found"

    def set_status(self, status):
        for label in self.status_labels:
            if label == status:
                self.status_labels[label].active = True
            else:
                self.status_labels[label].active = False

