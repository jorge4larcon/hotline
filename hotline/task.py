from PyQt5 import QtCore
import inbox
import asyncio
import ftplib
import os


# def recvall(sock: socket.socket, length):
#     data = b''
#     while len(data) < length:
#         more = sock.recv(length - len(data))
#         if not more:
#             raise EOFError()

class GetContactInformationSignals(QtCore.QObject):
    on_error = QtCore.pyqtSignal(str, int)
    on_result = QtCore.pyqtSignal(str)
    on_finished = QtCore.pyqtSignal()


class GetContactInformationThread(QtCore.QRunnable):
    def __init__(self, ip, port=42000, timeout=3):
        super(GetContactInformationThread, self).__init__()
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.signals = GetContactInformationSignals()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = asyncio.run(inbox.get_contact_information(self.ip, self.port, self.timeout))
        except Exception as e:
            self.signals.on_error.emit(self.ip, self.port)
        else:
            self.signals.on_result.emit(result)
        finally:
            self.signals.on_finished.emit()


class StartFtpClientConnectionSignals(QtCore.QObject):
    on_error = QtCore.pyqtSignal(str, int)
    on_result = QtCore.pyqtSignal('PyQt_PyObject')
    on_connect = QtCore.pyqtSignal(str)
    on_finished = QtCore.pyqtSignal()


class StartFtpClientConnectionThread(QtCore.QRunnable):
    def __init__(self, ip, port=42000, timeout=3):
        super(StartFtpClientConnectionThread, self).__init__()
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.signals = StartFtpClientConnectionSignals()

    def run(self):
        try:
            ftp = ftplib.FTP()
            banner = ftp.connect(host=self.ip, port=self.port, timeout=self.timeout)
            self.signals.on_connect.emit(banner)
            ftp.login(user='hotline', passwd='hotpassword')
        except Exception as e:
            self.signals.on_error.emit(self.ip, self.port)
        else:
            self.signals.on_result.emit(ftp)
        finally:
            self.signals.on_finished.emit()


class UploadFileSignals(QtCore.QObject):
    # host, port, filename
    on_start = QtCore.pyqtSignal(str, int, str)
    # host, port, filename, exception
    on_error = QtCore.pyqtSignal(str, int, str, 'PyQt_PyObject')
    # host, port, filename
    on_finished = QtCore.pyqtSignal(str, int, str)


class UploadFileThread(QtCore.QRunnable):
    def __init__(self, filename, ftp_conn: ftplib.FTP):
        super(UploadFileThread, self).__init__()
        self.filename = filename
        self.ftp_conn = ftp_conn
        self.signals = UploadFileSignals()

    def run(self):
        try:
            with open(self.filename, 'rb') as f:
                self.signals.on_start.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename)
                self.ftp_conn.storbinary(f"STOR {os.path.split(self.filename)[1]}", f)
        except Exception as e:
            self.signals.on_error.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename, e)
        else:
            self.signals.on_finished.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename)


class DownloadFileSignals(QtCore.QObject):
    # host, port, filename
    on_start = QtCore.pyqtSignal(str, int, str)
    # host, port, filename, exception
    on_error = QtCore.pyqtSignal(str, int, str, 'PyQt_PyObject')
    # host, port, filename
    on_finished = QtCore.pyqtSignal(str, int, str)


class DownloadFileThread(QtCore.QRunnable):
    def __init__(self, filename, ftp_conn: ftplib.FTP, folder_to_save):
        super(DownloadFileThread, self).__init__()
        self.filename = filename
        self.ftp_conn = ftp_conn
        self.folder_to_save = folder_to_save
        self.signals = DownloadFileSignals()

    def run(self) -> None:
        try:
            self.signals.on_start.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename)
            # self.filename = f"{self.ftp_conn.pwd()}/{self.filename}"
            filepath = os.path.join(self.folder_to_save, self.filename)
            with open(filepath, 'wb') as fp:
                self.ftp_conn.retrbinary(f'RETR {os.path.split(self.filename)[1]}', fp.write)
        except Exception as e:
            self.signals.on_error.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename, e)
        else:
            self.signals.on_finished.emit(self.ftp_conn.host, self.ftp_conn.port, self.filename)
