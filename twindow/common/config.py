#!coding:utf-8
"""
Routines for configuring 
"""

import logging.handlers
import sys,os
from twindow.common import utils
from twindow.common.ziploghandler import ZipRotatingFileHandler as zip_log
from ConfigParser import ConfigParser

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)8s [%(name)s] %(message)s"
DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(app_name,conf=None):
    """
    Sets up the logging options for a log with supplied name

    :param conf: Mapping of untyped key/values from config file
    """
    if not conf: conf = load_settings()

    # If either the CLI option or the conf value
    # is True, we set to True
    debug = conf.get_bool('twindow.debug')

    root_logger = logging.root
    if debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)


    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_LOG_DATE_FORMAT)

    logpath = conf.get('twindow.log.path')
    if logpath and not os.path.exists(logpath):
        os.makedirs(conf.get('twindow.log.path'))

    use_syslog = conf.get_bool('twindow.use_syslog')

    if use_syslog:
        handler = logging.handlers.SysLogHandler(address='/dev/log')
    elif logpath:
        logfile = os.path.join(logpath,"%s.log" % app_name)
        handler = zip_log(logfile,compress_mode='gz')
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

def _load_service_conf(app_name,filename):
    c = ConfigParser()
    try:
        c.read(filename)
        return dict(c.items(app_name)) if c.has_section(app_name) else {}
    except Exception as e:
        print 'can not read config of service : thor.conf',e
        sys.exit(-1)
    
def load_app_conf(app_name='all'):
   
    "we just need config what starts with app name and global configs"
    settings = load_settings(app_name)
    
    #setup up log
    setup_logging(app_name,settings)
    
    if settings.get_bool('twindow.debug'):
        logger = logging.getLogger(app_name)
        logger.debug("*" * 80)
        logger.debug("Configuration options gathered from db for: %s" % app_name)
        logger.debug("================================================")
        items = dict([(k, v) for k, v in settings.items()
                      if k not in ('__file__', 'here')])
        for key, value in sorted(items.items()):
            logger.debug("%(key)-30s %(value)s" % locals())
        logger.debug("*" * 80)
        
    return settings

configcache = {}#config cache

def load_settings(app_name="all",filepath='/etc/thor/twindow.conf',for_test=False):
    if configcache.has_key(app_name): return configcache[app_name]
    
    if not os.path.exists(filepath):
        thorPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        filepath = os.path.join(os.path.join(thorPath,os.pardir), "conf/twindow.conf")
        
    #测试用   
    if for_test:
        thorPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        filepath = os.path.join(os.path.join(thorPath, "tests/test.conf"))

    configmap = Config(dict())
    #update service host conf    
    configmap.update(_load_service_conf(app_name, filepath))
    
    configcache[app_name] = configmap
    return configmap


class Config(object):
    "模拟dict，增加类型转换的方法"
    def __init__(self,conf):
        self.conf = conf
    
    def __getitem__(self, name):
        if self.conf.has_key(name): return self.conf[name]

    def get_file_path(self):
        ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(ROOT_PATH,'../..', 'conf/twindow.conf'))

    def write_conf(self,values):
        utils.dict_updating(self.get_file_path(),values)

    def get(self,name,default=None):
        return self[name] if self[name] else default
    
    def update(self,otherdict):
        self.conf.update(otherdict)
        
    def items(self):
        return self.conf.items()
    
    def get_bool(self,name,default=False):
        return self._get_option(name,type='bool',default=default)
        
    def get_int(self,name,default=0):
        return self._get_option(name,type='int',default=default)
    
    def get_float(self,name):
        return self._get_option(name,type='float')
        
    def _get_option(self, option, **kwargs):
        if option in self.conf:
            value = self.conf[option]
            type_ = kwargs.get('type', 'str')
            if type_ == 'bool':
                if hasattr(value, 'lower'):
                    return value.lower() == 'true'
                else:
                    return value
            elif type_ == 'int':
                return int(value) if value else 0
            elif type_ == 'float':
                return float(value)
            else:
                return value
        elif 'default' in kwargs:
            return kwargs['default']
        else:
            raise KeyError("option '%s' not found" % option)
        
if __name__ == '__main__':
    pass
    #conf = load_settings(for_test=True)
    #print conf.items()