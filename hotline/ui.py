# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\media\appui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\media\appui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import logging
import os
import dbfunctions
import valid
import sqlite3
import ftp
import datetime
import configuration
import task
import ftplib
import knownpaths
import inbox


class FtpClientTabWidget(QtWidgets.QWidget):
    def __init__(self, ftp_conn: ftplib.FTP, container: QtWidgets.QTabBar, thread_pool: QtCore.QThreadPool,
                 notificationsTable: QtWidgets.QTableWidget, tabWidget: QtWidgets.QTabBar, *args, **kwargs):
        super(FtpClientTabWidget, self).__init__(*args, **kwargs)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.innerLayout = QtWidgets.QVBoxLayout()
        self.ftp_conn = ftp_conn
        self.thread_pool = thread_pool
        self.notificationsTableWidget = notificationsTable
        self.tabWidget = tabWidget
        self.topWindowFieldsLayout = QtWidgets.QFormLayout()
        self.container = container
        self.currentFolderLabel = QtWidgets.QLabel(self)
        self.currentFolderLabel.setText("Current folder:")
        self.topWindowFieldsLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.currentFolderLabel)
        self.currentFolderLineEdit = QtWidgets.QLineEdit(self)
        self.currentFolderLineEdit.setReadOnly(True)
        self.currentFolderLineEdit.setText(self.ftp_conn.pwd())
        self.topWindowFieldsLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.currentFolderLineEdit)
        self.innerLayout.addLayout(self.topWindowFieldsLayout)

        self.ftpServerFilesTableWidget = QtWidgets.QTableWidget(self)
        self.ftpServerFilesTableWidget.setColumnCount(0)
        self.ftpServerFilesTableWidget.setRowCount(0)
        self.innerLayout.addWidget(self.ftpServerFilesTableWidget)

        self.optionsLayout = QtWidgets.QHBoxLayout()
        self.goBackPushButton = QtWidgets.QPushButton(self)
        self.goBackPushButton.setText("Go back")
        self.goBackPushButton.clicked.connect(self.goBackPushButtonAction)
        self.optionsLayout.addWidget(self.goBackPushButton)

        buttonsSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.optionsLayout.addItem(buttonsSpacer)

        self.uploadPushButton = QtWidgets.QPushButton(self)
        self.uploadPushButton.setText("Upload file")
        self.uploadPushButton.clicked.connect(self.uploadPushButtonAction)
        self.optionsLayout.addWidget(self.uploadPushButton)

        self.refreshPushButton = QtWidgets.QPushButton(self)
        self.refreshPushButton.setText("Refresh")
        self.refreshPushButton.clicked.connect(self.refreshPushButtonAction)
        self.optionsLayout.addWidget(self.refreshPushButton)

        self.innerLayout.addLayout(self.optionsLayout)
        self.verticalLayout.addLayout(self.innerLayout)
        self.setupftpServerFilesTable()
        self.loadDirContentInFtpServerFilesTable()

    def setupftpServerFilesTable(self):
        headers = ['File name', 'Type', 'Size', 'Actions']
        self.ftpServerFilesTableWidget.setColumnCount(len(headers))
        self.ftpServerFilesTableWidget.setHorizontalHeaderLabels(headers)
        header = self.ftpServerFilesTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

    @QtCore.pyqtSlot()
    def uploadPushButtonAction(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file to upload',
                                                         knownpaths.get_path(knownpaths.FOLDERID.Documents,
                                                                             knownpaths.UserHandle.current))[0]
        if not os.path.isfile(filename):
            return
        logging.info(f"Filen selected: '{filename}'")
        uploader = task.UploadFileThread(filename, self.ftp_conn)
        uploader.signals.on_start.connect(self.uploadFileOnStart)
        uploader.signals.on_error.connect(self.uploadFileOnError)
        uploader.signals.on_finished.connect(self.uploadFileOnFinished)
        uploader.signals.on_end.connect(self.uploadFileOnEnd)
        self.thread_pool.start(uploader)

    def freezeControls(self):
        self.goBackPushButton.setEnabled(False)
        self.refreshPushButton.setEnabled(False)
        self.uploadPushButton.setEnabled(False)
        self.ftpServerFilesTableWidget.setEnabled(False)

    def unfreezeControls(self):
        self.goBackPushButton.setEnabled(True)
        self.refreshPushButton.setEnabled(True)
        self.uploadPushButton.setEnabled(True)
        self.ftpServerFilesTableWidget.setEnabled(True)

    @QtCore.pyqtSlot(str, int, str)
    def uploadFileOnStart(self, ip, port, filename):
        logging.info(f"Uploading '{filename}' to {ip}:{port}")
        self.addNotificationToNotificationsTable(f"Uploading '{filename}' to {ip}:{port}")
        self.freezeControls()

    @QtCore.pyqtSlot(str, int, str, 'PyQt_PyObject')
    def uploadFileOnError(self, ip, port, filename, e):
        logging.info(f"Could not upload '{filename}' to {ip}:{port} error: {e}")
        self.addNotificationToNotificationsTable(f"Could not upload '{filename}' to {ip}:{port} error: {e}")

    @QtCore.pyqtSlot(str, int, str)
    def uploadFileOnFinished(self, ip, port, filename):
        logging.info(f"'{filename}' was uploaded to {ip}:{port}")
        self.addNotificationToNotificationsTable(f"'{filename}' was uploaded to {ip}:{port}")

    @QtCore.pyqtSlot()
    def uploadFileOnEnd(self):
        logging.info('The upload thread has finished, reactivating buttons')
        self.unfreezeControls()

    def loadDirContentInFtpServerFilesTable(self):
        self.freezeControls()
        while self.ftpServerFilesTableWidget.rowCount():
            self.ftpServerFilesTableWidget.removeRow(0)

        try:
            for filename, fileinfo in self.ftp_conn.mlsd():
                row = self.ftpServerFilesTableWidget.rowCount()
                self.ftpServerFilesTableWidget.insertRow(row)

                item = QtWidgets.QTableWidgetItem(filename)
                item.setFlags((item.flags() ^ QtCore.Qt.ItemIsEditable))
                self.ftpServerFilesTableWidget.setItem(row, 0, item)

                item = QtWidgets.QTableWidgetItem(fileinfo['type'])
                item.setFlags((item.flags() ^ QtCore.Qt.ItemIsEditable))
                self.ftpServerFilesTableWidget.setItem(row, 1, item)

                item = QtWidgets.QTableWidgetItem(f"{fileinfo['size']} bytes")
                item.setFlags((item.flags() ^ QtCore.Qt.ItemIsEditable))
                self.ftpServerFilesTableWidget.setItem(row, 2, item)

                if fileinfo['type'] == 'dir':
                    open_button = QtWidgets.QPushButton(self)
                    open_button.setText('Open folder')
                    open_button.clicked.connect(self.change_folder)
                    self.ftpServerFilesTableWidget.setCellWidget(row, 3, open_button)
                else:
                    download_button = QtWidgets.QPushButton(self)
                    download_button.setText('Download file')
                    download_button.clicked.connect(self.downloadPushButtonAction)
                    self.ftpServerFilesTableWidget.setCellWidget(row, 3, download_button)
        except Exception as e:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("The connection was interrumpted")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
            answer = msg.exec_()
            self.erase_myself()

        self.unfreezeControls()

    @QtCore.pyqtSlot()
    def change_folder(self):
        btn = self.sender()
        if btn:
            self.freezeControls()
            row = self.ftpServerFilesTableWidget.indexAt(btn.pos()).row()
            dirname = self.ftpServerFilesTableWidget.item(row, 0).text()
            try:
                self.ftp_conn.cwd(dirname)
                self.currentFolderLineEdit.setText(self.ftp_conn.pwd())
                self.loadDirContentInFtpServerFilesTable()
            except Exception as e:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle('Error')
                msg.setText("The connection was interrumpted")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()
                self.erase_myself()

            self.unfreezeControls()

    @QtCore.pyqtSlot()
    def refreshPushButtonAction(self):
        self.loadDirContentInFtpServerFilesTable()

    @QtCore.pyqtSlot()
    def downloadPushButtonAction(self):
        btn = self.sender()
        if btn:
            row = self.ftpServerFilesTableWidget.indexAt(btn.pos()).row()
            filename = self.ftpServerFilesTableWidget.item(row, 0).text()

            download_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder to save the file')
            if not os.path.isdir(download_dir):
                return

            downloadThread = task.DownloadFileThread(filename, self.ftp_conn, download_dir)
            downloadThread.signals.on_start.connect(self.downloadFileOnStart)
            downloadThread.signals.on_error.connect(self.downloadFileOnError)
            downloadThread.signals.on_finished.connect(self.downloadFileOnFinished)
            downloadThread.signals.on_end.connect(self.downloadFileOnEnd)
            self.thread_pool.start(downloadThread)

    @QtCore.pyqtSlot(str, int, str)
    def downloadFileOnStart(self, ip, port, filename):
        logging.info(f"Downloading '{filename}' from {ip}:{port}")
        self.addNotificationToNotificationsTable(f"Downloading '{filename}' from {ip}:{port}")
        self.freezeControls()

    @QtCore.pyqtSlot(str, int, str, 'PyQt_PyObject')
    def downloadFileOnError(self, ip, port, filename, e):
        logging.info(f"Could not download '{filename}' from {ip}:{port} error: {e}")
        self.addNotificationToNotificationsTable(f"Could not download '{filename}' from {ip}:{port} error: {e}")

    @QtCore.pyqtSlot(str, int, str)
    def downloadFileOnFinished(self, ip, port, filename):
        logging.info(f"'{filename}' was downloaded from {ip}:{port}")
        self.addNotificationToNotificationsTable(f"'{filename}' was downloaded from {ip}:{port}")

    @QtCore.pyqtSlot()
    def downloadFileOnEnd(self):
        self.unfreezeControls()

    @QtCore.pyqtSlot()
    def goBackPushButtonAction(self):
        self.freezeControls()
        try:
            self.ftp_conn.cwd('..')
            self.currentFolderLineEdit.setText(self.ftp_conn.pwd())
            self.loadDirContentInFtpServerFilesTable()
        except Exception as e:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText("The connection was interrumpted")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
            answer = msg.exec_()
            self.erase_myself()

        self.unfreezeControls()

    def erase_myself(self):
        self.container.removeTab(self.container.currentIndex())

    def addNotificationToNotificationsTable(self, notification, time=None):
        if not time:
            time = datetime.datetime.now()
        row = self.notificationsTableWidget.rowCount()
        self.notificationsTableWidget.insertRow(row)
        item = QtWidgets.QTableWidgetItem(time.strftime('%b %d %Y %I:%M %p'))
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.notificationsTableWidget.setItem(row, 0, item)
        item = QtWidgets.QTableWidgetItem(notification)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.notificationsTableWidget.setItem(row, 1, item)
        self.tabWidget.setTabText(5, "Notifications*")


