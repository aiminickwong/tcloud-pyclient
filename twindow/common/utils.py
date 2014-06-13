#!coding:utf-8
"""
    @author: jay.han
    
"""
import dircache
import glob
import os
import gtk,gobject
import shlex
import socket,signal
import fcntl, struct
import logging
import platform
import re
import sys
import subprocess
import datetime


basepath =os.path.abspath(os.path.dirname(__file__))
TWINDOW = os.path.dirname(os.path.dirname(basepath))
LOG = logging.getLogger("twindow.utils")

class MENU:
    REPO = 0
    SYSMANAGE = 1
    CLASSMANAGE = 2
    USERMANAGE = 3
    TEMPLATEMANAGE =4
    SYSMAINTAIN = 5
    SCHEDULE = 6
    @staticmethod
    def has_label(name):
        return name == MENU.REPO or name == MENU.SYSMANAGE or \
                name ==MENU.CLASSMANAGE or name == MENU.USERMANAGE \
                or name == MENU.TEMPLATEMANAGE or name == MENU.SYSMAINTAIN \
                or name == MENU.SCHEDULE
                
class TEACHER_MENU:
    #REPO = 0 name == TEACHER_MENU.REPO or
    MYCLASS = 1
    MONITOR = 2
    TEACHING = 3
    @staticmethod
    def has_label(name):
        return  name == TEACHER_MENU.MYCLASS or \
                name ==TEACHER_MENU.MONITOR or name == TEACHER_MENU.TEACHING

class ROLE:
    STUDENT = 2
    ADMIN = 0
    TEACHER = 1
    
class EDU_DICT:
    CLASS = 2
    DEPARTMENT = 1
    SCHOOL = 0
    
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def isotime(at=None,time_format=None):
    if not at:
        at = datetime.datetime.utcnow()
    if time_format:
        return at.strftime(time_format)
    return at.strftime(TIME_FORMAT)

def escape_pattern(pattern):
    """ Escape special chars on patterns, so glob doesn't get confused """
    pattern = pattern.replace('[', '[[]')
    return pattern

def get_file_listing(dir, mode, pattern=None):
    """ Returns the file listing of a given directory. It returns only files.
    Returns a list of [file,/path/to/file] """

    filelist = []

    if  pattern == None:
        listaux = dircache.listdir(dir)
    else:
        if dir != '/': 
            dir += '/'
        dir = escape_pattern(dir + pattern)
        listaux = glob.glob(dir)
    listaux.sort(key=str.lower)
    
    for elem in listaux:
        if mode == 0:
            # Get files
            if not os.path.isdir(os.path.join(dir, elem)):
                filelist.append([os.path.basename(elem), os.path.join(dir, elem)])
        elif mode == 1:
            # Get directories
            if os.path.isdir(os.path.join(dir, elem)):
                filelist.append([os.path.basename(elem), os.path.join(dir, elem)])
        elif mode == 2:
            # Get files and directories
            filelist.append([os.path.basename(elem), os.path.join(dir, elem)])
        else:
            # Get files
            if not os.path.isdir(os.path.join(dir, elem)):
                filelist.append([os.path.basename(elem), os.path.join(dir, elem)])

    return filelist

def _subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def smb_mount(host,dir,user,pwd):
    return execute("mount","-t","cifs","-o","username=%s,password=%s"% (user,pwd), "//%s/%s"% (host,dir),"/mnt/repo",run_as_root=True)

def upload(file,path):
    
    return execute("mv %s %s" % (file,path))


def execute(*cmd, **kwargs):
    """
    Helper method to execute command with optional retry.

    :cmd                Passed to subprocess.Popen.
    :process_input      Send to opened process.
    :check_exit_code    Defaults to 0. Raise exception.ProcessExecutionError
                        unless program exits with this code.
    :delay_on_retry     True | False. Defaults to True. If set to True, wait a
                        short amount of time before retrying.
    :attempts           How many times to retry cmd.
    :run_as_root        True | False. Defaults to False. If set to True,
                        the command is prefixed by the command specified
                        in the root_helper FLAG.

    :raises exception.Error on receiving unknown arguments
    :raises exception.ProcessExecutionError
    """

    process_input = kwargs.pop('process_input', None)
    delay_on_retry = kwargs.pop('delay_on_retry', True)
    attempts = kwargs.pop('attempts', 1)
    run_as_root = kwargs.pop('run_as_root', False)
    is_debug = kwargs.pop('is_debug', True)
    if run_as_root:
        cmd = shlex.split('sudo') + list(cmd)
    cmd = map(str, cmd)
    while attempts > 0:
        attempts -= 1
        try:
            if is_debug: 
                LOG.debug('Running cmd (subprocess): %s' % cmd), ' '.join(cmd)
            _PIPE = subprocess.PIPE  
            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE,
                                   stdout=_PIPE,
                                   stderr=_PIPE,
                                   close_fds=True,
                                   preexec_fn=_subprocess_setup)
            result = None
            if process_input is not None:
                result = obj.communicate(process_input)
            else:
                result = obj.communicate()
            obj.stdin.close()  
            _returncode = obj.returncode  
            if _returncode:
                LOG.debug(('Result code was %s') % _returncode)
            return result
        except Exception as e:
            LOG.debug('exception was %s ' % e)

    
            
