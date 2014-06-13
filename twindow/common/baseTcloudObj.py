#!coding:utf-8

from gobject import GObject
import gobject
import gtk


"""
    GObject 可以方便的写回调,由于gtk库和gone大量使用了这个库,有些时候我们就不用转换了
"""
class TcloudObject(GObject):
    
    def __init__(self):
        GObject.__init__(self)

        
    @staticmethod
    def type_register(*args, **kwargs):
        if not hasattr(gobject, "type_register"):
            return
        gobject.type_register(*args, **kwargs)

    @staticmethod
    def signal_new(klass, signal, args):
        
        gobject.signal_new(signal, klass,
                            gobject.SIGNAL_RUN_FIRST,
                            gobject.TYPE_NONE,
                            args)

    def on_error(self,msg,callback=None,master=None):
        m_dialog = gtk.MessageDialog(master, 0,
                                     gtk.MESSAGE_ERROR,
                                     gtk.BUTTONS_CLOSE, msg)
        if callback:
            m_dialog.connect("response",callback)
        else:
            m_dialog.connect("response", self._error_apply)
        m_dialog.run()

    def _error_apply(self,widget,response_id=None):
        widget.destroy()

    def __del__(self):
        if hasattr(GObject, "__del__"):
            getattr(GObject, "__del__")(self)
        