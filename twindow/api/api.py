# -*- encoding: utf-8 -*-

import urllib2
import urllib
import json

from cache import SimpleCache
from twindow.common.exception import ApiError, RemoteServerException, BusinessException, NetworkException
from twindow.common import config, resource

import logging

conf = config.load_settings("client")
LANGUAGE_CODE = conf.get_int('language_code')
HTTP_DEBUG = conf.get_int('http_debug')


"""
    @author: jay.han
    @module : api
"""
LOG = logging.getLogger("twindow.api")
API_KEY = None
API_SECRET = None
REST_URL = "http://"+conf["api_server"]
CACHE = None
__methods__ ={}

def change_url(uri):
    REST_URL = "http://"+ uri

def enable_cache(cache_object = None):
    global CACHE
    if not CACHE:
        CACHE = cache_object or SimpleCache()

def disable_cache():
    global CACHE
    CACHE = None
    

def clean_args(args):
    """
        Reformat the arguments.
    """
    for k,v in args.items() :
        if isinstance(v,bool):
            args[k] = int(v)

def request(url,data=None):
    req = urllib2.Request(url,data,headers={'Accept-Language': resource.LANGUAGE_PREFIX[LANGUAGE_CODE] })
    #Debug
    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=HTTP_DEBUG))
    try :
        return opener.open(req,timeout=60).read()
    except urllib2.HTTPError as e:
        if e.code == 500:
            raise RemoteServerException()
        elif e.code != 200:
            raise ApiError(message=e)
    except urllib2.URLError as e:
        raise NetworkException()
    except Exception as e:
        raise ApiError(message=e)
    finally:
        opener.close()
    
def _get_methods(uri=None):

    if not uri:uri = REST_URL

    if len(__methods__) > 1:
        return __methods__

    try:
        resp = request(uri)
    except:
        LOG.exception('first trying ....')
        # try again
        try:
            resp = request(uri)
        except:
            LOG.exception('second trying ....')
            resp = request(uri)

    try :
        resp = json.loads(resp)

    except ValueError,e:
        raise e
    for r in resp:
        if r == "/":
            continue
        else:
            m = r.split("/")[1] + "_" +r.split("/")[2] 
            __methods__[m] = r
    return __methods__

try:
    __methods__ = _get_methods()
except:
    __methods__ = {}
    pass


class TcloudMethodProxy(object):
    """
        Proxy object to perform seamless direct calls to 
        API.
    """
    def __init__(self,is_changed=False,uri=None):
        if is_changed:
            change_url(uri)
        self.__dict__ = _get_methods(uri)

        
    def __call__(self,method=None,**kargs):
        
        path = self.__dict__[method]
        return call_api(method_path=path,**kargs)


def call_api(api_key = None, api_secret = None,method_path=None,
                 **args):

    request_url = REST_URL
    if not api_key :
        api_key = API_KEY
    if not api_secret :
        api_secret = API_SECRET

    request_url= request_url + method_path
    
    #clean_args(args)
    data = args.pop("data",None)
    is_stream = args.pop("is_stream",False)
    no_cache = args.pop("no_cache",True)
    
    
    if data:
        data = urllib.urlencode(data)
        
    resp = request(request_url,data)

    if not is_stream:
        try:
            resp = json.loads(resp)
        except ValueError,e :
            raise e
    
    return check_resp(resp)

def check_resp(resp):
    if 'error' in resp:
        raise BusinessException(errors=resp['error'])
    return resp

if __name__ == "__main__":
    t = TcloudMethodProxy()
    print t.__dict__
    
    
