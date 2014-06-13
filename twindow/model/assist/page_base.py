#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""Base assistant page.
"""

# GTK+.
import pygtk; pygtk.require("2.0")
import gtk
from gtk import gdk
import gobject

class PageBase(gtk.Frame):
    """Base functionaility for gtk.Assistant pages."""

    __gsignals__ = {
        "ready": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }    

    trigger_expose = False

    def __init__(self, assistant, page_name):
        # type, title and complete can only be called after the page has
        #   been appended to a gtk.Assistant.
        super(PageBase, self).__init__()
        
        self.assistant = assistant
        self.page_name = page_name
        
        self.set_border_width(10)
        self.set_shadow_type(gtk.SHADOW_NONE)
        # Make sure the child widgets try to use the full width of the dialog.
        align = gtk.Alignment(yalign=0.0, xscale=1.0)
        super(PageBase, self).add(align)
        # Layout container.
        self.vbox = gtk.VBox(False, 10)
        align.add(self.vbox)
        self.connect("expose_event", self.exposed)
        assistant.connect_after("prepare", self.activate_expose)

    def remove_all(self):
        for child in self.vbox.get_children():
            self.vbox.remove(child)

    def add(self, widget):
        self.vbox.pack_start(widget)

    def get_type(self):
        return self.assistant.get_page_type(self)
    def set_type(self, type):
        self.assistant.set_page_type(self, type)
    type = property(get_type, set_type)

    def get_title(self):
        return self.assistant.get_page_title(self)
    def set_title(self, title):
        self.assistant.set_page_title(self, title)
    title = property(get_title, set_title)
    
    def get_complete(self):
        return self.assistant.get_page_complete(self)
    def set_complete(self, complete):
        self.assistant.set_page_complete(self, complete)
    complete = property(get_complete, set_complete)

    # Label functions.

    def header(self, text, label=None):
        text = "<big><b>%(text)s</b></big>" % {"text": text}
        if label:
            return self.label(text, wrap=False, label=label)
        else:
            return self.label(text, wrap=False)

    def label(self, text, wrap=True, label=None):
        if not label:
            label = gtk.Label(text)
            label.set_alignment(0.0, 0.0)
            label.set_use_markup(True)
        else:
            label.set_use_markup(True)
            label.set_label(text)
        label.set_line_wrap(wrap)
        return label

    def bordered_label(self, text):
        align = gtk.Alignment(xscale=1.0)
        align.set_padding(0, 0, 20, 20)
        frame = gtk.Frame(None)
        frame.set_shadow_type(gtk.SHADOW_IN)
        label = self.label(text)
        label.set_selectable(True)
        label.modify_fg(gtk.STATE_NORMAL, gdk.color_parse("#00FF00"))
        alignment = gtk.Alignment(yalign=0.5, xscale=1.0)
        alignment.set_padding(5, 5, 5, 5)
        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gdk.color_parse("#555555"))
        eventbox.add(alignment)        
        alignment.add(label)
        frame.add(eventbox)
        align.add(frame)
        return align

    # Signal handlers.
    def exposed(self, widget, event):
        """Called when the page is being exposed."""
        # Because the gtk.Assistant has no signal for telling us when a page
        #   is actually being shown (as opposed to `about to be shown', which
        #   is what the `prepare' signal does), we depend on the expose event
        #   of a widget on that page. Because expose is constantly triggered
        #   when the page is shown, we use a flag to make sure it only
        #   triggers the first time.
        if self.trigger_expose:
            self.trigger_expose = False
            self.emit("ready")

    def activate_expose(self, assistant, page):
        """Called when the assistant is about to change pages."""
        # If we are the next page, enable our `ready' signal
        if page.page_name == self.page_name:
            self.trigger_expose = True
