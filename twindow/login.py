#!coding:utf-8
#!/usr/bin/env python#
import logging
import gtk
import gobject

from twindow import BUILD_VERSION, VERSION

from twindow.baseUI import tcloudWindow
from twindow.common.exception import BusinessException, NetworkException
from twindow.common.ifconfig import Interface
from twindow.common.resource import res_dict as Resource, PowerStatus, Nth
from twindow.model.tcloudModel import TableModel, LabelModel, EditModel,\
    VMListModelShort, SimpleSelectWidget, ModeModel, ErrorLabelModel
from twindow.viewerManager import viewManager

from twindow.common import utils, resource
import os
"""
    @author: jay.han
"""
LOG = logging.getLogger("twindow.login")
import signal

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    print 'Finalizing main loop'
    gtk.main_quit()

REASON = None
try:
    from twindow.api.apr_proxy import api
    api_proxy = api
except NetworkException:
    api_proxy = None
    REASON = Resource.NETWORK_ERROR
except Exception:
    api_proxy = None
    REASON = None

signal.signal(signal.SIGTERM, handler)

class tLogin(tcloudWindow):
    def __init__(self,conf):
        tcloudWindow.__init__(self,"login.ui","twindow-login")

        """
            read from config
        """
        self.conf = conf
        self.mainwin.set_deletable(False)
        self.mainwin.set_resizable(False)
        self.mainwin.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.mainwin.set_position(gtk.WIN_POS_CENTER)
        self.mainwin.set_title(" ")
        """ 
            get config info
        """
        self.ifname = self.conf["interface"]
        self.body = self.widget("main")
        self.init_image()
        self.init_login_table()
        self.login_info = None
        self.manager = None
        self.client_trace = None

        self.mode = resource.CLASS_MODE

    def init_device(self):
        try:
            self.hostname = utils.get_hostname()
            self.ip = utils.get_interface_ip(self.ifname)
            self.mac = utils.get_mac_address(self.ifname)
        except:
            self.hostname = None
            self.ip = None
            self.mac = None

    def change_title(self):
        self.mainwin.set_title(" ")

    def init_image(self):
        if self.conf.get_int('version') == 1:
            if self.conf.get_int('language_code') == 1:
                self.widget("image_login").set_from_file(os.path.join(os.path.dirname(self.base),"res","vd_logo_pengke_en.jpg" ))
            else:
                self.widget("image_login").set_from_file(os.path.join(os.path.dirname(self.base),"res","vdi-pengke.jpg" ))
        else:
            self.widget("image_login").set_from_file(os.path.join(os.path.dirname(self.base),"res","vdi_logo.jpg" ))

    def init_login_table(self):

        self.login_table = TableModel(5,2)

        #login = gtk.Alignment(1, 0, 0, 0)

        self.error_label = ErrorLabelModel("",1,0.5)
        self.username_label = EditModel(max=255,visible=False,default=self.conf.get('user_name'))
        self.password_label = EditModel(vis=False,visible=False)
        self.login_model = SimpleSelectWidget()
        self.user_display = LabelModel(Resource.LOGIN_USER_LABEL,1,0.5,font=12,visible=False)
        self.pwd_display = LabelModel(Resource.LOGIN_PASSWD_LABEL,1,0.5,font=12,visible=False)

        self.check_box = self.right_align()

        check_me = gtk.CheckButton('')
        if self.conf.get('user_name'):
            check_me.set_active(True)
        check_me.connect("toggled",self._remember)

        pwd_label  = LabelModel('',1,0.5)
        pwd_label.set_markup(Resource.CHANGE_PWD_URI)
        pwd_label.connect('activate-link',self._change_pwd)

        self.check_box.add(check_me)
        self.right_box = gtk.HBox()

        remember_me = LabelModel(Resource.REMMERBER_ME,0,0.5,font=12,visible=False)
        self.right_box.pack_start(remember_me,0,0)
        self.right_box.pack_start(pwd_label,0,0)
        login_mode = LabelModel(Resource.LOGIN_MODE,1,0.5,font=12)
        self.login_table.init_data_fill([[login_mode,
                               self.user_display, 
                               self.pwd_display,self.check_box],

                            [self.login_model.make_view(data_list=[[Resource.USER_MODE,1],[Resource.FREE_MODE,0]]),
                             self.username_label,
                             self.password_label,self.right_box]])

        self.login_button = gtk.Button(Resource.LOGIN_BUTTON)
        self.login_button.set_size_request(70,30)
        self.login_button.set_focus_on_click(True)
        self.login_button.connect("clicked",self.login)

        self.config_button = gtk.Button(Resource.CONFIG_BUTTON)
        self.config_button.set_size_request(70,30)
        self.config_button.set_focus_on_click(True)
        self.config_button.connect("clicked",self.config)

        button_box = gtk.HButtonBox()
        button_box.set_spacing(10)

        button_box.add(self.config_button)
        button_box.add(self.login_button)

        right_a = self.right_align()
        right_a.set_property("right-padding",36)
        right_a.add(button_box)
        right_a.show_all()

        right_a_1 = self.right_align()
        right_a_1.set_property("right-padding",36)
        right_a_1.add(self.error_label)
        right_a_1.show_all()
        login_mode.show()
        self.login_table.show()
        self.body.pack_start(self.login_table,0,0,padding=5)
        self.body.pack_start(right_a_1,1,1)
        self.body.pack_start(right_a,1,1,padding=5)


        if self.conf.get_int('version') == 1:
            self.body.pack_start(LabelModel(Resource.PENGKE_COMPANY_INFO,0.5,0.5,font=10),0,0)
        else:
            self.body.pack_start(LabelModel(Resource.OE_COMPANY_INFO,0.5,0.5,font=10),0,0)
        self.body.pack_start(LabelModel(BUILD_VERSION,0.5,0.5,font=10),0,0)

        self.get_out_five = False

        if not api_proxy:
            self.login_button.set_sensitive(False)

            reason = REASON if REASON else Resource.NETWORK_UNREACHABLE
            self.error_label.error_text(reason)

        self.login_model.view.connect('changed',self._change_mode)
        #####
        
    def show(self,widget=None,data=None):

        self.clean()
        self.init_device()
        self.bind_events()
        self.mainwin.present()

        #self.mainwin.show_all()
        
    def close(self,widget,data=None):
        pass
        #gtk.main_quit()
    
    def clean(self):
        if self.manager:
            self.manager.clean()
        self.manager = None
        
    def change_view(self,g_type,c_info):
        LOG.debug("changing view from spice to vnc, connect_info is %s" % c_info)
        self.manager.change_view(g_type,c_info)
        
    def change_back(self):
        self.manager.change_back()

    def killSession(self):

        self.mainwin.set_title("  ")
        if self.manager:
            self.manager.close()

        self.error_label.error_text(Resource.KILL_SESSION_MSG)

    def close_manager(self):
        if self.manager:
            self.manager.hide()

        self.show()



    def _popup_vm_list(self,vm_list=None):
        dialog = self.init_diag(Resource.SELECT_VM_LABEL,500,400)
        vm_box = dialog.get_child()
        vm_label = LabelModel(Resource.LOGIN_VM_PROMT,0,0.5,font=12)
        vm_rows = []

        for vm in vm_list:
            if vm['power_status'] == PowerStatus.RUNNING:
                icon = utils.get_pixbuf_from_file("poweron.ico")
            else:
                icon = utils.get_pixbuf_from_file("poweroff.ico")
            vm_rows.append([icon,vm['display_name'],vm['image']['os_type'],vm['id']])

        vm_table = VMListModelShort()
        
        vm_box.pack_start(vm_label,0,0)
        vm_box.pack_start(vm_table.make_view(data_list=vm_rows),1,1)

        dialog.connect("response", self._apply, vm_list,Nth.THREE,0,vm_table)
        
        dialog.show_all()
        dialog.run()

    def _popup_mode_list(self,mode_list=None):

        dialog = self.init_diag(Resource.SELECT_MODE_LABEL,300,300)
        mode_box = dialog.get_child()
        mode_label = LabelModel(Resource.LOGIN_MODE_PROMT,0,0.5,font=12)
        mode_rows = []
        for mode in mode_list:
            mode_rows.append([mode['name'],mode['id']])

        md_table = ModeModel()

        mode_box.pack_start(mode_label,0,0)
        mode_box.pack_start(md_table.make_view(data_list=mode_rows),1,1)

        dialog.connect("response", self._apply, mode_list,Nth.ONE,1,md_table)
        dialog.show_all()
        dialog.run()


    def _select_mode(self,data):
        try:
            result = api_proxy.select_mode_api({'mode_id':data['id'],
                                                'mode_name':data['name'],
                                                'client_mac':self.mac,
                                                'client_name':utils.get_hostname(),
                                                'user_id':self.user_id})

            self.choose_vm(result['vms'])
        except Exception as e:
            self.error_label.error_text(Resource.NO_MODE_MSG)
            self.mainwin.show()
            self.error_label.show()
            return False



    def _change_mode(self,widget):
        self.get_out_five = True
        self.mode = self.login_model.get_selected(1)
        self.error_label.set_markup(" ")
        if self.mode == 0:
            self.check_box.show_all()
            self.right_box.show_all()
            self.user_display.show()
            self.username_label.show()
            self.pwd_display.show()
            self.password_label.show()
        else:
            self.check_box.hide_all()
            self.right_box.hide_all()
            self.user_display.hide()
            self.username_label.hide()
            self.pwd_display.hide()
            self.password_label.hide()
        #self.user_display.set_visible(self.mode == 0)
        #self.username_label.set_visible(self.mode==0)
        #self.pwd_display.set_visible(self.mode == 0)
        #self.password_label.set_visible(self.mode == 0)

    def _change_pwd(self,widget,data=None):
        dialog = self.init_diag(Resource.CHANGE_PWD,200,100)
        pwd_box = dialog.get_child()

        config = TableModel(2,2)
        old_pwd = EditModel(width=200,vis=False)
        new_pwd = EditModel(width=200,vis=False)
        confirm_pwd = EditModel(width=200,vis=False)

        config.init_data_fill([[LabelModel(Resource.OLD_PWD,1,0.5,font=12),
                                LabelModel(Resource.NEW_PWD,1,0.5,font=12),
                                LabelModel(Resource.CONFIRM_PWD,1,0.5,font=12),
                                ],

                               [old_pwd,new_pwd,confirm_pwd]])

        pwd_box.pack_start(config)

        datas = {"old_passwd":old_pwd,
                'new_passwd':new_pwd,
                'confirm_pwd':confirm_pwd}

        dialog.connect("response", self._apply_change_pwd,datas)

        dialog.show_all()
        dialog.run()
            
    def _build_connect_info(self,vm):
        return "%s:%s" % (vm['host'],"%s" % (5900 + int(vm['id'])))
    
    def _select_vm(self,data):

        result = self._start_vm(data)
        if not result:
            return

        vm_id = data['id']
        connect_info = self._build_connect_info(data)
        password = utils.getMD5Str(resource.INSTANCE_TEMPLATE % vm_id)[-6:]

        self.manager = viewManager(hostname=self.hostname,
                                   ip=self.ip,
                                   api=api_proxy,
                                   vm_id=vm_id,
                                   pwd=password,
                                   connect_info=connect_info)
        
        if self.manager:
            self.manager.connect("manager-closed", self.logout)
            self.manager.show()
            self.error_label.set_markup("")

    def choose_vm(self,vms):
        if len(vms) == 1:
            vm = vms[0]
            self._select_vm(vm)
        else:
            self._popup_vm_list(vms)

    def _start_vm(self,vm):

        try:
            api_proxy.vm_connect_api({'vm_id':vm['id'],
                                      'client_mac':self.mac})
            return True
        except BusinessException as e:
            self.error_label.error_text(str(e))
            self.mainwin.show()
            return False
        except:
            LOG.exception('error in start vm')
            self.error_label.error_text(Resource.START_VM_MSG)
            self.mainwin.show()
            return False

    def ignore(*args): # do nothing
        return gtk.TRUE
        
    def bind_events(self):
        #self.login_model.connect('expose-event',self._change_back_ground)

        self.mainwin.connect("destroy",self.ignore)
        self.mainwin.connect("close",self.ignore)
        self.mainwin.connect('delete_event', self.ignore)
        self.mainwin.connect('key-press-event', self._enter_login)
        self.add_timeout()

    def _change_back_ground(self,widget,data=None):
        widget.draw_pixbuf(widget.style.bg_gc[gtk.STATE_NORMAL],
                                  utils.get_pixbuf_from_file('background.jpg',xsize=800,ysize=600), 0, 0, 0,0)

        self.init_image()
        self.init_login_table()
        return True

    def _enter_login(self,widget,event):
        #enter
        if event.keyval == 65293:
            self.login(widget)
            return True
        return False




    def add_timeout(self):
        gobject.timeout_add(self.conf.get_int('timeout')*1000,self._login_within_five)

    ##############################################
    #########  event binding
    ##############################################
    def _apply(self,widget,response_id=None,dates=None,
                            nth=0,type=0,table=None):

        if response_id != gtk.RESPONSE_APPLY:
            self.mainwin.show()
            self.error_label.error_text(" ")
            widget.destroy()
        else:
            select_id = self.check_before_up_del(table,nth=nth)
            if select_id:
                for data in dates:
                    if data['id'] == int(select_id):
                        if type==0:
                            self._select_vm(data)
                        else:
                            self._select_mode(data)
                        widget.destroy()
                        return False

    def _apply_change_pwd(self,widget,response_id=None,data=None):
        if response_id == gtk.RESPONSE_APPLY:
            if data['confirm_pwd'].get_text() != data['new_passwd'].get_text():
                self.on_error(Resource.PASSWD_NOT_EQUAL,master=widget)
                widget.run()
                return False
            try:
                api_proxy.change_pwd({"name":self.username_label.get_text(),
                                  "passwd":data['old_passwd'].get_text(),
                                  "new_passwd":data['new_passwd'].get_text()})
                self.on_info(Resource.SUCCESS,master=widget)
            except Exception as e:
                self.on_error(str(e))
                widget.run()
                return False

        widget.destroy()
        return True



    def _login_within_five(self):
        if not self.get_out_five:
            with gtk.gdk.lock:
                self.login_button.emit("clicked")
                self.get_out_five=True
        return False

    def _remember(self,widget,date=None):
        toggled = widget.get_active()
        text = self.username_label.get_text() if toggled else ''
        self.conf.write_conf({'user_name':text})
        return True

    def config(self,widget,data=None):
        if widget:
            self.get_out_five = True

        def init_diag(title,width,height):
            dialog = gtk.Dialog(title,buttons=None)
            dialog.set_default_size(width,height)

            dialog.add_buttons(Resource.BUTTON_CANCEL, gtk.RESPONSE_CLOSE)
            dialog.add_buttons(Resource.BUTTON_OK, gtk.RESPONSE_APPLY)
            dialog.connect('close',dialog.destroy)
            return dialog

        def _config(widget,response_id,values):
            if response_id == gtk.RESPONSE_APPLY:
                ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
                file = os.path.abspath(os.path.join(ROOT_PATH,'..', 'conf/twindow.conf'))

                hostname = values['hostname'].get_text()

                if not hostname or not ':' in hostname:
                    self.on_error(Resource.INPUT_HOSTNAME_REQUIRE,master=widget)
                    widget.run()
                    return False

                utils.dict_updating(file,dict(api_server=values['hostname'].get_text(),
                                              timeout=values['timeout'].get_text(),
                                              interface = values['iface'].get_text()))

                if values['iface'].get_text() and values['ip'].get_text() \
                    and values['netmask'].get_text() and values['gateway'].get_text():

                    self.curr_interface.set_network(dev=values['iface'].get_text(),
                                                    ip=values['ip'].get_text(),
                                                    netmask=values['netmask'].get_text(),
                                                    gateway=values['gateway'].get_text())
                    utils.execute('/usr/bin/python','/etc/twindow/bin/clientDaemon.pyc','restart')
                else:
                    self.on_error(Resource.INPUT_NETWORK_INVALID,master=widget)
                    widget.run()
                    return False
  

            widget.destroy()
            return True


        dialog = init_diag(Resource.MODIFY_IP_LABEL,200,100)
        config_box = dialog.get_child()
        config = TableModel(2,2)
        hostname = EditModel(width=200,text=self.conf['api_server'])
        timeout = EditModel(width=200,text='5')


        iface = EditModel(width=200,text=self.conf['interface'])
        self.curr_interface = Interface(self.conf['interface'])

        ip_text = self.curr_interface.ip
        ip = EditModel(width=200,text=ip_text,default='0.0.0.0')
        net_mask_text = self.curr_interface.get_netmask_str()
        net_mask = EditModel(width=200,text=net_mask_text)
        gateway_text = self.curr_interface.get_gw()
        gateway = EditModel(width=200,text=gateway_text,default='0.0.0.0')

        config.init_data_fill([[LabelModel(Resource.CONFIG_API,1,0.5,font=12),
                                LabelModel(Resource.CONFIG_TIMEOUT,1,0.5,font=12),
                                LabelModel(Resource.CONFIG_IFACE,1,0.5,font=12),
                                LabelModel(Resource.CONFIG_IP,1,0.5,font=12),
                                LabelModel(Resource.CONFIG_NETMASK,1,0.5,font=12),
                                LabelModel(Resource.CONFIG_GATEWAY,1,0.5,font=12),],

                               [hostname,timeout,iface,ip,net_mask,gateway]])

        config_box.pack_start(config)
        values = {'timeout':timeout,
                  'hostname':hostname,
                  'iface':iface,
                    'ip':ip,
                 'netmask':net_mask,
                 'gateway':gateway}
        dialog.connect("response", _config,values)

        dialog.show_all()
        dialog.run()

        return False

    def login(self,widget,data=None):
        if widget:
            self.get_out_five = True
        self.user = self.username_label.get_text()
        self.pwd = self.password_label.get_text()

        if self.mode == resource.CLASS_MODE:
            result = api_proxy.get_login_name({'client_mac':self.mac})
            self.user = result['login_name']
            self.pwd = self.mac
        else:
            if not self.user:
                self.error_label.error_text(Resource.INPUT_USERNAME)
                return False
            if not self.pwd:
                # display error
                self.error_label.error_text(Resource.INPUT_PASSWORD)
                return False
        try:
            self.login_info = api_proxy.login_api({"name":self.user,
                                                   "passwd":self.pwd,
                                                   "client_mac":self.mac,
                                                   "client_ip":utils.get_interface_ip(self.ifname)})
        except Exception as e:
            self.error_label.error_text(str(e))
            return False

        result = self.login_info

        if 'client_trace' in result:
            self.client_trace = result['client_trace']

        self.user_id = result['user_id']
        self.role = result['role']
        self.mainwin.hide()

        modes = result['modes'] if 'modes' in result else None
        print modes
        if modes:
            if len(modes) == 1 or not widget:
                mode = modes[0]
                self._select_mode(mode)
            else:
                self._popup_mode_list(modes)

        else:
            vms = result['vms'] if 'vms' in result else None
            # copy result to login info
            self.choose_vm(vms)

        return False

    def hello(self):
        LOG.debug("hello from login")
    
    def logout(self,widget=None,data=None):
        LOG.debug("logout....")
        api_proxy.logout_api({"name":self.user,
                              "user_id":self.user_id,
                              "client_mac":self.mac,
                              'client_trace':self.client_trace})
        self.show()