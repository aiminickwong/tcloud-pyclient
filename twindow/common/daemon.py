#!/usr/bin/env python
#!coding:utf-8
import sys, os, time, atexit
from signal import SIGKILL

class Daemon(object):
    """
    守护进程启动帮助类
    """
    def __init__(self, pidfile, workman, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.run = workman

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        引用：
        Fork a second child and exit immediately to prevent zombies.  This
        causes the second child process to be orphaned, making the init
        process responsible for its cleanup.  And, since the first child is
        a session leader without a controlling terminal, it's possible for
        it to acquire one by opening a terminal in the future (System V-
        based systems).  This second fork guarantees that the child is no
        longer a session leader, preventing the daemon from ever acquiring
        a controlling terminal.
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        with file(self.pidfile, 'w') as f:
            pid = str(os.getpid())
            f.write("%s" % pid)

    def delpid(self):
        os.remove(self.pidfile)


    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            with file(self.pidfile) as f:
                pid = int(f.read())
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            with file(self.pidfile) as f:
                pid = int(f.read())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGKILL)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)


    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