class Ui_HotlineMainWindow(object):
    def setupUi(self, HotlineMainWindow):
        HotlineMainWindow.setObjectName("HotlineMainWindow")
        HotlineMainWindow.resize(792, 600)
        self.centralwidget = QtWidgets.QWidget(HotlineMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabChats = QtWidgets.QWidget()
        self.tabChats.setObjectName("tabChats")
        self.verticalLayout_26 = QtWidgets.QVBoxLayout(self.tabChats)
        self.verticalLayout_26.setObjectName("verticalLayout_26")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.conversationsGroupBox = QtWidgets.QGroupBox(self.tabChats)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.conversationsGroupBox.sizePolicy().hasHeightForWidth())
        self.conversationsGroupBox.setSizePolicy(sizePolicy)
        self.conversationsGroupBox.setMinimumSize(QtCore.QSize(221, 0))
        self.conversationsGroupBox.setMaximumSize(QtCore.QSize(221, 16777215))
        self.conversationsGroupBox.setObjectName("conversationsGroupBox")
        self.verticalLayout_23 = QtWidgets.QVBoxLayout(self.conversationsGroupBox)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.verticalLayout_21 = QtWidgets.QVBoxLayout()
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.conversationsTableWidget = QtWidgets.QTableWidget(self.conversationsGroupBox)
        self.conversationsTableWidget.setObjectName("conversationsTableWidget")
        self.conversationsTableWidget.setColumnCount(0)
        self.conversationsTableWidget.setRowCount(0)
        self.verticalLayout_21.addWidget(self.conversationsTableWidget)
        self.verticalLayout_23.addLayout(self.verticalLayout_21)
        self.horizontalLayout_16.addWidget(self.conversationsGroupBox)
        self.chatGroupBox = QtWidgets.QGroupBox(self.tabChats)
        self.chatGroupBox.setObjectName("chatGroupBox")
        self.verticalLayout_25 = QtWidgets.QVBoxLayout(self.chatGroupBox)
        self.verticalLayout_25.setObjectName("verticalLayout_25")
        self.verticalLayout_24 = QtWidgets.QVBoxLayout()
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.chatMateMacAddressLabel = QtWidgets.QLabel(self.chatGroupBox)
        self.chatMateMacAddressLabel.setObjectName("chatMateMacAddressLabel")
        self.horizontalLayout_14.addWidget(self.chatMateMacAddressLabel)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.chatMateFilesPushButton = QtWidgets.QPushButton(self.chatGroupBox)
        self.chatMateFilesPushButton.setObjectName("chatMateFilesPushButton")
        self.horizontalLayout_13.addWidget(self.chatMateFilesPushButton)
        self.horizontalLayout_14.addLayout(self.horizontalLayout_13)
        self.verticalLayout_24.addLayout(self.horizontalLayout_14)
        self.chatTextEdit = QtWidgets.QTextEdit(self.chatGroupBox)
        self.chatTextEdit.setReadOnly(True)
        self.chatTextEdit.setObjectName("chatTextEdit")
        self.verticalLayout_24.addWidget(self.chatTextEdit)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.messageLineEdit = QtWidgets.QLineEdit(self.chatGroupBox)
        self.messageLineEdit.setObjectName("messageLineEdit")
        self.horizontalLayout_15.addWidget(self.messageLineEdit)
        self.sendMessagePushButton = QtWidgets.QPushButton(self.chatGroupBox)
        self.sendMessagePushButton.setObjectName("sendMessagePushButton")
        self.horizontalLayout_15.addWidget(self.sendMessagePushButton)
        self.verticalLayout_24.addLayout(self.horizontalLayout_15)
        self.verticalLayout_25.addLayout(self.verticalLayout_24)
        self.horizontalLayout_16.addWidget(self.chatGroupBox)
        self.verticalLayout_26.addLayout(self.horizontalLayout_16)
        self.tabWidget.addTab(self.tabChats, "")
        self.tabContacts = QtWidgets.QWidget()
        self.tabContacts.setObjectName("tabContacts")
        self.verticalLayout_28 = QtWidgets.QVBoxLayout(self.tabContacts)
        self.verticalLayout_28.setObjectName("verticalLayout_28")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.contactsDbGroupBox = QtWidgets.QGroupBox(self.tabContacts)
        self.contactsDbGroupBox.setObjectName("contactsDbGroupBox")
        self.verticalLayout_27 = QtWidgets.QVBoxLayout(self.contactsDbGroupBox)
        self.verticalLayout_27.setObjectName("verticalLayout_27")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.searchContactLineEdit = QtWidgets.QLineEdit(self.contactsDbGroupBox)
        self.searchContactLineEdit.setObjectName("searchContactLineEdit")
        self.horizontalLayout.addWidget(self.searchContactLineEdit)
        self.findContactPushButton = QtWidgets.QPushButton(self.contactsDbGroupBox)
        self.findContactPushButton.setObjectName("findContactPushButton")
        self.horizontalLayout.addWidget(self.findContactPushButton)
        self.searchContactCriteriaComboBox = QtWidgets.QComboBox(self.contactsDbGroupBox)
        self.searchContactCriteriaComboBox.setObjectName("searchContactCriteriaComboBox")
        self.searchContactCriteriaComboBox.addItem("")
        self.searchContactCriteriaComboBox.addItem("")
        self.horizontalLayout.addWidget(self.searchContactCriteriaComboBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.contactsTableWidget = QtWidgets.QTableWidget(self.contactsDbGroupBox)
        self.contactsTableWidget.setObjectName("contactsTableWidget")
        self.contactsTableWidget.setColumnCount(0)
        self.contactsTableWidget.setRowCount(0)
        self.verticalLayout_3.addWidget(self.contactsTableWidget)
        self.verticalLayout_27.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addWidget(self.contactsDbGroupBox)
        self.newContactGroupBox = QtWidgets.QGroupBox(self.tabContacts)
        self.newContactGroupBox.setObjectName("newContactGroupBox")
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout(self.newContactGroupBox)
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.nameLabel = QtWidgets.QLabel(self.newContactGroupBox)
        self.nameLabel.setObjectName("nameLabel")
        self.horizontalLayout_2.addWidget(self.nameLabel)
        self.newContactNameLineEdit = QtWidgets.QLineEdit(self.newContactGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newContactNameLineEdit.sizePolicy().hasHeightForWidth())
        self.newContactNameLineEdit.setSizePolicy(sizePolicy)
        self.newContactNameLineEdit.setMinimumSize(QtCore.QSize(30, 0))
        self.newContactNameLineEdit.setMaximumSize(QtCore.QSize(115, 16777215))
        self.newContactNameLineEdit.setText("")
        self.newContactNameLineEdit.setObjectName("newContactNameLineEdit")
        self.horizontalLayout_2.addWidget(self.newContactNameLineEdit)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.macAddressLabel = QtWidgets.QLabel(self.newContactGroupBox)
        self.macAddressLabel.setObjectName("macAddressLabel")
        self.horizontalLayout_3.addWidget(self.macAddressLabel)
        self.newContactMacAddressLineEdit = QtWidgets.QLineEdit(self.newContactGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newContactMacAddressLineEdit.sizePolicy().hasHeightForWidth())
        self.newContactMacAddressLineEdit.setSizePolicy(sizePolicy)
        self.newContactMacAddressLineEdit.setMinimumSize(QtCore.QSize(65, 0))
        self.newContactMacAddressLineEdit.setMaximumSize(QtCore.QSize(91, 16777215))
        self.newContactMacAddressLineEdit.setText("")
        self.newContactMacAddressLineEdit.setObjectName("newContactMacAddressLineEdit")
        self.horizontalLayout_3.addWidget(self.newContactMacAddressLineEdit)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label = QtWidgets.QLabel(self.newContactGroupBox)
        self.label.setObjectName("label")
        self.horizontalLayout_10.addWidget(self.label)
        self.newContactIpv4AddressLineEdit = QtWidgets.QLineEdit(self.newContactGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newContactIpv4AddressLineEdit.sizePolicy().hasHeightForWidth())
        self.newContactIpv4AddressLineEdit.setSizePolicy(sizePolicy)
        self.newContactIpv4AddressLineEdit.setMinimumSize(QtCore.QSize(80, 0))
        self.newContactIpv4AddressLineEdit.setMaximumSize(QtCore.QSize(91, 16777215))
        self.newContactIpv4AddressLineEdit.setText("")
        self.newContactIpv4AddressLineEdit.setObjectName("newContactIpv4AddressLineEdit")
        self.horizontalLayout_10.addWidget(self.newContactIpv4AddressLineEdit)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_2 = QtWidgets.QLabel(self.newContactGroupBox)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_11.addWidget(self.label_2)
        self.newContactIpv6AddressLineEdit = QtWidgets.QLineEdit(self.newContactGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newContactIpv6AddressLineEdit.sizePolicy().hasHeightForWidth())
        self.newContactIpv6AddressLineEdit.setSizePolicy(sizePolicy)
        self.newContactIpv6AddressLineEdit.setMinimumSize(QtCore.QSize(70, 0))
        self.newContactIpv6AddressLineEdit.setMaximumSize(QtCore.QSize(165, 16777215))
        self.newContactIpv6AddressLineEdit.setText("")
        self.newContactIpv6AddressLineEdit.setObjectName("newContactIpv6AddressLineEdit")
        self.horizontalLayout_11.addWidget(self.newContactIpv6AddressLineEdit)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.inboxPortLabel = QtWidgets.QLabel(self.newContactGroupBox)
        self.inboxPortLabel.setObjectName("inboxPortLabel")
        self.horizontalLayout_18.addWidget(self.inboxPortLabel)
        self.newContactInboxPortSpinBox = QtWidgets.QSpinBox(self.newContactGroupBox)
        self.newContactInboxPortSpinBox.setMaximum(65535)
        self.newContactInboxPortSpinBox.setProperty("value", 42000)
        self.newContactInboxPortSpinBox.setObjectName("newContactInboxPortSpinBox")
        self.horizontalLayout_18.addWidget(self.newContactInboxPortSpinBox)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.fTPPortLabel = QtWidgets.QLabel(self.newContactGroupBox)
        self.fTPPortLabel.setObjectName("fTPPortLabel")
        self.horizontalLayout_19.addWidget(self.fTPPortLabel)
        self.newContactFtpPortSpinBox = QtWidgets.QSpinBox(self.newContactGroupBox)
        self.newContactFtpPortSpinBox.setMaximum(65535)
        self.newContactFtpPortSpinBox.setProperty("value", 21)
        self.newContactFtpPortSpinBox.setObjectName("newContactFtpPortSpinBox")
        self.horizontalLayout_19.addWidget(self.newContactFtpPortSpinBox)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        spacerItem1 = QtWidgets.QSpacerItem(13, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem1)
        self.addNewContactPushButton = QtWidgets.QPushButton(self.newContactGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addNewContactPushButton.sizePolicy().hasHeightForWidth())
        self.addNewContactPushButton.setSizePolicy(sizePolicy)
        self.addNewContactPushButton.setMinimumSize(QtCore.QSize(70, 0))
        self.addNewContactPushButton.setMaximumSize(QtCore.QSize(70, 16777215))
        self.addNewContactPushButton.setObjectName("addNewContactPushButton")
        self.horizontalLayout_17.addWidget(self.addNewContactPushButton)
        self.horizontalLayout_20.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_21.addLayout(self.horizontalLayout_20)
        self.verticalLayout_2.addWidget(self.newContactGroupBox)
        self.verticalLayout_28.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.tabContacts, "")
        self.tabFTP = QtWidgets.QWidget()
        self.tabFTP.setObjectName("tabFTP")
        self.verticalLayout_31 = QtWidgets.QVBoxLayout(self.tabFTP)
        self.verticalLayout_31.setObjectName("verticalLayout_31")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_19 = QtWidgets.QVBoxLayout()
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.ftpServerConfigGroupBox = QtWidgets.QGroupBox(self.tabFTP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpServerConfigGroupBox.sizePolicy().hasHeightForWidth())
        self.ftpServerConfigGroupBox.setSizePolicy(sizePolicy)
        self.ftpServerConfigGroupBox.setMinimumSize(QtCore.QSize(254, 0))
        self.ftpServerConfigGroupBox.setMaximumSize(QtCore.QSize(254, 16777215))
        self.ftpServerConfigGroupBox.setObjectName("ftpServerConfigGroupBox")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.ftpServerConfigGroupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.formLayout_5 = QtWidgets.QFormLayout()
        self.formLayout_5.setObjectName("formLayout_5")
        self.iPAddressLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.iPAddressLabel.setObjectName("iPAddressLabel")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.iPAddressLabel)
        self.ftpIpAddressLineEdit = QtWidgets.QLineEdit(self.ftpServerConfigGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpIpAddressLineEdit.sizePolicy().hasHeightForWidth())
        self.ftpIpAddressLineEdit.setSizePolicy(sizePolicy)
        self.ftpIpAddressLineEdit.setMinimumSize(QtCore.QSize(110, 0))
        self.ftpIpAddressLineEdit.setMaximumSize(QtCore.QSize(110, 16777215))
        self.ftpIpAddressLineEdit.setText("")
        self.ftpIpAddressLineEdit.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ftpIpAddressLineEdit.setPlaceholderText("")
        self.ftpIpAddressLineEdit.setObjectName("ftpIpAddressLineEdit")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.ftpIpAddressLineEdit)
        self.portLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.portLabel.setObjectName("portLabel")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.portLabel)
        self.ftpPortSpinBox = QtWidgets.QSpinBox(self.ftpServerConfigGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpPortSpinBox.sizePolicy().hasHeightForWidth())
        self.ftpPortSpinBox.setSizePolicy(sizePolicy)
        self.ftpPortSpinBox.setMinimumSize(QtCore.QSize(110, 0))
        self.ftpPortSpinBox.setMaximum(65535)
        self.ftpPortSpinBox.setProperty("value", 21)
        self.ftpPortSpinBox.setObjectName("ftpPortSpinBox")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.ftpPortSpinBox)
        self.maxConnectionsLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.maxConnectionsLabel.setObjectName("maxConnectionsLabel")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.maxConnectionsLabel)
        self.ftpMaxConnectionsSpinBox = QtWidgets.QSpinBox(self.ftpServerConfigGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpMaxConnectionsSpinBox.sizePolicy().hasHeightForWidth())
        self.ftpMaxConnectionsSpinBox.setSizePolicy(sizePolicy)
        self.ftpMaxConnectionsSpinBox.setMinimumSize(QtCore.QSize(110, 0))
        self.ftpMaxConnectionsSpinBox.setMinimum(1)
        self.ftpMaxConnectionsSpinBox.setMaximum(20)
        self.ftpMaxConnectionsSpinBox.setProperty("value", 5)
        self.ftpMaxConnectionsSpinBox.setObjectName("ftpMaxConnectionsSpinBox")
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.ftpMaxConnectionsSpinBox)
        self.maxConnectionsPerIPLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.maxConnectionsPerIPLabel.setObjectName("maxConnectionsPerIPLabel")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.maxConnectionsPerIPLabel)
        self.ftpMaxConnectionsPerIPSpinBox = QtWidgets.QSpinBox(self.ftpServerConfigGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpMaxConnectionsPerIPSpinBox.sizePolicy().hasHeightForWidth())
        self.ftpMaxConnectionsPerIPSpinBox.setSizePolicy(sizePolicy)
        self.ftpMaxConnectionsPerIPSpinBox.setMinimumSize(QtCore.QSize(110, 0))
        self.ftpMaxConnectionsPerIPSpinBox.setMinimum(1)
        self.ftpMaxConnectionsPerIPSpinBox.setMaximum(5)
        self.ftpMaxConnectionsPerIPSpinBox.setProperty("value", 1)
        self.ftpMaxConnectionsPerIPSpinBox.setObjectName("ftpMaxConnectionsPerIPSpinBox")
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.ftpMaxConnectionsPerIPSpinBox)
        self.folderLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.folderLabel.setObjectName("folderLabel")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.folderLabel)
        self.ftpFolderLineEdit = QtWidgets.QLineEdit(self.ftpServerConfigGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpFolderLineEdit.sizePolicy().hasHeightForWidth())
        self.ftpFolderLineEdit.setSizePolicy(sizePolicy)
        self.ftpFolderLineEdit.setMinimumSize(QtCore.QSize(110, 0))
        self.ftpFolderLineEdit.setMaximumSize(QtCore.QSize(110, 16777215))
        self.ftpFolderLineEdit.setObjectName("ftpFolderLineEdit")
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.ftpFolderLineEdit)
        self.usersCanUploadFilesLabel = QtWidgets.QLabel(self.ftpServerConfigGroupBox)
        self.usersCanUploadFilesLabel.setObjectName("usersCanUploadFilesLabel")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.usersCanUploadFilesLabel)
        self.ftpUsersCanUploadFilesCheckBox = QtWidgets.QCheckBox(self.ftpServerConfigGroupBox)
        self.ftpUsersCanUploadFilesCheckBox.setObjectName("ftpUsersCanUploadFilesCheckBox")
        self.formLayout_5.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.ftpUsersCanUploadFilesCheckBox)
        self.verticalLayout_5.addLayout(self.formLayout_5)
        self.verticalLayout_19.addWidget(self.ftpServerConfigGroupBox)
        self.groupBox_7 = QtWidgets.QGroupBox(self.tabFTP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_7.sizePolicy().hasHeightForWidth())
        self.groupBox_7.setSizePolicy(sizePolicy)
        self.groupBox_7.setMinimumSize(QtCore.QSize(254, 0))
        self.groupBox_7.setMaximumSize(QtCore.QSize(254, 16777215))
        self.groupBox_7.setObjectName("groupBox_7")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.groupBox_7)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.ftpBannerPlainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ftpBannerPlainTextEdit.sizePolicy().hasHeightForWidth())
        self.ftpBannerPlainTextEdit.setSizePolicy(sizePolicy)
        self.ftpBannerPlainTextEdit.setMinimumSize(QtCore.QSize(234, 0))
        self.ftpBannerPlainTextEdit.setMaximumSize(QtCore.QSize(234, 16777215))
        self.ftpBannerPlainTextEdit.setPlainText("")
        self.ftpBannerPlainTextEdit.setObjectName("ftpBannerPlainTextEdit")
        self.verticalLayout_15.addWidget(self.ftpBannerPlainTextEdit)
        self.verticalLayout_19.addWidget(self.groupBox_7)
        spacerItem2 = QtWidgets.QSpacerItem(248, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_19.addItem(spacerItem2)
        self.groupBox_8 = QtWidgets.QGroupBox(self.tabFTP)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_8.sizePolicy().hasHeightForWidth())
        self.groupBox_8.setSizePolicy(sizePolicy)
        self.groupBox_8.setMinimumSize(QtCore.QSize(254, 0))
        self.groupBox_8.setMaximumSize(QtCore.QSize(254, 16777215))
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.groupBox_8)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.ftpStartPushButton = QtWidgets.QPushButton(self.groupBox_8)
        self.ftpStartPushButton.setObjectName("ftpStartPushButton")
        self.horizontalLayout_4.addWidget(self.ftpStartPushButton)
        self.ftpShutdownPushButton = QtWidgets.QPushButton(self.groupBox_8)
        self.ftpShutdownPushButton.setObjectName("ftpShutdownPushButton")
        self.horizontalLayout_4.addWidget(self.ftpShutdownPushButton)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout_16.addLayout(self.verticalLayout_4)
        self.verticalLayout_19.addWidget(self.groupBox_8)
        self.horizontalLayout_5.addLayout(self.verticalLayout_19)
        self.verticalLayout_20 = QtWidgets.QVBoxLayout()
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.groupBox_9 = QtWidgets.QGroupBox(self.tabFTP)
        self.groupBox_9.setObjectName("groupBox_9")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.groupBox_9)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.ftpConnectedUsersTableWidget = QtWidgets.QTableWidget(self.groupBox_9)
        self.ftpConnectedUsersTableWidget.setObjectName("ftpConnectedUsersTableWidget")
        self.ftpConnectedUsersTableWidget.setColumnCount(0)
        self.ftpConnectedUsersTableWidget.setRowCount(0)
        self.verticalLayout_17.addWidget(self.ftpConnectedUsersTableWidget)
        self.verticalLayout_20.addWidget(self.groupBox_9)
        self.groupBox_10 = QtWidgets.QGroupBox(self.tabFTP)
        self.groupBox_10.setObjectName("groupBox_10")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout(self.groupBox_10)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.ftpFilesTableWidget = QtWidgets.QTableWidget(self.groupBox_10)
        self.ftpFilesTableWidget.setObjectName("ftpFilesTableWidget")
        self.ftpFilesTableWidget.setColumnCount(0)
        self.ftpFilesTableWidget.setRowCount(0)
        self.verticalLayout_18.addWidget(self.ftpFilesTableWidget)
        self.verticalLayout_20.addWidget(self.groupBox_10)
        self.horizontalLayout_5.addLayout(self.verticalLayout_20)
        self.verticalLayout_31.addLayout(self.horizontalLayout_5)
        self.tabWidget.addTab(self.tabFTP, "")
        self.tabInterlocutor = QtWidgets.QWidget()
        self.tabInterlocutor.setObjectName("tabInterlocutor")
        self.verticalLayout_30 = QtWidgets.QVBoxLayout(self.tabInterlocutor)
        self.verticalLayout_30.setObjectName("verticalLayout_30")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout_22 = QtWidgets.QVBoxLayout()
        self.verticalLayout_22.setObjectName("verticalLayout_22")
        self.groupBox = QtWidgets.QGroupBox(self.tabInterlocutor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(220, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(220, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.formLayout_6 = QtWidgets.QFormLayout()
        self.formLayout_6.setObjectName("formLayout_6")
        self.iPAddressLabel_2 = QtWidgets.QLabel(self.groupBox)
        self.iPAddressLabel_2.setObjectName("iPAddressLabel_2")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.iPAddressLabel_2)
        self.interIpAddressLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.interIpAddressLineEdit.setText("")
        self.interIpAddressLineEdit.setObjectName("interIpAddressLineEdit")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.interIpAddressLineEdit)
        self.portLabel_2 = QtWidgets.QLabel(self.groupBox)
        self.portLabel_2.setObjectName("portLabel_2")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.portLabel_2)
        self.interPortSpinBox = QtWidgets.QSpinBox(self.groupBox)
        self.interPortSpinBox.setMaximum(65535)
        self.interPortSpinBox.setProperty("value", 42000)
        self.interPortSpinBox.setObjectName("interPortSpinBox")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.interPortSpinBox)
        self.passwordLabel = QtWidgets.QLabel(self.groupBox)
        self.passwordLabel.setObjectName("passwordLabel")
        self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.passwordLabel)
        self.interPasswordLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.interPasswordLineEdit.setText("")
        self.interPasswordLineEdit.setObjectName("interPasswordLineEdit")
        self.formLayout_6.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.interPasswordLineEdit)
        self.horizontalLayout_6.addLayout(self.formLayout_6)
        self.verticalLayout_22.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tabInterlocutor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(220, 0))
        self.groupBox_2.setMaximumSize(QtCore.QSize(220, 16777215))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.formLayout_7 = QtWidgets.QFormLayout()
        self.formLayout_7.setObjectName("formLayout_7")
        self.nameLabel_2 = QtWidgets.QLabel(self.groupBox_2)
        self.nameLabel_2.setObjectName("nameLabel_2")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nameLabel_2)
        self.myContactInfoNameLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.myContactInfoNameLineEdit.setText("")
        self.myContactInfoNameLineEdit.setObjectName("myContactInfoNameLineEdit")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.myContactInfoNameLineEdit)
        self.iPLabel = QtWidgets.QLabel(self.groupBox_2)
        self.iPLabel.setObjectName("iPLabel")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.iPLabel)
        self.myContactInfoIpAddressLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.myContactInfoIpAddressLineEdit.setObjectName("myContactInfoIpAddressLineEdit")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.myContactInfoIpAddressLineEdit)
        self.mACAddressLabel = QtWidgets.QLabel(self.groupBox_2)
        self.mACAddressLabel.setObjectName("mACAddressLabel")
        self.formLayout_7.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.mACAddressLabel)
        self.myContactInfoMacAddressLineEdit = QtWidgets.QLineEdit(self.groupBox_2)
        self.myContactInfoMacAddressLineEdit.setText("")
        self.myContactInfoMacAddressLineEdit.setObjectName("myContactInfoMacAddressLineEdit")
        self.formLayout_7.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.myContactInfoMacAddressLineEdit)
        self.onlyByMACLabel = QtWidgets.QLabel(self.groupBox_2)
        self.onlyByMACLabel.setObjectName("onlyByMACLabel")
        self.formLayout_7.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.onlyByMACLabel)
        self.myContactInfoGetOnlyByMacCheckBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.myContactInfoGetOnlyByMacCheckBox.setObjectName("myContactInfoGetOnlyByMacCheckBox")
        self.formLayout_7.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.myContactInfoGetOnlyByMacCheckBox)
        self.inboxPortLabel_2 = QtWidgets.QLabel(self.groupBox_2)
        self.inboxPortLabel_2.setObjectName("inboxPortLabel_2")
        self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.inboxPortLabel_2)
        self.myContactInfoInboxPortSpinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.myContactInfoInboxPortSpinBox.setMaximum(65535)
        self.myContactInfoInboxPortSpinBox.setProperty("value", 42000)
        self.myContactInfoInboxPortSpinBox.setObjectName("myContactInfoInboxPortSpinBox")
        self.formLayout_7.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.myContactInfoInboxPortSpinBox)
        self.verticalLayout_6.addLayout(self.formLayout_7)
        self.verticalLayout_22.addWidget(self.groupBox_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_22.addItem(spacerItem4)
        self.groupBox_11 = QtWidgets.QGroupBox(self.tabInterlocutor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_11.sizePolicy().hasHeightForWidth())
        self.groupBox_11.setSizePolicy(sizePolicy)
        self.groupBox_11.setMinimumSize(QtCore.QSize(220, 0))
        self.groupBox_11.setMaximumSize(QtCore.QSize(220, 16777215))
        self.groupBox_11.setObjectName("groupBox_11")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.groupBox_11)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem5 = QtWidgets.QSpacerItem(160, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem5)
        self.interSignUpPushButton = QtWidgets.QPushButton(self.groupBox_11)
        self.interSignUpPushButton.setObjectName("interSignUpPushButton")
        self.horizontalLayout_8.addWidget(self.interSignUpPushButton)
        self.verticalLayout_9.addLayout(self.horizontalLayout_8)
        self.verticalLayout_10.addLayout(self.verticalLayout_9)
        self.verticalLayout_22.addWidget(self.groupBox_11)
        self.horizontalLayout_9.addLayout(self.verticalLayout_22)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabInterlocutor)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.interSearchLineEdit = QtWidgets.QLineEdit(self.groupBox_3)
        self.interSearchLineEdit.setObjectName("interSearchLineEdit")
        self.horizontalLayout_7.addWidget(self.interSearchLineEdit)
        self.interSearchCriteriaComboBox = QtWidgets.QComboBox(self.groupBox_3)
        self.interSearchCriteriaComboBox.setObjectName("interSearchCriteriaComboBox")
        self.interSearchCriteriaComboBox.addItem("")
        self.interSearchCriteriaComboBox.addItem("")
        self.horizontalLayout_7.addWidget(self.interSearchCriteriaComboBox)
        self.interSearchPushButton = QtWidgets.QPushButton(self.groupBox_3)
        self.interSearchPushButton.setObjectName("interSearchPushButton")
        self.horizontalLayout_7.addWidget(self.interSearchPushButton)
        self.verticalLayout_7.addLayout(self.horizontalLayout_7)
        self.interDbTableWidget = QtWidgets.QTableWidget(self.groupBox_3)
        self.interDbTableWidget.setObjectName("interDbTableWidget")
        self.interDbTableWidget.setColumnCount(0)
        self.interDbTableWidget.setRowCount(0)
        self.verticalLayout_7.addWidget(self.interDbTableWidget)
        self.verticalLayout_8.addLayout(self.verticalLayout_7)
        self.horizontalLayout_9.addWidget(self.groupBox_3)
        self.verticalLayout_30.addLayout(self.horizontalLayout_9)
        self.tabWidget.addTab(self.tabInterlocutor, "")
        self.tabDownloads = QtWidgets.QWidget()
        self.tabDownloads.setObjectName("tabDownloads")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.tabDownloads)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tabDownloads)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.downloadsTabWidget = QtWidgets.QTabWidget(self.groupBox_4)
        self.downloadsTabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.downloadsTabWidget.setTabsClosable(True)
        self.downloadsTabWidget.setMovable(True)
        self.downloadsTabWidget.setObjectName("downloadsTabWidget")
        self.verticalLayout_11.addWidget(self.downloadsTabWidget)
        self.verticalLayout_12.addWidget(self.groupBox_4)
        self.tabWidget.addTab(self.tabDownloads, "")
        self.tabNotifications = QtWidgets.QWidget()
        self.tabNotifications.setObjectName("tabNotifications")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.tabNotifications)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tabNotifications)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.notificationsTableWidget = QtWidgets.QTableWidget(self.groupBox_5)
        self.notificationsTableWidget.setObjectName("notificationsTableWidget")
        self.notificationsTableWidget.setColumnCount(0)
        self.notificationsTableWidget.setRowCount(0)
        self.verticalLayout_13.addWidget(self.notificationsTableWidget)
        self.verticalLayout_14.addWidget(self.groupBox_5)
        self.tabWidget.addTab(self.tabNotifications, "")
        self.verticalLayout.addWidget(self.tabWidget)
        HotlineMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(HotlineMainWindow)
        self.statusbar.setObjectName("statusbar")
        HotlineMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(HotlineMainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.downloadsTabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(HotlineMainWindow)
        HotlineMainWindow.setTabOrder(self.chatMateFilesPushButton, self.ftpIpAddressLineEdit)
        HotlineMainWindow.setTabOrder(self.ftpIpAddressLineEdit, self.ftpPortSpinBox)
        HotlineMainWindow.setTabOrder(self.ftpPortSpinBox, self.ftpMaxConnectionsSpinBox)
        HotlineMainWindow.setTabOrder(self.ftpMaxConnectionsSpinBox, self.ftpMaxConnectionsPerIPSpinBox)
        HotlineMainWindow.setTabOrder(self.ftpMaxConnectionsPerIPSpinBox, self.ftpBannerPlainTextEdit)
        HotlineMainWindow.setTabOrder(self.ftpBannerPlainTextEdit, self.ftpStartPushButton)
        HotlineMainWindow.setTabOrder(self.ftpStartPushButton, self.ftpShutdownPushButton)
        HotlineMainWindow.setTabOrder(self.ftpShutdownPushButton, self.interIpAddressLineEdit)
        HotlineMainWindow.setTabOrder(self.interIpAddressLineEdit, self.interPortSpinBox)
        HotlineMainWindow.setTabOrder(self.interPortSpinBox, self.interPasswordLineEdit)
        HotlineMainWindow.setTabOrder(self.interPasswordLineEdit, self.myContactInfoNameLineEdit)
        HotlineMainWindow.setTabOrder(self.myContactInfoNameLineEdit, self.myContactInfoIpAddressLineEdit)
        HotlineMainWindow.setTabOrder(self.myContactInfoIpAddressLineEdit, self.myContactInfoInboxPortSpinBox)
        HotlineMainWindow.setTabOrder(self.myContactInfoInboxPortSpinBox, self.myContactInfoMacAddressLineEdit)
        HotlineMainWindow.setTabOrder(self.myContactInfoMacAddressLineEdit, self.myContactInfoGetOnlyByMacCheckBox)
        HotlineMainWindow.setTabOrder(self.myContactInfoGetOnlyByMacCheckBox, self.interSignUpPushButton)
        HotlineMainWindow.setTabOrder(self.interSignUpPushButton, self.interSearchLineEdit)
        HotlineMainWindow.setTabOrder(self.interSearchLineEdit, self.interSearchPushButton)
        HotlineMainWindow.setTabOrder(self.interSearchPushButton, self.interDbTableWidget)
        HotlineMainWindow.setTabOrder(self.interDbTableWidget, self.searchContactLineEdit)
        HotlineMainWindow.setTabOrder(self.searchContactLineEdit, self.tabWidget)
        HotlineMainWindow.setTabOrder(self.tabWidget, self.searchContactCriteriaComboBox)
        HotlineMainWindow.setTabOrder(self.searchContactCriteriaComboBox, self.contactsTableWidget)
        HotlineMainWindow.setTabOrder(self.contactsTableWidget, self.newContactNameLineEdit)
        HotlineMainWindow.setTabOrder(self.newContactNameLineEdit, self.newContactMacAddressLineEdit)
        HotlineMainWindow.setTabOrder(self.newContactMacAddressLineEdit, self.newContactIpv4AddressLineEdit)
        HotlineMainWindow.setTabOrder(self.newContactIpv4AddressLineEdit, self.newContactIpv6AddressLineEdit)
        HotlineMainWindow.setTabOrder(self.newContactIpv6AddressLineEdit, self.newContactInboxPortSpinBox)
        HotlineMainWindow.setTabOrder(self.newContactInboxPortSpinBox, self.newContactFtpPortSpinBox)
        HotlineMainWindow.setTabOrder(self.newContactFtpPortSpinBox, self.addNewContactPushButton)
        HotlineMainWindow.setTabOrder(self.addNewContactPushButton, self.chatTextEdit)
        HotlineMainWindow.setTabOrder(self.chatTextEdit, self.messageLineEdit)
        HotlineMainWindow.setTabOrder(self.messageLineEdit, self.sendMessagePushButton)
        HotlineMainWindow.setTabOrder(self.sendMessagePushButton, self.findContactPushButton)
        HotlineMainWindow.setTabOrder(self.findContactPushButton, self.conversationsTableWidget)
        HotlineMainWindow.setTabOrder(self.conversationsTableWidget, self.ftpFolderLineEdit)
        HotlineMainWindow.setTabOrder(self.ftpFolderLineEdit, self.ftpConnectedUsersTableWidget)
        HotlineMainWindow.setTabOrder(self.ftpConnectedUsersTableWidget, self.ftpFilesTableWidget)
        HotlineMainWindow.setTabOrder(self.ftpFilesTableWidget, self.interSearchCriteriaComboBox)
        HotlineMainWindow.setTabOrder(self.interSearchCriteriaComboBox, self.downloadsTabWidget)
        HotlineMainWindow.setTabOrder(self.downloadsTabWidget, self.notificationsTableWidget)

    def retranslateUi(self, HotlineMainWindow):
        _translate = QtCore.QCoreApplication.translate
        HotlineMainWindow.setWindowTitle(_translate("HotlineMainWindow", "Hotline"))
        self.conversationsGroupBox.setTitle(_translate("HotlineMainWindow", "Conversations"))
        self.chatGroupBox.setTitle(_translate("HotlineMainWindow", "A_Username"))
        self.chatMateMacAddressLabel.setText(_translate("HotlineMainWindow", "MAC address"))
        self.chatMateFilesPushButton.setText(_translate("HotlineMainWindow", "Files"))
        self.messageLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "Type your message here"))
        self.sendMessagePushButton.setText(_translate("HotlineMainWindow", "Send"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabChats), _translate("HotlineMainWindow", "Chats"))
        self.contactsDbGroupBox.setTitle(_translate("HotlineMainWindow", "Contacts database"))
        self.searchContactLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "Type here to search contacts"))
        self.findContactPushButton.setText(_translate("HotlineMainWindow", "Find"))
        self.searchContactCriteriaComboBox.setItemText(0, _translate("HotlineMainWindow", "Name"))
        self.searchContactCriteriaComboBox.setItemText(1, _translate("HotlineMainWindow", "MAC address"))
        self.newContactGroupBox.setTitle(_translate("HotlineMainWindow", "New contact"))
        self.nameLabel.setText(_translate("HotlineMainWindow", "Name:"))
        self.newContactNameLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "Muhammad"))
        self.macAddressLabel.setText(_translate("HotlineMainWindow", "MAC:"))
        self.newContactMacAddressLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "aaaa.bbbb.cccc"))
        self.label.setText(_translate("HotlineMainWindow", "IPv4:"))
        self.newContactIpv4AddressLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "192.168.1.89"))
        self.label_2.setText(_translate("HotlineMainWindow", "IPv6:"))
        self.newContactIpv6AddressLineEdit.setPlaceholderText(
            _translate("HotlineMainWindow", "fe80::721c:e7ff:fe61:8a61%19"))
        self.inboxPortLabel.setText(_translate("HotlineMainWindow", "Inbox port:"))
        self.fTPPortLabel.setText(_translate("HotlineMainWindow", "FTP port:"))
        self.addNewContactPushButton.setText(_translate("HotlineMainWindow", "Add"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabContacts), _translate("HotlineMainWindow", "Contacts"))
        self.ftpServerConfigGroupBox.setTitle(_translate("HotlineMainWindow", "FTP server configuration"))
        self.iPAddressLabel.setText(_translate("HotlineMainWindow", "IP address:"))
        self.portLabel.setText(_translate("HotlineMainWindow", "Port:"))
        self.maxConnectionsLabel.setText(_translate("HotlineMainWindow", "Max connections:"))
        self.maxConnectionsPerIPLabel.setText(_translate("HotlineMainWindow", "Max connections per IP:"))
        self.folderLabel.setText(_translate("HotlineMainWindow", "Folder:"))
        self.ftpFolderLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "C:\\Users\\muhammad\\"))
        self.usersCanUploadFilesLabel.setText(_translate("HotlineMainWindow", "Users can upload files:"))
        self.groupBox_7.setTitle(_translate("HotlineMainWindow", "Banner"))
        self.ftpBannerPlainTextEdit.setPlaceholderText(
            _translate("HotlineMainWindow", "Type here a creative banner message :)"))
        self.groupBox_8.setTitle(_translate("HotlineMainWindow", "Options"))
        self.ftpStartPushButton.setText(_translate("HotlineMainWindow", "Start"))
        self.ftpShutdownPushButton.setText(_translate("HotlineMainWindow", "Shutdown"))
        self.groupBox_9.setTitle(_translate("HotlineMainWindow", "Connected users"))
        self.groupBox_10.setTitle(_translate("HotlineMainWindow", "Files and folders"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFTP), _translate("HotlineMainWindow", "FTP"))
        self.groupBox.setTitle(_translate("HotlineMainWindow", "Server information"))
        self.iPAddressLabel_2.setText(_translate("HotlineMainWindow", "IP address:"))
        self.interIpAddressLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "172.16.128.5"))
        self.portLabel_2.setText(_translate("HotlineMainWindow", "Port:"))
        self.passwordLabel.setText(_translate("HotlineMainWindow", "Password:           "))
        self.interPasswordLineEdit.setPlaceholderText(_translate("HotlineMainWindow", "12345"))
        self.groupBox_2.setTitle(_translate("HotlineMainWindow", "My contact information"))
        self.nameLabel_2.setText(_translate("HotlineMainWindow", "Name:"))
        self.iPLabel.setText(_translate("HotlineMainWindow", "IP address:"))
        self.mACAddressLabel.setText(_translate("HotlineMainWindow", "MAC address:"))
        self.onlyByMACLabel.setText(_translate("HotlineMainWindow", "Get only by MAC:"))
        self.inboxPortLabel_2.setText(_translate("HotlineMainWindow", "Inbox port:"))
        self.groupBox_11.setTitle(_translate("HotlineMainWindow", "Options"))
        self.interSignUpPushButton.setText(_translate("HotlineMainWindow", "Sign up"))
        self.groupBox_3.setTitle(_translate("HotlineMainWindow", "Interlocutor database"))
        self.interSearchLineEdit.setPlaceholderText(
            _translate("HotlineMainWindow", "Type here the name or MAC address of the user you want to get"))
        self.interSearchCriteriaComboBox.setItemText(0, _translate("HotlineMainWindow", "Name"))
        self.interSearchCriteriaComboBox.setItemText(1, _translate("HotlineMainWindow", "MAC address"))
        self.interSearchPushButton.setText(_translate("HotlineMainWindow", "Get"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabInterlocutor),
                                  _translate("HotlineMainWindow", "Interlocutor"))
        self.groupBox_4.setTitle(_translate("HotlineMainWindow", "My downloads"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDownloads),
                                  _translate("HotlineMainWindow", "Downloads"))
        self.groupBox_5.setTitle(_translate("HotlineMainWindow", "My notifications"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotifications),
                                  _translate("HotlineMainWindow", "Notifications"))


