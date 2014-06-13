# -*- coding: utf-8 -*-
"""
    @author: jay.han
"""
from twindow.common.resource import res_dict as Resource

"""
    @TODO Message
"""
class Error(Exception):
    message = "An unknown exception has occurred. please contact us"
    def __init__(self, message=None,**kwargs):
        if not message:
            message = self.message % kwargs
        super(Error, self).__init__(message)
        
class MountException(Error):
    message = "远程存储挂载错误" 
            
class ApiError(Error):
    def __init__(self, message='Unknown', code='Unknown'):
        self.message = message
        self.returncode = code
        super(ApiError, self).__init__('%s: %s' % (code, message))

class RemoteServerException(Error):
    message = Resource.SERVICE_NOT_USABLE


class NetworkException(Error):
    message = Resource.NETWORK_ERROR

class BusinessException(Error):
    message=Resource.ERROR

