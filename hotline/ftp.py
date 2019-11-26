# Author: Jorge Alarcon Alvarez
# Email: jorge4larcon@gmail.com
"""This module contains functions to start an FTP server and handle its events."""

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from PyQt5 import QtCore
import logging


class FtpServerSignals(QtCore.QObject):
    """This class defines the signals a FTP server thread will emit."""
    # remote_ip, remote_port
    on_connect = QtCore.pyqtSignal(str, int)
    on_disconnect = QtCore.pyqtSignal(str, int)

    # remote_ip, remote_port, username
    on_login = QtCore.pyqtSignal(str, int, str)
    on_logout = QtCore.pyqtSignal(str, int, str)

    on_start = QtCore.pyqtSignal()
    on_shutdown = QtCore.pyqtSignal()

    # remote_ip, remote_port, filename
    on_file_sent = QtCore.pyqtSignal(str, int, str)
    on_file_received = QtCore.pyqtSignal(str, int, str)
    on_incomplete_file_sent = QtCore.pyqtSignal(str, int, str)
    on_incomplete_file_received = QtCore.pyqtSignal(str, int, str)

    on_error = QtCore.pyqtSignal('PyQt_PyObject')


class MyHandler(FTPHandler):
    """This class defines the connection handler of the FTP server."""
    signals: FtpServerSignals = None

    def on_connect(self):
        """When FTP client connects"""
        logging.info(f"ftp: new connection from {self.remote_ip}:{self.remote_port}")
        self.signals.on_connect.emit(self.remote_ip, self.remote_port)

    def on_disconnect(self):
        """When FTP client disconnects"""
        logging.info(f"ftp: client {self.remote_ip}:{self.remote_port} disconnected")
        self.signals.on_disconnect.emit(self.remote_ip, self.remote_port)

    def on_login(self, username):
        """When FTP client login"""
        logging.info(f"ftp: '{username}' {self.remote_ip}:{self.remote_port} logged in")
        self.signals.on_login.emit(self.remote_ip, self.remote_port, username)

    def on_logout(self, username):
        """When FTP client logout"""
        logging.info(f"ftp: '{username}' {self.remote_ip}:{self.remote_port} logged out")
        self.signals.on_logout.emit(self.remote_ip, self.remote_port, username)

    def on_file_sent(self, file):
        """When a file has been sent"""
        logging.info(f"ftp: '{file}' was succesfully sent to {self.remote_ip}:{self.remote_port}")
        self.signals.on_file_sent.emit(self.remote_ip, self.remote_port, file)

    def on_file_received(self, file):
        """When a file has been received"""
        logging.info(f"ftp: '{file}' was succesfully received from {self.remote_ip}:{self.remote_port}")
        self.signals.on_file_received.emit(self.remote_ip, self.remote_port, file)

    def on_incomplete_file_sent(self, file):
        """When a file has been incompletely sent"""
        logging.info(f"ftp: '{file}' was not fully sent to {self.remote_ip}:{self.remote_port}")
        self.signals.on_incomplete_file_sent.emit(self.remote_ip, self.remote_port, file)

    def on_incomplete_file_received(self, file):
        """When a file has been incompletely received"""
        logging.info(f"ftp: '{file}' was not fully received from {self.remote_ip}:{self.remote_port}")
        self.signals.on_incomplete_file_received.emit(self.remote_ip, self.remote_port, file)
        import os
        try:
            os.remove(file)
        except Exception as e:
            pass


class FtpServer(QtCore.QRunnable):
    """The FTP server thread"""
    def __init__(self, ip, port, max_conn, max_conn_per_ip, folder, banner, users_can_upload_files):
        super(FtpServer, self).__init__()
        self.signals = FtpServerSignals()
        self.ip = ip
        self.port = port
        self.max_connections = max_conn
        self.max_connections_per_ip = max_conn_per_ip
        self.folder = folder
        self.banner = banner
        self.permisions = 'elr'
        if users_can_upload_files:
            self.permisions += 'w'

    @QtCore.pyqtSlot()
    def run(self):
        """This method defines what actions the FTP server does when running"""
        authorizer = DummyAuthorizer()
        authorizer.add_user('hotline', 'hotpassword', homedir=self.folder, perm=self.permisions)
        handler = MyHandler
        handler.banner = self.banner
        handler.authorizer = authorizer
        self.handler = handler
        self.handler.signals = self.signals
        try:
            self.server = FTPServer((self.ip, self.port), handler)
        except Exception as e:
            self.signals.on_error.emit(e)
            return

        self.server.max_cons = self.max_connections
        self.server.max_cons_per_ip = self.max_connections_per_ip
        # server = FTPServer((self.ip, self.port), handler)
        try:
            self.signals.on_start.emit()
            self.server.serve_forever()
        except Exception as e:
            self.signals.on_error.emit(e)

    def my_jorge_shutdown(self):
        """This method shutdowns the server"""
        self.signals.on_shutdown.emit()
        # self.server.close()
        self.server.close_all()
