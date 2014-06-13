#!/usr/bin/env python
#!coding:utf-8
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
    @author jay.han
"""
import gobject

import dbus
import dbus.service
import dbus.mainloop.glib

class DemoException(dbus.DBusException):
    _dbus_error_name = 'com.tcloud.Exception'

class TcloudGtkObject(dbus.service.Object):

    @dbus.service.method("com.tcloud.Interface",
                         in_signature='s', out_signature='as')
    def killSession(self, hello_message):

        self.gtk_obj.killSession()
        return ['True']

    @dbus.service.method("com.tcloud.Interface",
                         in_signature='', out_signature='as')
    def close_manager(self):
        self.gtk_obj.close_manager()
        return ['True']

    @dbus.service.method("com.tcloud.Interface",
                         in_signature='', out_signature='as')
    def Shutdown(self):
        self.gtk_obj.logout()
        return ['True']

    @dbus.service.method("com.tcloud.Interface",
                         in_signature='', out_signature='')
    def RaiseException(self):
        raise DemoException('The RaiseException method does what you might '
                            'expect')

    @dbus.service.method("com.tcloud.Interface",
                         in_signature='', out_signature='')
    def Exit(self):
        mainloop.quit()

    def set_gtk_obj(self,obj):
        self.gtk_obj = obj


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName("com.tcloud.gtkService", session_bus)
    object = TcloudGtkObject(session_bus, '/gtkObject')


    object.set_gtk_obj()

    mainloop = gobject.MainLoop()
    mainloop.run()