class HotlineMainWindow(QtWidgets.QMainWindow, Ui_HotlineMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.searchCriteria = 'Name'
        self.findContactSearchPattern = ''
        self.lastMatchingRow = None

        # Each Qt application has one global QThreadPool object, which can be accessed by calling globalInstance() .
        self.threadPool = QtCore.QThreadPool()  # QThreadPool.globalInstance()
        self.threadPool.setMaxThreadCount(12)
        self.ftpServerThread = None

        logging.info(f'max thread count = {self.threadPool.maxThreadCount()}')

        # When user changes between tabs, keep the information ordered
        self.tabWidget.currentChanged.connect(self.onTabChange)

        self.setupFtpTab()
        self.setupInterlocutorTab()
        self.setupContactsTab()
        self.setupChatsTab()
        self.setupNotificationsTab()
        self.setupDownloadsTab()
        self.start_inbox_server()

        if "err" in kwargs:
            self.addNotificationToNotificationsTable(kwargs["err"])

    def setupDownloadsTab(self):
        self.downloadsTabWidget.tabCloseRequested.connect(self.close_download_tab)

    def start_inbox_server(self):
        conn = dbfunctions.get_connection()
        mac, ipv4, ipv6ll, inbox_port = dbfunctions.get_configuration(conn, 'mac_address', 'ipv4_address',
                                                                      'ipv6_address', 'inbox_port')

        logging.info(f'IPv6 = {ipv6ll} IPv4 = {ipv4}')

        inbox_port = inbox_port if inbox_port else 42000
        # TODO: Update in the db the new value

        inboxServerThread6 = inbox.InboxServerThread(ipv6ll, inbox_port)
        inboxServerThread6.signals.on_start.connect(self.inboxServerThreadOnStart)
        inboxServerThread6.signals.on_error.connect(self.inboxServerThreadOnError)
        inboxServerThread6.signals.on_message_received.connect(self.inboxServerThreadOnMessageReceived)
        inboxServerThread6.signals.on_get_contact_information.connect(self.inboxServerThreadOnGetContactInformation)

        inboxServerThread4 = inbox.InboxServerThread(ipv4, inbox_port)
        inboxServerThread4.signals.on_start.connect(self.inboxServerThreadOnStart)
        inboxServerThread4.signals.on_error.connect(self.inboxServerThreadOnError)
        inboxServerThread4.signals.on_message_received.connect(self.inboxServerThreadOnMessageReceived)
        inboxServerThread4.signals.on_get_contact_information.connect(self.inboxServerThreadOnGetContactInformation)

        self.threadPool.start(inboxServerThread4)
        self.threadPool.start(inboxServerThread6)

    @QtCore.pyqtSlot(str, int)
    def inboxServerThreadOnStart(self, ip, port):
        logging.info(f'Inbox server started at {ip}:{port}')
        self.addNotificationToNotificationsTable(f"Waiting for messages on {ip}:{port}")

    @QtCore.pyqtSlot('PyQt_PyObject')
    def inboxServerThreadOnError(self, e):
        logging.info(f'Inbox server error: {e}')
        self.addNotificationToNotificationsTable(f"Inbox server error: {e}")
        self.addNotificationToNotificationsTable(f"You wont be able to receive messages")

    @QtCore.pyqtSlot(dict)
    def inboxServerThreadOnMessageReceived(self, msginfo):
        logging.info(
            f'Message received from {msginfo["mac_address"]}, IP={msginfo["ip"]} , stranger={msginfo["is_stranger"]}')
        # If the contact was a stranger, he was added to contacts and the ip information has been updated in the
        # database, so if its the current user of the chat update the messages, and if its not an stranger, update the info
        # in the table
        if msginfo['is_stranger']:  # Add him to the contacts table and the first chat is going to be him
            conn = dbfunctions.get_connection()
            name, ip4, ip6, inbox_p, ftp_p = dbfunctions.get_contact(conn, msginfo['mac_address'], 'name',
                                                                     'ipv4_address', 'ipv6_address', 'inbox_port',
                                                                     'ftp_port')
            conn.close()
            self.addContactToContactsTable(name, msginfo["mac_address"], ip4, ip6, inbox_p, ftp_p)
            self.addConversationToConversationsTable(msginfo["mac_address"], name)
        else:  # Update the contacts table, and if he is the active chat, update the messages
            for row in range(self.contactsTableWidget.rowCount()):
                if self.contactsTableWidget.item(row, 1).text() == msginfo['mac_address']:
                    name = self.contactsTableWidget.item(row, 0).text()
                    if msginfo['ipv'] == 6:
                        self.contactsTableWidget.item(row, 3).setText(msginfo['ip'])
                    elif msginfo['ipv'] == 4:
                        self.contactsTableWidget.item(row, 2).setText(msginfo['ip'])

                    break

            if self.chatMateMacAddressLabel.text() == msginfo["mac_address"]:
                for row in range(self.conversationsTableWidget.rowCount()):
                    if self.conversationsTableWidget.item(row, 0).text().split('\n')[1] == msginfo["mac_address"]:
                        self.conversationsTableWidget.cellClicked.emit(row, 0)
                        break

        # Notify the user
        if self.chatMateMacAddressLabel.text() == msginfo["mac_address"] and self.tabWidget.currentIndex() == 0:
            pass
        else:
            self.addNotificationToNotificationsTable(f'You have new messages from {name} {msginfo["mac_address"]}')

    @QtCore.pyqtSlot(str)
    def inboxServerThreadOnGetContactInformation(self, remote_ip):
        logging.info(f"{remote_ip} requested contact information")
        self.addNotificationToNotificationsTable(f"{remote_ip} requested contact information")

    @QtCore.pyqtSlot(int)
    def close_download_tab(self, index):
        logging.info(f'Tab {index} closing')
        tab: FtpClientTabWidget = self.downloadsTabWidget.widget(index)
        try:
            tab.ftp_conn.quit()
        except Exception as e:
            logging.error(e)

        self.downloadsTabWidget.removeTab(index)

    def setupChatsTab(self):
        font = QtGui.QFont()
        font.setPointSize(10)
        self.chatTextEdit.setFont(font)
        self.chatGroupBox.setTitle('')
        self.chatMateMacAddressLabel.setText('')
        self.chatMateFilesPushButton.clicked.connect(self.start_ftp_client_connection_fast)
        self.setupConversationsTable()
        self.loadConversationsTable()
        self.sendMessagePushButton.clicked.connect(self.sendMessagePushButtonAction)
        self.messageLineEdit.returnPressed.connect(self.sendMessagePushButtonAction)

    def setupContactsTab(self):
        self.addNewContactPushButton.clicked.connect(self.addNewContactPushButtonAction)
        self.findContactPushButton.clicked.connect(self.findContactInTable)
        self.setupContactsTable()
        self.loadContactsTable()

    def setupFtpTab(self):
        self.ftpIpAddressLineEdit.setReadOnly(True)
        self.ftpShutdownPushButton.setEnabled(False)
        self.ftpStartPushButton.clicked.connect(self.ftpStartPushButtonAction)
        self.ftpShutdownPushButton.clicked.connect(self.ftpShutdownPushButtonAction)
        self.loadFtpConfiguration()
        self.setupFtpFilesTable()
        self.loadFtpFilesTable()

        self.setupFtpConnectedUsersTable()

    def setupInterlocutorTab(self):
        self.myContactInfoIpAddressLineEdit.setReadOnly(True)
        self.myContactInfoMacAddressLineEdit.setReadOnly(True)
        self.myContactInfoInboxPortSpinBox.setReadOnly(True)
        self.loadInterlocutorConfiguration()
        self.setupInterlocutorTable()
        self.interSignUpPushButton.clicked.connect(self.interSignUpPushButtonAction)
        self.interSearchPushButton.clicked.connect(self.interSearchPushButtonAction)

    def setupNotificationsTab(self):
        self.setupNotificationsTable()

    @QtCore.pyqtSlot()
    def sendMessagePushButtonAction(self):
        message = self.messageLineEdit.text().strip()
        message = message.replace('"', "'")
        if not message:
            return

        if len(message) > 10240:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
            msg.setText(f"The message is too large to be sent")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
            answer = msg.exec_()
            return

        remote_mac = self.chatMateMacAddressLabel.text()
        conn = dbfunctions.get_connection()
        ipv4, ipv6, inbox_p, name = dbfunctions.get_contact(conn, remote_mac, 'ipv4_address', 'ipv6_address',
                                                            'inbox_port', 'name')
        user_mac = dbfunctions.get_configuration(conn, 'mac_address')
        conn.close()

        inter_ip = self.interIpAddressLineEdit.text()
        inter_port = self.interPortSpinBox.value()
        inter_password = self.interPasswordLineEdit.text()

        smartSendMessageThread = inbox.SmartSendMessageThread(ipv4, ipv6, inbox_p, remote_mac, user_mac, inter_ip, inter_port, inter_password, message, name, timeout=3)
        smartSendMessageThread.signals.on_success.connect(self.smartSendMessageOnSuccess)
        smartSendMessageThread.signals.on_fail.connect(self.smartSendMessageOnFail)
        self.threadPool.start(smartSendMessageThread)


    @QtCore.pyqtSlot(str, str)
    def smartSendMessageOnFail(self, remote_name, remote_mac):
        logging.info(f"Cannot send message to {remote_name} {remote_mac}")
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(f"Could not send the message to {remote_name}")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    @QtCore.pyqtSlot(dict, str, str, str, dict)
    def smartSendMessageOnSuccess(self, received_confirmation, sent_timestamp, message, ipv_used, contact_information):

        conn = dbfunctions.get_connection()
        dbfunctions.insert_sent_message(conn, sent_timestamp, received_confirmation['receiver'], message, received_confirmation['received_timestamp'])
        conn.close()

        if contact_information:  # Update the contact (ipv4, ipv6, inbox_port, ftp_port)
            for row in range(self.contactsTableWidget.rowCount()):
                if self.contactsTableWidget.item(row, 1).text() == received_confirmation['receiver']:
                    if ipv_used == '4':  # Actualiza todas las IP
                        self.contactsTableWidget.item(row, 2).setText(contact_information['ipv4_address'])
                        self.contactsTableWidget.item(row, 3).setText(contact_information['ipv6_address'])
                    elif ipv_used == '6':  # Elimina la IPv4
                        self.contactsTableWidget.item(row, 2).setText('')
                        self.contactsTableWidget.item(row, 3).setText(contact_information['ipv6_address'])
                    elif ipv_used == '6lleui64':  # Elimina la IPv4 y actualiza la IPv6 a esta direccion
                        self.contactsTableWidget.item(row, 2).setText('')
                        ipv6lleui64 = configuration.generate_ipv6_linklocal_eui64_address(received_confirmation['receiver'])
                        self.contactsTableWidget.item(row, 3).setText(ipv6lleui64)

                    self.contactsTableWidget.cellWidget(row, 4).setValue(contact_information['inbox_port'])
                    self.contactsTableWidget.cellWidget(row, 5).setValue(contact_information['ftp_port'])
                    break
        else:
            for row in range(self.contactsTableWidget.rowCount()):
                if self.contactsTableWidget.item(row, 1).text() == received_confirmation['receiver']:
                    if ipv_used == '4':  # La Ipv4 funciono, no actualices las IP
                        pass
                    elif ipv_used == '6':  # La IPv4 no funciono, pero la 6 si, elimina la IPv4
                        self.contactsTableWidget.item(row, 2).setText('')
                    elif ipv_used == '6lleui64':  # La IPv4 y la IPv6 no funcionaron, pero la IPv6 ll eui64 si, elimina la 4 y actualiza la 6
                        self.contactsTableWidget.item(row, 2).setText('')
                        ipv6lleui64 = configuration.generate_ipv6_linklocal_eui64_address(received_confirmation['receiver'])
                        self.contactsTableWidget.item(row, 3).setText(ipv6lleui64)

                    break

        if self.chatMateMacAddressLabel.text() == received_confirmation['receiver']:
            for row in range(self.conversationsTableWidget.rowCount()):
                if self.conversationsTableWidget.item(row, 0).text().split('\n')[1] == received_confirmation['receiver']:
                    self.conversationsTableWidget.cellClicked.emit(row, 0)
                    break

        self.messageLineEdit.setText('')

    @QtCore.pyqtSlot(int, int)
    def open_conversation_from_table_cell(self, row, col):
        text = self.conversationsTableWidget.item(row, col).text().split('\n')
        name = text[0]
        mac_address = text[1]

        # if mac_address == self.chatMateMacAddressLabel.text():
        #     logging.info('The conversation is opened, update the messages')
        #     self.
        #     return

        self.chatTextEdit.setText('')
        logging.info(f"Opening conversation with '{name}' '{mac_address}'")
        self.chatGroupBox.setTitle(name)
        self.chatMateMacAddressLabel.setText(mac_address)
        conn = dbfunctions.get_connection()
        messages = dbfunctions.last_sent_or_received_messages_from_contact(conn, mac_address, 50)
        conn.close()
        text = ''
        for message in reversed(messages):
            if message['type'] == 'received':
                text = f"[{message['timestamp'].strftime('%b %d %Y %I:%M %p')}]{message['name']}: {message['content']}"
                # text = f"S[{message['sent_timestamp'].strftime('%b %d %Y %I:%M %p')}]  R[{message['timestamp'].strftime('%b %d %Y %I:%M %p')}] {message['name']}: {message['content']}"
                # text += f"""<b>R[ {message['timestamp'].strftime('%b %d %Y %I:%M %p')} ] {message['name']}: </b> <p>{message['content']}</p><br>"""

            else:
                text = f"[{message['received_timestamp'].strftime('%b %d %Y %I:%M %p')}] Me: {message['content']}"
                # text = f"S[{message['timestamp'].strftime('%b %d %Y %I:%M %p')}]  R[{message['received_timestamp'].strftime('%b %d %Y %I:%M %p')}] Me: {message['content']}"
                # text += f"""<b>S[ {message['timestamp'].strftime('%b %d %Y %I:%M %p')} ] {message['name']}: </b> <p>{message['content']}</p><br>"""

            self.chatTextEdit.append(text)
        # self.chatTextEdit.setHtml(text)
        self.messageLineEdit.setFocus()

    @QtCore.pyqtSlot(int, int)
    def update_contact_from_table_cell(self, row, cell):
        mac_address = self.contactsTableWidget.item(row, 1).text()
        new_value = self.contactsTableWidget.item(row, cell).text()
        if cell == 0:  # name changed
            conn = dbfunctions.get_connection()
            try:
                valid.is_name(new_value, exception=True)
                dbfunctions.update_contact(conn, mac_address, name=new_value)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
                try:
                    self.contactsTableWidget.item(row, cell).setText(dbfunctions.get_contact(conn, mac_address, 'name'))
                except Exception as e:
                    logging.error(e)
                    msg = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Critical,
                        'Error',
                        f'{e}',
                        QtWidgets.QMessageBox.Ok
                    )
                    answer = msg.exec_()
                    return
            else:
                logging.info(f"New value '{new_value}' for field 'name' for user '{mac_address}'")
                row_position = -1
                for row in range(self.conversationsTableWidget.rowCount()):
                    if self.conversationsTableWidget.item(row, 0).text().split('\n')[1] == mac_address:
                        self.conversationsTableWidget.item(row, 0).setText(f"{new_value}\n{mac_address}")
                        row_position = row
                        break

                if self.chatMateMacAddressLabel.text() == mac_address:
                    if row_position != -1:
                        self.conversationsTableWidget.cellClicked.emit(row_position, 0)

                    self.chatGroupBox.setTitle(new_value)

            finally:
                conn.close()
        elif cell == 2:
            conn = dbfunctions.get_connection()
            try:
                if not new_value == '':
                    valid.is_ipv4_address(new_value, exception=True)
                dbfunctions.update_contact(conn, mac_address, ipv4_address=new_value)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
                try:
                    self.contactsTableWidget.item(row, cell).setText(
                        dbfunctions.get_contact(conn, mac_address, 'ipv4_address'))
                except Exception as e:
                    logging.error(e)
                    msg = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Critical,
                        'Error',
                        f'{e}',
                        QtWidgets.QMessageBox.Ok
                    )
                    answer = msg.exec_()
                    return
            else:
                logging.info(f"New value '{new_value}' for field 'ipv4_address' for user '{mac_address}'")
            finally:
                conn.close()
        elif cell == 3:
            conn = dbfunctions.get_connection()
            try:
                if not new_value == '':
                    valid.is_ipv6_address(new_value, exception=True)
                dbfunctions.update_contact(conn, mac_address, ipv6_address=new_value)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
                try:
                    self.contactsTableWidget.item(row, cell).setText(
                        dbfunctions.get_contact(conn, mac_address, 'ipv6_address'))
                except Exception as e:
                    logging.error(e)
                    msg = QtWidgets.QMessageBox(
                        QtWidgets.QMessageBox.Critical,
                        'Error',
                        f'{e}',
                        QtWidgets.QMessageBox.Ok
                    )
                    answer = msg.exec_()
                    return
            else:
                logging.info(f"New value '{new_value}' for field 'ipv6_address' for user '{mac_address}'")
            finally:
                conn.close()

    # @QtCore.pyqtSlot(int)
    # def update_contact_inbox_port(self, port):
    @QtCore.pyqtSlot()
    def update_contact_inbox_port(self):
        spin = self.sender()
        if spin:
            port = spin.value()
            row = self.contactsTableWidget.indexAt(spin.pos()).row()
            mac_address = self.contactsTableWidget.item(row, 1).text()
            logging.info(f"New value '{port}' for field 'inbox_port' for user '{mac_address}'")
            conn = dbfunctions.get_connection()
            try:
                dbfunctions.update_contact(conn, mac_address, inbox_port=port)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
            finally:
                conn.close()

    # @QtCore.pyqtSlot(int)
    # def update_contact_ftp_port(self, port):
    @QtCore.pyqtSlot()
    def update_contact_ftp_port(self):
        spin = self.sender()
        if spin:
            port = spin.value()
            row = self.contactsTableWidget.indexAt(spin.pos()).row()
            mac_address = self.contactsTableWidget.item(row, 1).text()
            logging.info(f"New value '{port}' for field 'ftp_port' for user '{mac_address}'")
            conn = dbfunctions.get_connection()
            try:
                dbfunctions.update_contact(conn, mac_address, ftp_port=port)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
            finally:
                conn.close()

    @QtCore.pyqtSlot()
    def start_chat_contact_row(self):
        btn = self.sender()
        if btn:
            row = self.contactsTableWidget.indexAt(btn.pos()).row()
            logging.info(f"Row selected: {row}")
            mac_address = self.contactsTableWidget.item(row, 1).text()
            name = self.contactsTableWidget.item(row, 0).text()
            logging.info(f"Starting chat with '{name}' '{mac_address}'")
            self.tabWidget.setCurrentIndex(0)
            self.messageLineEdit.setFocus()
            self.addConversationToConversationsTable(mac_address, name)

    @QtCore.pyqtSlot()
    def delete_contact_row(self):
        btn = self.sender()
        if btn:
            row = self.contactsTableWidget.indexAt(btn.pos()).row()
            mac_address = self.contactsTableWidget.item(row, 1).text()
            logging.info(f"Deleting Contact '{mac_address}'...")
            conn = dbfunctions.get_connection()
            try:
                dbfunctions.delete_contact(conn, mac_address)
            except Exception as e:
                logging.error(e)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
            else:
                self.contactsTableWidget.removeRow(row)

                for row in range(self.conversationsTableWidget.rowCount()):
                    if mac_address == self.conversationsTableWidget.item(row, 0).text().split()[1]:
                        self.conversationsTableWidget.removeRow(row)
                        break

                if mac_address == self.chatMateMacAddressLabel.text():
                    self.chatMateMacAddressLabel.setText('')
                    self.chatGroupBox.setTitle('')
                    self.chatTextEdit.setText('')

            finally:
                conn.close()

    def nextMatchingRow(self, search_criteria, pattern: str, lastMatchingRow):
        if search_criteria == 'Name':
            for row in range(lastMatchingRow, self.contactsTableWidget.rowCount()):
                name = self.contactsTableWidget.item(row, 0).text()
                if pattern.lower() in name.lower():
                    return row

        elif search_criteria == 'MAC address':
            for row in range(lastMatchingRow, self.contactsTableWidget.rowCount()):
                mac = self.contactsTableWidget.item(row, 1).text()
                if pattern.lower() in mac.lower():
                    return row

    @QtCore.pyqtSlot()
    def findContactInTable(self):
        self.contactsTableWidget.clearSelection()
        newFindContactSearchPattern = self.searchContactLineEdit.text()
        if not newFindContactSearchPattern:
            self.lastMatchingRow = 0
            print('No search pattern specified, restarting last matching row to 0 and exiting')
            return

        newSearchCriteria = self.searchContactCriteriaComboBox.currentText()
        if self.searchCriteria != newSearchCriteria:
            self.searchCriteria = newSearchCriteria
            print('New search criteria = ', self.searchCriteria, 'setting the lastMatchingRow to 0')
            self.lastMatchingRow = 0
        else:  # Restart scrolling
            print('The search criteria is the same, verifying the lastMatchingRow')
            if newFindContactSearchPattern != self.findContactSearchPattern:
                self.findContactSearchPattern = newFindContactSearchPattern
                print('New search pattern = ', self.findContactSearchPattern, 'setting the lasMatchingRow to 0')
                self.lastMatchingRow = 0
            else:
                print('The search pattern is the same')

        row_to_scroll = self.nextMatchingRow(self.searchCriteria, self.findContactSearchPattern, self.lastMatchingRow)
        if row_to_scroll == None:
            self.lastMatchingRow = 0
            row_to_scroll = self.nextMatchingRow(self.searchCriteria, self.findContactSearchPattern,
                                                 self.lastMatchingRow)
            if row_to_scroll == None:
                print(
                    f"None of the values of the '{self.searchCriteria}' matches with '{self.findContactSearchPattern}'")
                return

        print('scrolling to row:', row_to_scroll)
        col = 0 if self.searchCriteria == 'Name' else 1
        item_to_scroll = self.contactsTableWidget.item(row_to_scroll, col)
        self.contactsTableWidget.scrollToItem(item_to_scroll, QtWidgets.QAbstractItemView.PositionAtTop)
        self.contactsTableWidget.selectRow(row_to_scroll)
        # item_to_scroll.setSelected(True)

        self.lastMatchingRow = row_to_scroll + 1
        print('last matching row:', self.lastMatchingRow)

    def loadFtpConfiguration(self):
        conn = dbfunctions.get_connection()
        ipv4, ipv6, max_conn, max_conn_per_ip, folder, banner, port, usr_can_upload = dbfunctions.get_configuration(
            conn, 'ipv4_address', 'ipv6_address', 'ftp_max_connections', 'ftp_max_connections_per_ip', 'ftp_folder',
            'ftp_banner', 'ftp_port', 'ftp_users_can_upload_files')
        conn.close()
        ip = ipv4 if ipv4 else (ipv6 if ipv6 else 'Could not obtain your IP address')
        max_conn = max_conn if max_conn else 10
        max_conn_per_ip = max_conn_per_ip if max_conn_per_ip else 1
        folder = folder if folder and os.path.isdir(folder) else ''
        banner = banner if banner is not None else ''
        port = port if port is not None else 21
        users_can_upload_files = bool(usr_can_upload)
        self.ftpIpAddressLineEdit.setText(ip)
        self.ftpMaxConnectionsSpinBox.setValue(max_conn)
        self.ftpMaxConnectionsPerIPSpinBox.setValue(max_conn_per_ip)
        self.ftpFolderLineEdit.setText(folder)
        self.ftpBannerPlainTextEdit.setPlainText(banner)
        self.ftpPortSpinBox.setValue(port)
        self.ftpUsersCanUploadFilesCheckBox.setChecked(users_can_upload_files)

        self.ftpMaxConnectionsSpinBox.editingFinished.connect(self.save_ftp_max_connections_configuration)
        self.ftpMaxConnectionsPerIPSpinBox.editingFinished.connect(self.save_ftp_max_connections_per_ip_configuration)
        self.ftpPortSpinBox.editingFinished.connect(self.save_ftp_port_configuration)
        self.ftpFolderLineEdit.editingFinished.connect(self.save_ftp_folder_configuration)
        self.ftpUsersCanUploadFilesCheckBox.stateChanged.connect(self.save_ftp_users_can_upload_files_configuration)

    @QtCore.pyqtSlot(int)
    def save_ftp_users_can_upload_files_configuration(self, new_state):
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, ftp_users_can_upload_files=new_state)
        conn.close()
        logging.info(f"New value '{new_state}' for field 'ftp_users_can_upload_files'")

    @QtCore.pyqtSlot()
    def save_ftp_folder_configuration(self):
        new_folder = self.ftpFolderLineEdit.text()
        if new_folder == '':
            conn = dbfunctions.get_connection()
            dbfunctions.update_configuration(conn, ftp_folder=new_folder)
            conn.close()
            logging.info(f"New value '{new_folder}' for field 'ftp_folder'")
            self.loadFtpFilesTable()
        else:
            if os.path.isdir(new_folder):
                conn = dbfunctions.get_connection()
                dbfunctions.update_configuration(conn, ftp_folder=new_folder)
                conn.close()
                logging.info(f"New value '{new_folder}' for field 'ftp_folder'")
                self.loadFtpFilesTable()
            else:
                conn = dbfunctions.get_connection()
                old_folder = dbfunctions.get_configuration(conn, 'ftp_folder')
                conn.close()
                self.ftpFolderLineEdit.setText(old_folder)
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f"'{new_folder}' is not a folder or doesn't exist",
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()

    @QtCore.pyqtSlot()
    def save_ftp_max_connections_per_ip_configuration(self):
        new_value = self.ftpMaxConnectionsPerIPSpinBox.value()
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, ftp_max_connections_per_ip=new_value)
        conn.close()
        logging.info(f"New value '{new_value}' for field 'ftp_max_connections_per_ip'")

    @QtCore.pyqtSlot()
    def save_ftp_max_connections_configuration(self):
        new_value = self.ftpMaxConnectionsSpinBox.value()
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, ftp_max_connections=new_value)
        conn.close()
        logging.info(f"New value '{new_value}' for field 'ftp_max_connections'")

    @QtCore.pyqtSlot()
    def save_ftp_port_configuration(self):
        new_port = self.ftpPortSpinBox.value()
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, ftp_port=new_port)
        conn.close()
        logging.info(f"New value '{new_port}' for field 'ftp_port'")

    def loadInterlocutorConfiguration(self):
        conn = dbfunctions.get_connection()
        inter_address, inter_port, inter_pass, ipv4, username, inbox_port, mac_address, get_only_by_mac = dbfunctions.get_configuration(
            conn, 'interlocutor_address', 'interlocutor_port', 'interlocutor_password', 'ipv4_address', 'username',
            'inbox_port', 'mac_address', 'get_only_by_mac')
        conn.close()
        inter_address = inter_address if inter_address else ''
        inter_port = inter_port if inter_port is not None else 42000
        inter_password = inter_pass if inter_pass is not None else 'secret'
        ipv4 = ipv4 if ipv4 else 'Could not obtain your IP address'
        mac_address = mac_address if mac_address else 'Could not obtain your MAC address'
        username = username if username else 'Muhammad'
        get_only_by_mac = bool(get_only_by_mac)
        self.interIpAddressLineEdit.setText(inter_address)
        self.interPortSpinBox.setValue(inter_port)
        self.interPasswordLineEdit.setText(inter_password)
        self.myContactInfoIpAddressLineEdit.setText(ipv4)
        self.myContactInfoMacAddressLineEdit.setText(mac_address)
        self.myContactInfoNameLineEdit.setText(username)
        self.myContactInfoInboxPortSpinBox.setValue(inbox_port)
        self.myContactInfoGetOnlyByMacCheckBox.setChecked(get_only_by_mac)

        self.interIpAddressLineEdit.editingFinished.connect(self.save_inter_ip_address_configuration)
        self.interPortSpinBox.editingFinished.connect(self.save_inter_port_configuration)
        self.interPasswordLineEdit.editingFinished.connect(self.save_inter_password_configuration)

        self.myContactInfoNameLineEdit.editingFinished.connect(self.save_my_contact_info_name_configuration)
        self.myContactInfoInboxPortSpinBox.editingFinished.connect(self.save_my_contact_info_inbox_port_configuration)
        self.myContactInfoGetOnlyByMacCheckBox.stateChanged.connect(
            self.save_my_contact_info_get_only_by_mac_configuration)

    @QtCore.pyqtSlot(int)
    def save_my_contact_info_get_only_by_mac_configuration(self, new_state):
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, get_only_by_mac=new_state)
        conn.close()
        logging.info(f"New value '{new_state}' for field 'get_only_by_mac'")

    @QtCore.pyqtSlot()
    def save_my_contact_info_inbox_port_configuration(self):
        new_port = self.myContactInfoInboxPortSpinBox.value()
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, inbox_port=new_port)
        conn.close()
        logging.info(f"New value '{new_port}' for field 'inbox_port'")

    @QtCore.pyqtSlot()
    def save_my_contact_info_name_configuration(self):
        new_name = self.myContactInfoNameLineEdit.text()

        try:
            valid.is_name(new_name, True)
        except Exception as e:
            logging.error(e)
            conn = dbfunctions.get_connection()
            old_name = dbfunctions.get_configuration(conn, 'username')
            conn.close()
            self.myContactInfoNameLineEdit.setText(old_name)
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical,
                'Error',
                f'{e}',
                QtWidgets.QMessageBox.Ok
            )
            answer = msg.exec_()
        else:
            conn = dbfunctions.get_connection()
            dbfunctions.update_configuration(conn, username=new_name)
            conn.close()
            logging.info(f"New value '{new_name}' for field 'username'")

    @QtCore.pyqtSlot()
    def save_inter_password_configuration(self):
        new_password = self.interPasswordLineEdit.text()

        try:
            valid.is_valid_password(new_password, True)
        except Exception as e:
            logging.error(e)
            conn = dbfunctions.get_connection()
            old_pass = dbfunctions.get_configuration(conn, 'interlocutor_password')
            conn.close()
            self.interPasswordLineEdit.setText(old_pass)
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical,
                'Error',
                f'{e}',
                QtWidgets.QMessageBox.Ok
            )
            answer = msg.exec_()
        else:
            conn = dbfunctions.get_connection()
            dbfunctions.update_configuration(conn, interlocutor_password=new_password)
            conn.close()
            logging.info(f"New value '{new_password}' for field 'interlocutor_password'")

    @QtCore.pyqtSlot()
    def save_inter_port_configuration(self):
        new_port = self.interPortSpinBox.value()
        conn = dbfunctions.get_connection()
        dbfunctions.update_configuration(conn, interlocutor_port=new_port)
        conn.close()
        logging.info(f"New value '{new_port}' for field 'interlocutor_port'")

    @QtCore.pyqtSlot()
    def save_inter_ip_address_configuration(self):
        new_ip = self.interIpAddressLineEdit.text()

        if new_ip == '':
            conn = dbfunctions.get_connection()
            dbfunctions.update_configuration(conn, interlocutor_address=new_ip)
            conn.close()
            logging.info(f"New value '{new_ip}' for field 'interlocutor_address'")
        else:
            try:
                valid.is_ipv4_address(new_ip, True)
            except Exception as e:
                logging.error(e)
                ##### Recover the last value from the db
                conn = dbfunctions.get_connection()
                old_value = dbfunctions.get_configuration(conn, 'interlocutor_address')
                conn.close()
                self.interIpAddressLineEdit.setText(old_value)

                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f'{e}',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()

            else:
                conn = dbfunctions.get_connection()
                dbfunctions.update_configuration(conn, interlocutor_address=new_ip)
                conn.close()
                logging.info(f"New value '{new_ip}' for field 'interlocutor_address'")

    def setupConversationsTable(self):
        conversationsTableHeaders = ['Contacts']
        self.conversationsTableWidget.setColumnCount(len(conversationsTableHeaders))
        self.conversationsTableWidget.setHorizontalHeaderLabels(conversationsTableHeaders)
        self.conversationsTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.conversationsTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        conversationsTableHeader = self.conversationsTableWidget.horizontalHeader()
        for col in range(len(conversationsTableHeader)):
            conversationsTableHeader.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

    def loadConversationsTable(self):
        conn = dbfunctions.get_connection()
        last_messages = dbfunctions.last_sent_received_messages(conn)
        conn.close()
        self.conversationsTableWidget.setRowCount(len(last_messages))
        try:
            self.conversationsTableWidget.cellClicked.disconnect()
        except:
            pass
        for row, message in enumerate(last_messages):
            item = QtWidgets.QTableWidgetItem(f"{message['name']}\n{message['mac_address']}")
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.conversationsTableWidget.setItem(row, 0, item)
            self.conversationsTableWidget.setRowHeight(row, 40)

        self.conversationsTableWidget.cellClicked.connect(self.open_conversation_from_table_cell)

        if self.conversationsTableWidget.rowCount():
            self.conversationsTableWidget.cellClicked.emit(0, 0)

    def addConversationToConversationsTable(self, mac_address, name):
        try:
            self.conversationsTableWidget.cellClicked.disconnect()
        except:
            pass

        for row in range(self.conversationsTableWidget.rowCount()):
            mac = self.conversationsTableWidget.item(row, 0).text().split('\n')[1]
            if mac_address == mac:
                # The conversation already exists, dont add it, just scroll to the item
                logging.info(f"The conversation with '{mac_address}' exists, scrolling down")
                item_to_scroll = self.conversationsTableWidget.item(row, 0)
                self.conversationsTableWidget.scrollToItem(item_to_scroll, QtWidgets.QAbstractItemView.PositionAtTop)
                self.conversationsTableWidget.cellClicked.connect(self.open_conversation_from_table_cell)
                self.conversationsTableWidget.cellClicked.emit(row, 0)
                self.conversationsTableWidget.clearSelection()
                # self.conversationsTableWidget.selectRow(row)
                self.conversationsTableWidget.item(row, 0).setSelected(True)
                return

        self.conversationsTableWidget.insertRow(0)
        item = QtWidgets.QTableWidgetItem(f"{name}\n{mac_address}")
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.conversationsTableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(item))
        self.conversationsTableWidget.setRowHeight(0, 40)

        self.conversationsTableWidget.cellClicked.connect(self.open_conversation_from_table_cell)
        self.conversationsTableWidget.cellClicked.emit(0, 0)
        self.conversationsTableWidget.clearSelection()
        # self.conversationsTableWidget.selectRow(0)
        self.conversationsTableWidget.item(0, 0).setSelected(True)

    def setupFtpConnectedUsersTable(self):
        tableHeaders = ['IP', 'Port']
        self.ftpConnectedUsersTableWidget.setColumnCount(len(tableHeaders))
        self.ftpConnectedUsersTableWidget.setHorizontalHeaderLabels(tableHeaders)
        hHeader = self.ftpConnectedUsersTableWidget.horizontalHeader()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def setupFtpFilesTable(self):
        tableHeaders = ['Name', 'Type', 'Size']
        self.ftpFilesTableWidget.setColumnCount(len(tableHeaders))
        self.ftpFilesTableWidget.setHorizontalHeaderLabels(tableHeaders)
        ftpFilesHeader = self.ftpFilesTableWidget.horizontalHeader()
        ftpFilesHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        ftpFilesHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        ftpFilesHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    def loadFtpFilesTable(self):
        path = self.ftpFolderLineEdit.text()
        if path == '':
            while self.ftpFilesTableWidget.rowCount():
                self.ftpFilesTableWidget.removeRow(0)
            return
        else:
            logging.info(f"Listing files in '{path}'")
            files = os.listdir(path)
            self.ftpFilesTableWidget.setRowCount(len(files))

            for row, file in enumerate(files):
                if os.path.isdir(os.path.join(path, file)):
                    item = QtWidgets.QTableWidgetItem(file)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 0, item)

                    item = QtWidgets.QTableWidgetItem('Folder')
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 1, item)

                    item = QtWidgets.QTableWidgetItem('Unknown')
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 2, item)
                else:
                    filename, extension = os.path.splitext(file)
                    size = os.path.getsize(os.path.join(path, file))

                    item = QtWidgets.QTableWidgetItem(filename)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 0, item)

                    item = QtWidgets.QTableWidgetItem(extension)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 1, item)

                    item = QtWidgets.QTableWidgetItem(f'{size} bytes')
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.ftpFilesTableWidget.setItem(row, 2, item)

    def setupContactsTable(self):
        contactsTableHeaders = ['Name', 'MAC address', 'IPv4 address', 'IPv6 address',
                                'Inbox port', 'FTP port', 'CHAT', 'FILES', 'UPDATE', 'DELETE']
        self.contactsTableWidget.setColumnCount(len(contactsTableHeaders))
        self.contactsTableWidget.setHorizontalHeaderLabels(contactsTableHeaders)
        contactsTableHeader = self.contactsTableWidget.horizontalHeader()
        for col in range(len(contactsTableHeaders)):
            contactsTableHeader.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)

    def loadContactsTable(self):
        conn = dbfunctions.get_connection()
        contacts = dbfunctions.contacts(conn)
        conn.close()
        self.contactsTableWidget.setRowCount(len(contacts))

        try:
            self.contactsTableWidget.cellChanged.disconnect()
        except:
            pass

        for row, contact in enumerate(contacts):
            self.contactsTableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(contact['name'])))
            mac_address = QtWidgets.QTableWidgetItem(str(contact['mac_address']))
            mac_address.setFlags(mac_address.flags() ^ QtCore.Qt.ItemIsEditable)
            self.contactsTableWidget.setItem(row, 1, mac_address)
            self.contactsTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(contact['ipv4_address'])))
            self.contactsTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(contact['ipv6_address'])))

            inbox_port_spin = QtWidgets.QSpinBox(self.contactsTableWidget)
            inbox_port_spin.setMaximum(65535)
            inbox_port_spin.setMinimum(0)
            inbox_port_spin.setValue(contact['inbox_port'])
            inbox_port_spin.editingFinished.connect(self.update_contact_inbox_port)
            self.contactsTableWidget.setCellWidget(row, 4, inbox_port_spin)

            ftp_port_spin = QtWidgets.QSpinBox(self.contactsTableWidget)
            ftp_port_spin.setMaximum(65535)
            ftp_port_spin.setMinimum(0)
            ftp_port_spin.setValue(contact['ftp_port'])
            ftp_port_spin.editingFinished.connect(self.update_contact_ftp_port)
            self.contactsTableWidget.setCellWidget(row, 5, ftp_port_spin)

            chat_btn = QtWidgets.QPushButton(self.contactsTableWidget)
            chat_btn.setText('Chat')
            chat_btn.clicked.connect(self.start_chat_contact_row)
            self.contactsTableWidget.setCellWidget(row, 6, chat_btn)
            files_btn = QtWidgets.QPushButton(self.contactsTableWidget)
            files_btn.setText('Files')
            files_btn.clicked.connect(self.start_ftp_client_connection)
            self.contactsTableWidget.setCellWidget(row, 7, files_btn)
            delete_btn = QtWidgets.QPushButton(self.contactsTableWidget)

            update_btn = QtWidgets.QPushButton(self.contactsTableWidget)
            update_btn.setText('Update')
            update_btn.clicked.connect(self.start_information_request)
            self.contactsTableWidget.setCellWidget(row, 8, update_btn)

            delete_btn.setText('Delete')
            delete_btn.clicked.connect(self.delete_contact_row)
            self.contactsTableWidget.setCellWidget(row, 9, delete_btn)

        self.contactsTableWidget.cellChanged.connect(self.update_contact_from_table_cell)

    def addContactToContactsTable(self, name, mac_address, ipv4_address, ipv6_address, inbox_port, ftp_port):
        row = self.contactsTableWidget.rowCount()

        try:
            self.contactsTableWidget.cellChanged.disconnect()
        except:
            pass
        self.contactsTableWidget.insertRow(row)
        self.contactsTableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
        mac_address = QtWidgets.QTableWidgetItem(mac_address)
        mac_address.setFlags(mac_address.flags() ^ QtCore.Qt.ItemIsEditable)
        self.contactsTableWidget.setItem(row, 1, mac_address)
        self.contactsTableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(ipv4_address))
        self.contactsTableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(ipv6_address))

        inbox_port_spin = QtWidgets.QSpinBox(self.contactsTableWidget)
        inbox_port_spin.setMaximum(65535)
        inbox_port_spin.setMinimum(0)
        inbox_port_spin.setValue(inbox_port)
        inbox_port_spin.valueChanged.connect(self.update_contact_inbox_port)
        self.contactsTableWidget.setCellWidget(row, 4, inbox_port_spin)

        ftp_port_spin = QtWidgets.QSpinBox(self.contactsTableWidget)
        ftp_port_spin.setMaximum(65535)
        ftp_port_spin.setMinimum(0)
        ftp_port_spin.setValue(ftp_port)
        ftp_port_spin.valueChanged.connect(self.update_contact_ftp_port)
        self.contactsTableWidget.setCellWidget(row, 5, ftp_port_spin)

        chat_btn = QtWidgets.QPushButton(self.contactsTableWidget)
        chat_btn.setText('Chat')
        chat_btn.clicked.connect(self.start_chat_contact_row)
        self.contactsTableWidget.setCellWidget(row, 6, chat_btn)
        files_btn = QtWidgets.QPushButton(self.contactsTableWidget)
        files_btn.setText('Files')
        files_btn.clicked.connect(self.start_ftp_client_connection)
        self.contactsTableWidget.setCellWidget(row, 7, files_btn)
        delete_btn = QtWidgets.QPushButton(self.contactsTableWidget)

        update_btn = QtWidgets.QPushButton(self.contactsTableWidget)
        update_btn.setText('Update')
        update_btn.clicked.connect(self.start_information_request)
        self.contactsTableWidget.setCellWidget(row, 8, update_btn)

        delete_btn.setText('Delete')
        delete_btn.clicked.connect(self.delete_contact_row)
        self.contactsTableWidget.setCellWidget(row, 9, delete_btn)

        self.contactsTableWidget.cellChanged.connect(self.update_contact_from_table_cell)

    @QtCore.pyqtSlot()
    def start_information_request(self):
        btn = self.sender()
        if btn:
            row = self.contactsTableWidget.indexAt(btn.pos()).row()
            name = self.contactsTableWidget.item(row, 0).text()
            mac = self.contactsTableWidget.item(row, 1).text()
            ip4 = self.contactsTableWidget.item(row, 2).text()
            ip6 = self.contactsTableWidget.item(row, 3).text()
            port = self.contactsTableWidget.cellWidget(row, 4).value()

            inter_ip = self.interIpAddressLineEdit.text()
            inter_port = self.interPortSpinBox.value()
            inter_pass = self.interPasswordLineEdit.text()

            ifreqthread = task.RequestContactInformationThread(ip4, ip6, mac, name, port, inter_ip, inter_port, inter_pass, timeout=2)
            ifreqthread.signals.on_fail.connect(self.informationRequestOnFail)
            ifreqthread.signals.on_success.connect(self.informationRequestOnSuccess)
            self.threadPool.start(ifreqthread)

    @QtCore.pyqtSlot(str, str)
    def informationRequestOnFail(self, name, mac):
        logging.info(f'Could not request contact information of {name} {mac}')
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(f'Could not request contact information of {name} {mac}')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    @QtCore.pyqtSlot(dict)
    def informationRequestOnSuccess(self, contact_info):
        logging.info(
            f"Contact information succesfully requested of {contact_info.get('name')} {contact_info.get('mac_address')}")
        print('Algo')
        for row in range(self.contactsTableWidget.rowCount()):
            if contact_info.get('mac_address') == self.contactsTableWidget.item(row, 1).text():
                self.contactsTableWidget.item(row, 2).setText(contact_info.get('ipv4_address'))
                self.contactsTableWidget.cellWidget(row, 4).setValue(contact_info.get('inbox_port'))

                self.contactsTableWidget.item(row, 3).setText(contact_info.get('ipv6_address'))
                self.contactsTableWidget.cellWidget(row, 5).setValue(contact_info.get('ftp_port'))
                conn = dbfunctions.get_connection()
                dbfunctions.update_contact(
                    conn,
                    contact_info.get('mac_address'),
                    inbox_port=contact_info.get('inbox_port'),
                    ftp_port=contact_info.get('ftp_port')
                )
                conn.close()
                success_message = f'{self.contactsTableWidget.item(row, 0).text()} has been updated'
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle('Success in life')
                msg.setText(success_message)
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()
                return


    @QtCore.pyqtSlot()
    def start_ftp_client_connection_fast(self):
        btn = self.sender()
        if btn:
            mac = self.chatMateMacAddressLabel.text()
            conn = dbfunctions.get_connection()
            ip4, name, port = dbfunctions.get_contact(conn, mac, 'ipv4_address', 'name', 'ftp_port')
            conn.close()

            if not ip4:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle('Not enought information')
                msg.setText(f"{name} doesn't have an IPv4 address")
                msg.setInformativeText(f"Please, update {name} by clicking on 'Update' in the contacts table to try to get the IPv4 address of {name}")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()
            else:
                self.startFtpClientConnection(ip4, port)

    @QtCore.pyqtSlot()
    def start_ftp_client_connection(self):
        btn = self.sender()
        if btn:
            row = self.contactsTableWidget.indexAt(btn.pos()).row()
            ip4 = self.contactsTableWidget.item(row, 2).text()
            port = self.contactsTableWidget.cellWidget(row, 5).value()
            if not ip4:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle('Not enought information')
                msg.setText(f"{self.contactsTableWidget.item(row, 0).text()} doesn't have an IPv4 address")
                msg.setInformativeText(f"Please, click on 'Update' to try to get the IPv4 address of {self.contactsTableWidget.item(row, 0).text()}")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()
            else:
                self.startFtpClientConnection(ip4, port)

    def startFtpClientConnection(self, ip, port, timeout=3):
        logging.info(f"Starting FTP client connection with {ip}:{port}")
        startFtpThread = task.StartFtpClientConnectionThread(ip, port, timeout)
        startFtpThread.signals.on_connect.connect(self.startFtpClientConnectionOnConnect)
        startFtpThread.signals.on_finished.connect(self.startFtpClientConnectionOnFinished)
        startFtpThread.signals.on_result.connect(self.startFtpClientConnectionOnResult)
        startFtpThread.signals.on_error.connect(self.startFtpClientConnectionOnError)
        self.threadPool.start(startFtpThread)

    @QtCore.pyqtSlot(str)
    def startFtpClientConnectionOnConnect(self, banner):
        logging.info(f'FTP client connection made: {banner}')

    @QtCore.pyqtSlot('PyQt_PyObject')
    def startFtpClientConnectionOnResult(self, ftp_conn):
        logging.info(f'Succesfully FTP client login')
        self.addFtpClientToDownloadsTab(ftp_conn)

        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle('Success')
        msg.setText("FTP connection established")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

        self.tabWidget.setCurrentIndex(4)

    def addFtpClientToDownloadsTab(self, ftp_conn: ftplib.FTP):
        newDownloadTab = FtpClientTabWidget(ftp_conn, self.downloadsTabWidget, self.threadPool,
                                            self.notificationsTableWidget, self.tabWidget)
        self.downloadsTabWidget.addTab(newDownloadTab, f"{ftp_conn.host}:{ftp_conn.port}")
        print('Tab count=', self.downloadsTabWidget.count())
        self.downloadsTabWidget.setCurrentIndex(self.downloadsTabWidget.count() - 1)

    @QtCore.pyqtSlot(str, int)
    def startFtpClientConnectionOnError(self, ip, port):
        logging.error(f"Could not FTP client connect with {ip}:{port}")
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(f"Could not connect to FTP server {ip}:{port}")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    @QtCore.pyqtSlot()
    def startFtpClientConnectionOnFinished(self):
        logging.info(f"FTP Client connection finished")

    @QtCore.pyqtSlot()
    def addNewContactPushButtonAction(self):
        mac_address = self.newContactMacAddressLineEdit.text().strip()
        name = self.newContactNameLineEdit.text().strip()
        ipv4_address = self.newContactIpv4AddressLineEdit.text().strip()
        ipv6_address = self.newContactIpv6AddressLineEdit.text().strip()
        inbox_port = self.newContactInboxPortSpinBox.value()
        ftp_port = self.newContactFtpPortSpinBox.value()
        try:
            valid.is_name(name, exception=True)
            valid.is_mac_address(mac_address, exception=True)
            ipv4_address = ipv4_address if valid.is_ipv4_address(ipv4_address) else ''
            ipv6_address = ipv6_address if valid.is_ipv6_address(ipv6_address) else ''
        except Exception as e:
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical,
                'Wrong value',
                f'{e}',
                QtWidgets.QMessageBox.Ok
            )
            answer = msg.exec_()
        else:
            try:
                conn = dbfunctions.get_connection()
                dbfunctions.insert_contact(conn, mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port)
            except sqlite3.IntegrityError as e:
                logging.error(f'{e}')
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f"A contact with the MAC address '{mac_address}' is already registered",
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
            else:
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Information,
                    'Success',
                    'The contact was added successfully',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
                self.newContactMacAddressLineEdit.setText('')
                self.newContactNameLineEdit.setText('')
                self.newContactIpv4AddressLineEdit.setText('')
                self.newContactIpv6AddressLineEdit.setText('')
                logging.info(
                    f'nam={name} mac_address={mac_address} ipv4={ipv4_address} ipv6={ipv6_address} inbox={inbox_port} ftp={ftp_port}')
                self.addContactToContactsTable(name, mac_address, ipv4_address, ipv6_address, inbox_port, ftp_port)
            finally:
                conn.close()

    def ftpStartPushButtonAction(self):
        address = self.ftpIpAddressLineEdit.text()
        port = self.ftpPortSpinBox.value()
        max_connections = self.ftpMaxConnectionsSpinBox.value()
        max_connections_per_ip = self.ftpMaxConnectionsPerIPSpinBox.value()
        banner = self.ftpBannerPlainTextEdit.toPlainText()
        folder = self.ftpFolderLineEdit.text()
        users_can_upload_files = self.ftpUsersCanUploadFilesCheckBox.isChecked()
        if not os.path.isdir(folder):
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder to share')
            logging.info(f"Folder selected: '{folder}'")
            if not folder:
                return
            self.ftpFolderLineEdit.setText(folder)
            self.ftpFolderLineEdit.editingFinished.emit()

        logging.info('Starting FTP server...')
        self.ftpServerThread = ftp.FtpServer(address, port, max_connections, max_connections_per_ip, folder, banner,
                                             users_can_upload_files)

        self.ftpServerThread.signals.on_start.connect(self.ftp_server_on_start)
        self.ftpServerThread.signals.on_shutdown.connect(self.ftp_server_on_shutdown)
        self.ftpServerThread.signals.on_error.connect(self.ftp_server_on_error)
        self.ftpServerThread.signals.on_connect.connect(self.ftp_server_on_connect)
        self.ftpServerThread.signals.on_disconnect.connect(self.ftp_server_on_disconnect)

        self.ftpServerThread.signals.on_login.connect(self.ftp_server_on_login)
        self.ftpServerThread.signals.on_logout.connect(self.ftp_server_on_logout)
        self.ftpServerThread.signals.on_file_received.connect(self.ftp_server_on_file_received)
        self.ftpServerThread.signals.on_incomplete_file_received.connect(self.ftp_server_on_incomplete_file_received)

        self.ftpServerThread.signals.on_file_sent.connect(self.ftp_server_on_file_sent)
        self.ftpServerThread.signals.on_incomplete_file_sent.connect(self.ftp_server_on_incomplete_file_sent)

        self.threadPool.start(self.ftpServerThread)

    def ftpShutdownPushButtonAction(self):
        logging.info('Shutting down the FTP server...')
        self.ftpServerThread.my_jorge_shutdown()

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_incomplete_file_received(self, remote_ip, remote_port, filename):
        logging.info(f"{remote_ip}:{remote_port} could not upload '{filename}'")
        self.addNotificationToNotificationsTable(
            f"{remote_ip}:{remote_port} could not upload '{filename}', removing the uploaded part")
        os.remove(filename)  # TODO: Do this in a separate thread

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_incomplete_file_sent(self, remote_ip, remote_port, filename):
        logging.info(f"{remote_ip}:{remote_port} could not download '{filename}'")
        self.addNotificationToNotificationsTable(f"{remote_ip}:{remote_port} could not download '{filename}'")

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_file_received(self, remote_ip, remote_port, filename):
        logging.info(f"{remote_ip}:{remote_port} uploaded '{filename}'")
        self.loadFtpFilesTable()
        self.addNotificationToNotificationsTable(f"{remote_ip}:{remote_port} uploaded '{filename}'")

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_file_sent(self, remote_ip, remote_port, filename):
        logging.info(f"{remote_ip}:{remote_port} downloaded '{filename}'")
        self.addNotificationToNotificationsTable(f"{remote_ip}:{remote_port} downloaded '{filename}'")

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_login(self, remote_ip, remote_port, username):
        logging.info(f"The FTP user '{username}' ({remote_ip}:{remote_port}) has logged in")
        self.addNotificationToNotificationsTable(f"The FTP user '{username}' ({remote_ip}:{remote_port}) has logged in")

    @QtCore.pyqtSlot(str, int, str)
    def ftp_server_on_logout(self, remote_ip, remote_port, username):
        logging.info(f"The FTP user '{username}' ({remote_ip}:{remote_port}) has logged out")
        self.addNotificationToNotificationsTable(
            f"The FTP user '{username}' ({remote_ip}:{remote_port}) has logged out")

    @QtCore.pyqtSlot(str, int)
    def ftp_server_on_connect(self, remote_ip, remote_port):
        self.addUserToFtpConnectedUsersTable(remote_ip, remote_port)
        self.addNotificationToNotificationsTable(f"New FTP connection from {remote_ip}:{remote_port}")

    @QtCore.pyqtSlot(str, int)
    def ftp_server_on_disconnect(self, remote_ip, remote_port):
        self.removeUserToFtpConnectedUsersTable(remote_ip)
        self.addNotificationToNotificationsTable(f"FTP client {remote_ip}:{remote_port} disconnected")

    def addUserToFtpConnectedUsersTable(self, ip, port):
        row = self.ftpConnectedUsersTableWidget.rowCount()
        self.ftpConnectedUsersTableWidget.insertRow(row)
        item = QtWidgets.QTableWidgetItem(ip)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.ftpConnectedUsersTableWidget.setItem(row, 0, item)
        item = QtWidgets.QTableWidgetItem(str(port))
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.ftpConnectedUsersTableWidget.setItem(row, 1, item)

    def removeUserToFtpConnectedUsersTable(self, ip):
        for row in range(self.ftpConnectedUsersTableWidget.rowCount()):
            if self.ftpConnectedUsersTableWidget.item(row, 0).text() == ip:
                self.ftpConnectedUsersTableWidget.removeRow(row)
                return

    @QtCore.pyqtSlot()
    def ftp_server_on_start(self):
        self.ftpPortSpinBox.setEnabled(False)
        self.ftpMaxConnectionsSpinBox.setEnabled(False)
        self.ftpMaxConnectionsPerIPSpinBox.setEnabled(False)
        self.ftpBannerPlainTextEdit.setEnabled(False)
        self.ftpFolderLineEdit.setEnabled(False)
        self.ftpUsersCanUploadFilesCheckBox.setEnabled(False)
        self.ftpStartPushButton.setEnabled(False)
        self.ftpShutdownPushButton.setEnabled(True)
        self.addNotificationToNotificationsTable("The FTP server is running")
        logging.info('The FTP server is running')

    def ftp_server_on_shutdown(self):
        self.ftpPortSpinBox.setEnabled(True)
        self.ftpMaxConnectionsSpinBox.setEnabled(True)
        self.ftpMaxConnectionsPerIPSpinBox.setEnabled(True)
        self.ftpBannerPlainTextEdit.setEnabled(True)
        self.ftpFolderLineEdit.setEnabled(True)
        self.ftpUsersCanUploadFilesCheckBox.setEnabled(True)
        self.ftpStartPushButton.setEnabled(True)
        self.ftpShutdownPushButton.setEnabled(False)
        while self.ftpConnectedUsersTableWidget.rowCount():
            self.ftpConnectedUsersTableWidget.removeRow(0)
        self.addNotificationToNotificationsTable("The FTP server was shutted down")
        logging.info('The FTP server was shutted down')

    @QtCore.pyqtSlot('PyQt_PyObject')
    def ftp_server_on_error(self, ex):
        logging.info(ex)
        msg = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Critical,
            'Error',
            f'{ex}',
            QtWidgets.QMessageBox.Ok
        )
        answer = msg.exec_()

    def onTabChange(self, i):
        self.update_tab(i)

    def update_tab(self, index):
        if index == 0:
            logging.info("Updating 'Chats' tab")
        elif index == 1:
            logging.info("Updating 'Contacts' tab")
        elif index == 2:
            logging.info("Updating 'FTP' tab")
        elif index == 3:
            logging.info("Updating 'Interlocutor' tab")
        elif index == 4:
            logging.info("Updating 'Downloads' tab")
        elif index == 5:
            logging.info("Updating 'Notifications' tab")
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotifications), "Notifications")

    def setupNotificationsTable(self):
        tableHeaders = ['Time', 'Notification']
        self.notificationsTableWidget.setColumnCount(len(tableHeaders))
        self.notificationsTableWidget.setHorizontalHeaderLabels(tableHeaders)
        self.notificationsTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.notificationsTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        hHeader = self.notificationsTableWidget.horizontalHeader()
        hHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        hHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def addNotificationToNotificationsTable(self, notification, time=None):
        if not time:
            time = datetime.datetime.now()
        row = self.notificationsTableWidget.rowCount()
        self.notificationsTableWidget.insertRow(row)
        item = QtWidgets.QTableWidgetItem(time.strftime('%b %d %Y %I:%M %p'))
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.notificationsTableWidget.setItem(row, 0, item)
        item = QtWidgets.QTableWidgetItem(notification)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.notificationsTableWidget.setItem(row, 1, item)

        if self.tabWidget.currentIndex() != 5:
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotifications), "Notifications*")

    @QtCore.pyqtSlot()
    def interSignUpPushButtonAction(self):
        server_address = self.interIpAddressLineEdit.text()
        server_port = self.interPortSpinBox.value()
        server_password = self.interPasswordLineEdit.text()

        mac = self.myContactInfoMacAddressLineEdit.text()
        name = self.myContactInfoNameLineEdit.text()
        getonlybymac = self.myContactInfoGetOnlyByMacCheckBox.isChecked()
        port = self.myContactInfoInboxPortSpinBox.value()

        signUpThread = task.SignUpRequestThread(
            server_address, server_port, server_password, mac, name, port, getonlybymac
        )
        signUpThread.signals.on_start.connect(self.signupOnStart)
        signUpThread.signals.on_result.connect(self.signupOnResult)
        signUpThread.signals.on_error.connect(self.signupOnError)
        self.threadPool.start(signUpThread)

    @QtCore.pyqtSlot()
    def signupOnStart(self):
        logging.info("SignUp request starting")
        self.interSignUpPushButton.setEnabled(False)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def signupOnError(self, exce):
        logging.error(f"SignUp exception: {exce}")
        self.interSignUpPushButton.setEnabled(True)
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(f"Could sign up to interlocutor server")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    @QtCore.pyqtSlot(dict)
    def signupOnResult(self, reply):
        logging.info(f"SignUp result: {reply}")
        self.interSignUpPushButton.setEnabled(True)

        result = reply.get('result')
        if result:
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle('Success')
            msg.setText(f"Interlocutor server says: '{result}'")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
            answer = msg.exec_()
        else:
            error = reply.get('error')
            error_name = reply.get('name')
            if error and error_name:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle('Error')
                msg.setText(f"Interlocutor server says: {error_name} [Error code {error}]")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()

    @QtCore.pyqtSlot()
    def interSearchPushButtonAction(self):

        server_address = self.interIpAddressLineEdit.text()
        server_port = self.interPortSpinBox.value()
        server_password = self.interPasswordLineEdit.text()

        pattern = self.interSearchLineEdit.text()
        if self.interSearchCriteriaComboBox.currentText() == 'Name':
            getThread = task.GetRequestThread(server_address, server_port, server_password, username=pattern)
        else:
            getThread = task.GetRequestThread(server_address, server_port, server_password, mac=pattern)

        getThread.signals.on_finished.connect(self.getRequestOnFinished)
        getThread.signals.on_error.connect(self.getRequestOnError)
        getThread.signals.on_result.connect(self.getRequestOnResult)
        getThread.signals.on_start.connect(self.getRequestOnStart)
        self.threadPool.start(getThread)

    @QtCore.pyqtSlot()
    def getRequestOnStart(self):
        self.interSearchLineEdit.setEnabled(False)
        self.interSearchCriteriaComboBox.setEnabled(False)
        self.interSearchPushButton.setEnabled(False)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def getRequestOnError(self, e):
        logging.info(f'GET error: {e}')
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(
            f"Could not connect to the Interlocutor server")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

    @QtCore.pyqtSlot(dict)
    def getRequestOnResult(self, info):
        logging.info(f'GET result: {info} {type(info)}')

        while self.interDbTableWidget.rowCount():
            self.interDbTableWidget.removeRow(0)

        if info.get('error'):
            pass
        else:
            clients = info.get('clients')
            if clients:
                for client in clients:
                    row = self.interDbTableWidget.rowCount()
                    self.interDbTableWidget.insertRow(row)
                    item = QtWidgets.QTableWidgetItem(client['username'])
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 0, item)
                    item = QtWidgets.QTableWidgetItem(client['ipv4_addr'])
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 1, item)
                    item = QtWidgets.QTableWidgetItem(str(client['port']))
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 2, item)

                    addToContactsButton = QtWidgets.QPushButton('Add to contacts')
                    addToContactsButton.clicked.connect(self.interlocutorAddToContactsButton)
                    self.interDbTableWidget.setCellWidget(row, 3, addToContactsButton)
            else:
                client = info.get('client')
                if client:
                    row = self.interDbTableWidget.rowCount()
                    self.interDbTableWidget.insertRow(row)
                    item = QtWidgets.QTableWidgetItem(client['username'])
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 0, item)
                    item = QtWidgets.QTableWidgetItem(client['ipv4_addr'])
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 1, item)
                    item = QtWidgets.QTableWidgetItem(str(client['port']))
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                    self.interDbTableWidget.setItem(row, 2, item)

                    addToContactsButton = QtWidgets.QPushButton('Add to contacts')
                    addToContactsButton.clicked.connect(self.interlocutorAddToContactsButton)
                    self.interDbTableWidget.setCellWidget(row, 3, addToContactsButton)

    @QtCore.pyqtSlot()
    def interlocutorAddToContactsButton(self):
        button = self.sender()
        if button:
            row = self.interDbTableWidget.indexAt(button.pos()).row()
            name = self.interDbTableWidget.item(row, 0).text()
            ipv4 = self.interDbTableWidget.item(row, 1).text()
            port = self.interDbTableWidget.item(row, 2).text()

            interGetContactInfoThread = task.GetContactInformationThread(ipv4, int(port))
            interGetContactInfoThread.signals.on_result.connect(self.interGetContactInfoThreadOnResult)
            interGetContactInfoThread.signals.on_error.connect(self.interGetContactInfoThreadOnError)
            interGetContactInfoThread.signals.on_finished.connect(self.interGetContactInfoThreadOnFinished)
            logging.info(f"Making a friend request to: '{name}' {ipv4}:{port}")
            self.threadPool.start(interGetContactInfoThread)

    @QtCore.pyqtSlot(dict)
    def interGetContactInfoThreadOnResult(self, new_contact):
        for row in range(self.contactsTableWidget.rowCount()):
            if new_contact.get('mac_address') == self.contactsTableWidget.item(row, 1).text():
                # Contact exists, update
                self.contactsTableWidget.item(row, 2).setText(new_contact['ipv4_address'])
                self.contactsTableWidget.item(row, 3).setText(new_contact['ipv6_address'])
                self.contactsTableWidget.cellWidget(row, 4).setValue(new_contact['inbox_port'])
                self.contactsTableWidget.cellWidget(row, 5).setValue(new_contact['ftp_port'])

                conn = dbfunctions.get_connection()
                dbfunctions.update_contact(conn, new_contact.get('mac_address'), inbox_port=new_contact['inbox_port'], ftp_port=new_contact['ftp_port'])
                conn.close()

                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle('Information')
                msg.setText(
                    f"The contact {new_contact['name']} ({new_contact['mac_address']}) aka {self.contactsTableWidget.item(row, 0).text()} ({self.contactsTableWidget.item(row, 1).text()}) has been updated")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
                answer = msg.exec_()
                return

        # Contact does not exist, add him

        name = new_contact.get('name')
        mac_address = new_contact.get('mac_address')
        ipv4_address = new_contact.get('ipv4_address')
        ipv6_address = new_contact.get('ipv6_address')
        ftp_port = new_contact.get('ftp_port')
        inbox_port = new_contact.get('inbox_port')

        try:
            valid.is_name(name, exception=True)
            valid.is_mac_address(mac_address, exception=True)
            ipv4_address = ipv4_address if valid.is_ipv4_address(ipv4_address) else ''
            ipv6_address = ipv6_address if valid.is_ipv6_address(ipv6_address) else ''
            inbox_port = inbox_port if inbox_port and 0 <= inbox_port <= 65535 else 42000
            ftp_port = ftp_port if ftp_port and 0 <= ftp_port <= 65535 else 21
        except Exception as e:
            msg = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical,
                'Wrong value received',
                f'{e}',
                QtWidgets.QMessageBox.Ok
            )
            answer = msg.exec_()
        else:
            try:
                conn = dbfunctions.get_connection()
                dbfunctions.insert_contact(conn, mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port)
            except sqlite3.IntegrityError as e:
                logging.error(f'{e}')
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Critical,
                    'Error',
                    f"A contact with the MAC address '{mac_address}' is already registered",
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
            else:
                msg = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Information,
                    'Success',
                    'The contact was added successfully',
                    QtWidgets.QMessageBox.Ok
                )
                answer = msg.exec_()
                self.addContactToContactsTable(name, mac_address, ipv4_address, ipv6_address, inbox_port, ftp_port)
            finally:
                conn.close()

    @QtCore.pyqtSlot(str, int)
    def interGetContactInfoThreadOnError(self, ip, port):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText(f"Could not add {ip}:{port} to contacts, sending a DROP request...")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        answer = msg.exec_()

        server_addr = self.interIpAddressLineEdit.text()
        server_port = self.interPortSpinBox.value()
        server_password = self.interPasswordLineEdit.text()
        dropRequestThread = task.DropRequestThread(server_addr, server_port, server_password, ip)
        dropRequestThread.signals.on_start.connect(self.dropRequestThreadOnStart)
        dropRequestThread.signals.on_error.connect(self.dropRequestThreadOnError)
        dropRequestThread.signals.on_result.connect(self.dropRequestThreadOnResult)
        dropRequestThread.signals.on_finished.connect(self.dropRequestThreadOnFinished)
        self.threadPool.start(dropRequestThread)

    @QtCore.pyqtSlot(str)
    def dropRequestThreadOnStart(self, ip_to_drop):
        logging.info(f"Requesting the interlocutor server to drop {ip_to_drop}")
        self.addNotificationToNotificationsTable(f"Requesting the interlocutor server to drop {ip_to_drop}")

    @QtCore.pyqtSlot('PyQt_PyObject', str)
    def dropRequestThreadOnError(self, error, ip_to_drop):
        logging.error(f"Could not request the interlocutor server to drop {ip_to_drop}, error: {e}")
        self.addNotificationToNotificationsTable(
            f"Could not request the interlocutor server to drop {ip_to_drop}, error: {e}")

    @QtCore.pyqtSlot(dict)
    def dropRequestThreadOnResult(self, reply: dict):
        result = reply.get('result')
        if result:
            msg = f"Interlocutor server says: '{result}'"
            logging.info(msg)
            self.addNotificationToNotificationsTable(msg)
        else:
            error = reply.get('error')
            nameerror = reply.get('name')
            if error and nameerror:
                msg = f"Interlocutor server says: '{nameerror}'[Err code {error}]"
                logging.info(msg)
                self.addNotificationToNotificationsTable(msg)

    @QtCore.pyqtSlot()
    def dropRequestThreadOnFinished(self):
        pass

    @QtCore.pyqtSlot()
    def interGetContactInfoThreadOnFinished(self):
        pass

    @QtCore.pyqtSlot()
    def getRequestOnFinished(self):
        self.interSearchLineEdit.setEnabled(True)
        self.interSearchCriteriaComboBox.setEnabled(True)
        self.interSearchPushButton.setEnabled(True)

    def setupInterlocutorTable(self):
        headers = ['Name', 'IPv4 address', 'Port', 'Actions']
        self.interDbTableWidget.setColumnCount(len(headers))
        self.interDbTableWidget.setHorizontalHeaderLabels(headers)
        header = self.interDbTableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
