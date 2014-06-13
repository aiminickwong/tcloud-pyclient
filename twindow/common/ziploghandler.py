#! coding:utf-8
#!/usr/bin/env python
"""
    @author: jay
"""
import os,time
from logging.handlers import TimedRotatingFileHandler


COMPRESSION_SUPPORTED = {}

"""
    check if we support gzip or zip
"""
try:
    import gzip
    COMPRESSION_SUPPORTED['gz'] = gzip
except ImportError:
    pass

try:
    import zipfile
    COMPRESSION_SUPPORTED['zip'] = zipfile
except ImportError:
    pass

"""
    zipRotating
"""
class ZipRotatingFileHandler(TimedRotatingFileHandler):
    
    def __init__(self, *args, **kws):
        compress_mode=kws.pop("compress_mode")
        try:
            self.compress_cls = COMPRESSION_SUPPORTED[compress_mode]
        except KeyError:
            raise ValueError('"%s" compression method not supported.' % compress_mode)
        
        TimedRotatingFileHandler.__init__(self,when='D', *args, **kws)
    
    def doRollover(self):
        """ get orginal file """
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        old_log = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        super(ZipRotatingFileHandler, self).doRollover()
        with open(old_log) as log:
            with self.compress_cls.open(old_log + '.gz', 'wb') as comp_log:
                comp_log.writelines(log)
        os.remove(old_log)