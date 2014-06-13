# -*- coding: utf-8 -*-
"""
    resource module
    @author: jay.han
"""
from twindow.common import config

conf = config.load_settings("client")
LANGUAGE_CODE = conf.get_int('language_code')
LANGUAGE_PREFIX={0:'cn',1:'en',2:'pk_cn'}
ResourceDict={
    "LOGIN_USER_LABEL" : [u'登录名',u'User',u'登录名'],
    "LOGIN_PASSWD_LABEL" : [u'密码',u'Password',u'密码'],

    "LOGIN_BUTTON" : [u'登录',u'Login',u'登录'],
    "LOGIN_MODE" : [u'登录模式',u'Login Mode',u'登录模式'],

    "LOGIN_VM_PROMT":[u'请选择你需要登录的桌面',u'Please select a desktop',u'请选择你需要登录的云PC'],
    "LOGIN_MODE_PROMT":[u'请选择你需要使用的场景',u'Please select a mode',u'请选择你需要使用的公共云PC'],
    "NETWORK_UNREACHABLE":[u'网络没有配置正确',u'API server is unreachable',u'网络没有配置正确'],
    "BUTTON_CANCEL" :[u'取消',u'Cancel',u'取消'],
    "BUTTON_OK" : [u'确定',u'Ok',u'确定'],
    "CONFIG_GATEWAY": [u'网关',u'gateway',u'网关'],
    "CONFIG_API":[u'服务器IP/端口',u'Host IP/Port',u'服务器IP/端口'],
    "CONFIG_TIMEOUT":[u'自动登陆时间',u'Auto Login timeout',u'自动登陆时间'],
    "CONFIG_IFACE":[u'网络接口',u'Interface',u'网络接口'],
    'CONFIG_NETMASK':[u"子网掩码",u'子网掩码',u'子网掩码'],
    "MODIFY_IP_LABEL":[u'修改配置',u'Config',u'修改配置'],
    "OLD_PWD":[u'旧密码',u'old pwd',u'旧密码'],
    "NEW_PWD":[u'新密码',u'new pwd',u'新密码'],
    "CONFIRM_PWD":[u'确认密码',u'confirm pwd',u'确认密码'],
    "START_VM_MSG" : [u'启动桌面失败',u'Fail to power on desktop',u'启动云PC失败'],
    "NO_MODE_MSG":[u'没有可用的场景实例',u'There is no available desktop now',u'没有可用的云PC'],

    "SELECT_VM_LABEL":[u'选择一个实例',u'Choose desktop',u'选择一个实例'],
    "SELECT_MODE_LABEL":[u"选择一个场景",u'Choose Mode',u"选择一个公共云PC"],
    "TOOLBAR":[u'工具栏',u'toolbar',u'工具栏'],
    "KILL_SESSION_MSG":[u'你被管理员中断了连接',u'Your session are Logout by administrator',u'你被管理员中断了连接'],
    "SERVER_ERROR_MSG" : [u"无法连接远程服务器, 请检查网络是否正常",u"Can't connect to Remote Server,Please check network configure"
        ,u"无法连接远程服务器, 请检查网络是否正常"],
    "CHANGE_PWD":[u'修改密码',u'modify password',u'修改密码'],
    "CHANGE_PWD_URI":[u'<a href="#">修改密码</a>',u'<a href="#">modify password</a>',u'<a href="#">修改密码</a>'],
    "INPUT_USERNAME":[u'请输入用户名',u'Please enter username',u'请输入用户名'],
    "INPUT_PASSWORD":[u'请输入密码',u'Please enter password',u'请输入密码'],
    "PASSWD_NOT_EQUAL":[u"密码不一致",u'Password not correct',u'密码不一致'],
    "INPUT_HOSTNAME_REQUIRE":[u'请输入正确的服务器ip和端口',u'Please enter valid hostname',u'请输入正确的服务器ip和端口'],
    "INPUT_NETWORK_INVALID":[u'请输入正确的网络配置信息',u'Please enter valid netowrk info',u'请输入正确的网络配置信息'],
    'CONFIG_IP':[u'IP',u'IP',u'IP'],
    "CONFIG_BUTTON":[u"配置",u'configure',u"配置"],
    "USER_MODE" : [u'教学桌面',u'Scene Mode',u'公共云PC'],
    "FREE_MODE" : [u'个人桌面',u'Free Mode',u'专属云PC'],
    "SHUTDOWN_VM":[u'关闭桌面',u'Shutdown Desktop',u"关闭云PC"],
    "REMMERBER_ME":[u'记住我',u'Remember Me',u'记住我'],
    "MODE_NAME":[u'场景名',u'Scene Name',u'公共云PC名'],
    "STATUS":[u"状态",u"Status",u"状态"],
    "VM_NAME":[u"桌面名",u"desktop Name",u"云PC名"],
    "VM_TYPE":[u"类型",u'OS Type',u"类型"],
    "NETWORK_ERROR":[u'网络错误,请检查网线以及IP是否配置正确',u'Network error,please check network configure',u'网络错误,请检查网线以及IP是否配置正确'],
    "SERVICE_NOT_USABLE":[u'远程服务器不可用',u"Remote Server is not available",u'远程服务器不可用'],
    "OE_COMPANY_INFO" : [u"噢易科技  2012-2013 © 版权所有",u'Openker Limited 2012-2013 @ all rights reserved',u"噢易科技  2012-2013 © 版权所有"],
    "PENGKE_COMPANY_INFO":[u"朋客云计算有限公司 2012-2013 @ 版权所有",u'Openker Limited 2012-2013 @ all rights reserved',u"朋客云计算有限公司 2012-2013 @ 版权所有"],
    "MANAGER_LABEL":[u"OE-VDI 客户端[终端名:%s][IP:%s]",u"Openker Client[Name:%s][IP:%s]",u"Openker 客户端[终端名:%s][IP:%s]"],

    "NEW" : [u"新增",u"New",u"新增"],
    "UPDATE": [u"更新",u"Update",u"更新"],
    "NOT_SELECTED" : [u"你没有选中任何记录",u"Please select a item",u"你没有选中任何记录"],
    "ERROR":[u"%(errors)s",u"%(errors)s",u"%(errors)s"],
    "SUCCESS":[u"操作成功",u"Operation Success",u"操作成功"]
    }

class Res(object):
    def __getattr__(self, item,language=LANGUAGE_CODE):
        return ResourceDict[item][language]


FREE_MODE = 0
CLASS_MODE= 1

INSTANCE_TEMPLATE=u"i-%08.f"

class PowerStatus:
    NOSTATE = 0x00
    RUNNING = 0x01
    BLOCKED = 0x02
    PAUSED = 0x03
    SHUTDOWN = 0x04
    SHUTOFF = 0x05
    CRASHED = 0x06


class Nth:
    ONE = 1
    TWO = 2
    THREE =3
    FOUR =4
    FIVE = 5
    SIX = 6

res_dict = Res()
