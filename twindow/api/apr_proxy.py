#!/usr/bin/env python
#!coding:utf-8
# vim: tabstop=4 shiftwidth=4 softtabstop=4
"""
    @author jay.han
"""
from twindow.common.exception import ApiError, BusinessException, RemoteServerException
import logging
from twindow.common.resource import res_dict as Resource

LOG = logging.getLogger(__name__)

class api_proxy(object):

    def __init__(self):
        self.proxy = None

    def _refresh_proxy(self,uri=None):
        try:
            from twindow.api.api import TcloudMethodProxy
            is_changed = True if uri else False
            if not self.proxy:
                self.proxy = TcloudMethodProxy(is_changed=is_changed,uri=uri)
        except:
            self.on_error(Resource.SERVER_ERROR_MSG)
            LOG.exception("api server not avaliable this time")

    def _clean_up(self):
        pass
        #self.proxy = None

    def api_proxy(self,method,**args):
        self._refresh_proxy()
        #LOG.debug("requesting method is %s" % method)
        try:
            return self.proxy(method=method,**args)
        except RemoteServerException as e:
            LOG.exception("api server RemoteServer issue %s" % e)
            raise e
        except BusinessException as e:
            raise e
        except ApiError as e:
            LOG.exception("api server 500 error,please check log for detail")
            raise e

    def api_proxy_no_cache(self,method,**args):
        self.api_proxy(method,no_cache=True,**args)

    def logout_api(self,data):
        return self.api_proxy(method="auth_logout",data=data)

    def logout_api_v2(self,data):
        return self.api_proxy(method='auth_logout_V2',data=data)

    def login_api(self,data):
        return self.api_proxy(method="auth_login",data=data)

    def shutdown_vm_api(self,data):
        return self.api_proxy(method="vm_poweroff",data=data)

    def vm_connect_api(self,data):
        return self.api_proxy(method="vm_connect",data=data)

    def select_mode_api(self,data):
        return self.api_proxy(method='select_mode',data=data)

    def register(self,data):
        return self.api_proxy(method='client_register',data=data)

    def keep_alive(self,data):
        return self.api_proxy(method='client_keep_live',data=data)

    def get_login_name(self,data):
        return self.api_proxy(method="client_get_login_name",data=data)

    def change_pwd(self,data):
        return self.api_proxy(method="user_change_pwd",data=data)

api = api_proxy()