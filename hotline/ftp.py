from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
from PyQt5 import QtCore
import pyftpdlib


class MyHandler(FTPHandler):

    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        print("%s:%s disconnected" % (self.remote_ip, self.remote_port))

    def on_login(self, username):
        print(f"'{username}' {self.remote_ip}:{self.remote_port}  logged in")

    def on_logout(self, username):
        print(f"'{username}' {self.remote_ip}:{self.remote_port}  logged out")

    def on_file_sent(self, file):
        print(f"Complete '{file}' send")

    def on_file_received(self, file):
        print(f"Complete '{file}' received")

    def on_incomplete_file_sent(self, file):
        print(f"Incomplete '{file}' send")

    def on_incomplete_file_received(self, file):
        print(f"Incomplete '{file}' received")
        import os
        os.remove(file)


class FtpServerSignals(QtCore.QObject):
    # remote_ip, remote_port
    on_connect = QtCore.pyqtSignal(str, int)
    on_disconnect = QtCore.pyqtSignal(str, int)

    # remote_ip, remote_port, username
    on_login = QtCore.pyqtSignal(str, int, str)
    on_logout = QtCore.pyqtSignal(str, int, str)

    on_start = QtCore.pyqtSignal()
    on_end = QtCore.pyqtSignal()

    # remote_ip, remote_port, filename
    on_file_sent = QtCore.pyqtSignal(str, int, str)
    on_file_received = QtCore.pyqtSignal(str, int, str)
    on_incomplete_file_sent = QtCore.pyqtSignal(str, int, str)
    on_incomplete_received_sent = QtCore.pyqtSignal(str, int, str)

    on_error = QtCore.pyqtSignal('PyQt_PyObject')


class FtpServer(QtCore.QRunnable):
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
        authorizer = DummyAuthorizer()
        authorizer.add_user('hotline', 'hotpassword', homedir=self.folder, perm=self.permisions)
        handler = MyHandler
        handler.authorizer = authorizer
        server = FTPServer((self.ip, self.port), handler)
        try:
            server.serve_forever()
            server.
        except Exception as e:
            self.signals.on_error.emit(e)
        else:
            self.signals.on_start.emit()


def main():
    authorizer = DummyAuthorizer()
    read_permissions = 'elr'
    write_permissions = 'w'
    permissions = read_permissions + write_permissions
    authorizer.add_user('hotline', 'hotpassword', homedir='.', perm=permissions)

    handler = MyHandler
    handler.authorizer = authorizer
    server = FTPServer(('172.16.161.29', 2121), handler)
    try:
        server.serve_forever()
    except Exception as e:
        self



if __name__ == "__main__":
    main()
