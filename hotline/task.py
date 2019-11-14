from PyQt5 import QtCore
import inbox
import asyncio
import ftplib


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
