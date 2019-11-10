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
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.newChatPushButton = QtWidgets.QPushButton(self.conversationsGroupBox)
        self.newChatPushButton.setObjectName("newChatPushButton")
        self.horizontalLayout_12.addWidget(self.newChatPushButton)
        self.verticalLayout_21.addLayout(self.horizontalLayout_12)
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
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_14.addItem(spacerItem1)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.chatMateFilesPushButton = QtWidgets.QPushButton(self.chatGroupBox)
        self.chatMateFilesPushButton.setObjectName("chatMateFilesPushButton")
        self.horizontalLayout_13.addWidget(self.chatMateFilesPushButton)
        self.chatMateAddToContactsPushButton = QtWidgets.QPushButton(self.chatGroupBox)
        self.chatMateAddToContactsPushButton.setObjectName("chatMateAddToContactsPushButton")
        self.horizontalLayout_13.addWidget(self.chatMateAddToContactsPushButton)
        self.horizontalLayout_14.addLayout(self.horizontalLayout_13)
        self.verticalLayout_24.addLayout(self.horizontalLayout_14)
        self.textEdit = QtWidgets.QTextEdit(self.chatGroupBox)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_24.addWidget(self.textEdit)
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
        spacerItem2 = QtWidgets.QSpacerItem(13, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem2)
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
        spacerItem3 = QtWidgets.QSpacerItem(248, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_19.addItem(spacerItem3)
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
        spacerItem4 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
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
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_22.addItem(spacerItem5)
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
        spacerItem6 = QtWidgets.QSpacerItem(160, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem6)
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
        self.tabWidget_2 = QtWidgets.QTabWidget(self.groupBox_4)
        self.tabWidget_2.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget_2.setTabsClosable(True)
        self.tabWidget_2.setMovable(True)
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.tabWidget_2.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_2.addTab(self.tab_2, "")
        self.verticalLayout_11.addWidget(self.tabWidget_2)
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
        self.tabWidget_2.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(HotlineMainWindow)
        HotlineMainWindow.setTabOrder(self.newContactInboxPortSpinBox, self.newContactFtpPortSpinBox)
        HotlineMainWindow.setTabOrder(self.newContactFtpPortSpinBox, self.addNewContactPushButton)
        HotlineMainWindow.setTabOrder(self.addNewContactPushButton, self.ftpIpAddressLineEdit)
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

    def retranslateUi(self, HotlineMainWindow):
        _translate = QtCore.QCoreApplication.translate
        HotlineMainWindow.setWindowTitle(_translate("HotlineMainWindow", "Hotline"))
        self.conversationsGroupBox.setTitle(_translate("HotlineMainWindow", "Conversations"))
        self.newChatPushButton.setText(_translate("HotlineMainWindow", "New chat"))
        self.chatGroupBox.setTitle(_translate("HotlineMainWindow", "A_Username"))
        self.chatMateFilesPushButton.setText(_translate("HotlineMainWindow", "Files"))
        self.chatMateAddToContactsPushButton.setText(_translate("HotlineMainWindow", "Add to contacts"))
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
        self.groupBox_7.setTitle(_translate("HotlineMainWindow", "Banner"))
        self.ftpBannerPlainTextEdit.setPlaceholderText(
            _translate("HotlineMainWindow", "Type here a creative banner message :)"))
        self.groupBox_8.setTitle(_translate("HotlineMainWindow", "Options"))
        self.ftpStartPushButton.setText(_translate("HotlineMainWindow", "Start"))
        self.ftpShutdownPushButton.setText(_translate("HotlineMainWindow", "Shutdown"))
        self.groupBox_9.setTitle(_translate("HotlineMainWindow", "Connected users"))
        self.groupBox_10.setTitle(_translate("HotlineMainWindow", "Files"))
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
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_1),
                                    _translate("HotlineMainWindow", "192.168.1.70"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_2), _translate("HotlineMainWindow", "Tab 2"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDownloads),
                                  _translate("HotlineMainWindow", "Downloads"))
        self.groupBox_5.setTitle(_translate("HotlineMainWindow", "My notifications"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNotifications),
                                  _translate("HotlineMainWindow", "Notifications"))