def get_image_from_file(name,size=20):
        
    image = gtk.Image()
    
    image.set_from_pixbuf(get_pixbuf_from_file(name,size))
    return image      

def get_pixbuf_from_file(name,xsize=20,ysize=20):
    file_path = os.path.join(TWINDOW,"res",name )
    pixbuf = gtk.gdk.pixbuf_new_from_file(file_path)
    scaled_buf = pixbuf.scale_simple(xsize,ysize,gtk.gdk.INTERP_BILINEAR)
    
    return scaled_buf
          
def get_icon_by_name(name,size=50):
    icon_theme = gtk.icon_theme_get_default()
    try:
        icon = icon_theme.load_icon(name, size, 0)
        return icon
    except gobject.GError, exc:
        return None 
    
def get_icon(path):
        icon_theme = gtk.icon_theme_get_default()
        if os.path.isdir(path):
            try:
                icon = icon_theme.load_icon("gnome-fs-directory", 16, 0)
                return icon
            except gobject.GError, exc:
                try:
                    icon = icon_theme.load_icon("gtk-directory", 16, 0)
                    return icon
                except:
                    return None
        else:
            mime = "text-x-generic"
            audio = ["mp3", "ogg", "wav", "aiff","m4a"]
            image = ["jpg", "gif", "png", "tiff", "tif", "jpeg"]
            video = ["avi", "ogm", "mpg", "mpeg", "mov"]
            package = ["rar", "zip", "gz", "tar", "bz2", "tgz", "deb", "rpm"]

            file = path.split('/')[-1]
            ext = (file.split('.')[-1]).lower()
            
            if ext in audio:
                mime = "audio-x-generic"

            elif ext in image:
                mime = "image-x-generic"

            elif ext in video:
                mime = "video-x-generic"

            elif ext in package:
                mime = "package-x-generic"
            else:
                mime = gtk.STOCK_FILE
            try:
                icon = icon_theme.load_icon(mime, 50, 0)
                return icon
            except gobject.GError, exc:
                return None

def get_interface_ip(if_name="eth0"):
    try:
        execute('ifconfig',if_name,'up')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', if_name[:15])
        )[20:24])
    except:
        LOG.exception("error in get interface_ip")
        return '0.0.0.0'

    
def get_mac_address(ifname="eth0"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1] 

def get_hostname():
    return socket.gethostname()

def get_os():
    return "%s %s %s" % platform.linux_distribution() + " ,%s" % (platform.system())

def get_memory_mb():
    """

    :returns: (MB).

    """
    if sys.platform.upper() not in ['LINUX2', 'LINUX3']:
        return 0

    meminfo = open('/proc/meminfo').read().split()
    idx = meminfo.index('MemTotal:')
    # transforming kb to mb.
    return int(meminfo[idx + 1]) / 1024
    
def get_cpu_type():
    if sys.platform.upper() not in ['LINUX2', 'LINUX3']:
        return None
    
    output,_= execute("cat","/proc/cpuinfo")
    for line in output.split("\n"):
        if "model name" in line:
            return re.sub( ".*model name.*:", "", line,1)


SALT = 'Tcloud'
def getMD5Str(original_str):

    '''对str进行MD5加密'''

    if not original_str:
        return ''

    import hashlib

    md5 = hashlib.md5()
    md5.update(SALT+original_str)
    md5Str = md5.hexdigest()

    return md5Str

"""
    file updating

"""
def dict_updating(filename,dict):
    RE = '(('+'|'.join(dict.keys())+')\s*=)[^\r\n]*?(\r?\n|\r)'
    pat = re.compile(RE)

    def jojo(mat,dic = dict ):
        return dic[mat.group(2)].join(mat.group(1,3))

    with open(filename,'rb') as f:
        content = f.read()

    with open(filename,'wb') as f:
        f.write(pat.sub(jojo,content))