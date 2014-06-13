#!/usr/bin/env python
#!coding:utf-8

import gtk
parentClass = gtk.MessageDialog

class TcloudErrorMessage(parentClass):
    def __init__(self,msg):
        parentClass.__init__(self, 
            gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_ERROR, 
            gtk.BUTTONS_CLOSE, msg)
        
    