class HotlineMainWindow(QtWidgets.QMainWindow, Ui_HotlineMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Some globals
        self.searchCriteria = 'Name'
        self.findContactSearchPattern = ''
        self.lastMatchingRow = None

        # When user changes between tabs, keep the information ordered
        self.tabWidget.currentChanged.connect(self.onTabChange)

        # FTP tab
        self.ftpIpAddressLineEdit.setReadOnly(True)
        self.ftpShutdownPushButton.setEnabled(False)
        self.ftpStartPushButton.clicked.connect(self.ftpStartPushButtonAction)

        # Interlocutor client tab
        self.myContactInfoIpAddressLineEdit.setReadOnly(True)
        self.myContactInfoMacAddressLineEdit.setReadOnly(True)

        # Functionality to buttons
        self.addNewContactPushButton.clicked.connect(self.addNewContactPushButtonAction)
        self.findContactPushButton.clicked.connect(self.findContactInTable)

        self.loadFtpConfiguration()
        self.loadInterlocutorConfiguration()
        self.setupContactsTable()
        self.loadContactsTable()
        self.contactsTableWidget.cellChanged.connect(self.update_contact_from_table_cell)

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
            else:
                logging.info(f"New value '{new_value}' for field 'name' for user '{mac_address}'")
            finally:
                conn.close()
        elif cell == 2:
            conn = dbfunctions.get_connection()
            try:
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
            else:
                logging.info(f"New value '{new_value}' for field 'ipv4_address' for user '{mac_address}'")
            finally:
                conn.close()
        elif cell == 3:
            conn = dbfunctions.get_connection()
            try:
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
            row_to_scroll = self.nextMatchingRow(self.searchCriteria, self.findContactSearchPattern, self.lastMatchingRow)
            if row_to_scroll == None:
                print(f"None of the values of the '{self.searchCriteria}' matches with '{self.findContactSearchPattern}'")
                return

        print('scrolling to row:', row_to_scroll)
        self.lastMatchingRow = row_to_scroll + 1
        print('last matching row:', self.lastMatchingRow)

    def loadFtpConfiguration(self):
        conn = dbfunctions.get_connection()
        ipv4, ipv6, max_conn, max_conn_per_ip, folder, banner, port = dbfunctions.get_configuration(
            conn, 'ipv4_address', 'ipv6_address', 'ftp_max_connections', 'ftp_max_connections_per_ip', 'ftp_folder',
            'ftp_banner', 'ftp_port')
        conn.close()
        ip = ipv4 if ipv4 else (ipv6 if ipv6 else 'Could not obtain your IP address')
        max_conn = max_conn if max_conn else 10
        max_conn_per_ip = max_conn_per_ip if max_conn_per_ip else 1
        folder = folder if folder else ''
        banner = banner if banner is not None else ''
        port = port if port is not None else 21
        self.ftpIpAddressLineEdit.setText(ip)
        self.ftpMaxConnectionsSpinBox.setValue(max_conn)
        self.ftpMaxConnectionsPerIPSpinBox.setValue(max_conn_per_ip)
        self.ftpFolderLineEdit.setText(folder)
        self.ftpBannerPlainTextEdit.setPlainText(banner)
        self.ftpPortSpinBox.setValue(port)

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
        self.myContactInfoGetOnlyByMacCheckBox.setCheckState(get_only_by_mac)

    def setupContactsTable(self):
        contactsTableHeaders = ['Name', 'MAC address', 'IPv4 address', 'IPv6 address',
                                'Inbox port', 'FTP port', 'CHAT', 'FILES', 'DELETE']
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
            self.contactsTableWidget.setCellWidget(row, 6, chat_btn)
            files_btn = QtWidgets.QPushButton(self.contactsTableWidget)
            files_btn.setText('Files')
            self.contactsTableWidget.setCellWidget(row, 7, files_btn)
            delete_btn = QtWidgets.QPushButton(self.contactsTableWidget)
            delete_btn.setText('Delete')
            delete_btn.clicked.connect(self.delete_contact_row)
            self.contactsTableWidget.setCellWidget(row, 8, delete_btn)

        self.contactsTableWidget.cellChanged.connect(self.update_contact_from_table_cell)

    def addContactToContactsTable(self, name, mac_address, ipv4_address, ipv6_address, inbox_port, ftp_port):
        for row in range(self.contactsTableWidget.rowCount()):
            row_name = self.contactsTableWidget.item(row, 0).text()
            if name < row_name:
                break
        else:
            row += 1

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
        self.contactsTableWidget.setCellWidget(row, 6, chat_btn)
        files_btn = QtWidgets.QPushButton(self.contactsTableWidget)
        files_btn.setText('Files')
        self.contactsTableWidget.setCellWidget(row, 7, files_btn)
        delete_btn = QtWidgets.QPushButton(self.contactsTableWidget)
        delete_btn.setText('Delete')
        delete_btn.clicked.connect(self.delete_contact_row)
        self.contactsTableWidget.setCellWidget(row, 8, delete_btn)
        self.contactsTableWidget.cellChanged.connect(self.update_contact_from_table_cell)

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
        folder = self.ftpFolderLineEdit.text().strip()
        if not os.path.isdir(folder):
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a folder to share')
            logging.info(f"Folder selected: '{folder}'")
            self.ftpFolderLineEdit.setText(folder)

        logging.info('Starting FTP server...')

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
