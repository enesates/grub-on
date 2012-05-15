#!/usr/bin/env python
#-*- coding:utf-8 -*-

import parser

from PyQt4 import QtGui
from PyQt4 import uic

import subprocess
import re
import sys
import os


DefaultGrubConfig=parser.DefaultGrubConfig()
DefaultGrubConfig.path="/etc/default/grub"
DefaultGrubConfig.read()

GrubCfgConfig=parser.GrubCfgConfig()
GrubCfgConfig.path="/boot/grub/grub.cfg"
GrubCfgConfig.read()

programPath = "/usr/share/grub-on"
BACKUP_PATH = programPath+"/backup/"
#BACKUP_PATH="/home/user/" # uncomment this for using another backup path

GRUB_UPDATE_COMMAND="update-grub"

class Gui(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        #self.programPath=os.path.abspath(os.path.dirname(sys.argv[0]))

        uic.loadUi(programPath+"/grubon.ui", self)

        self.upButton.setIcon(QtGui.QIcon.fromTheme("go-up",QtGui.QIcon(programPath+"/icons/go-up.png")))
        self.downButton.setIcon(QtGui.QIcon.fromTheme("go-down",QtGui.QIcon(programPath+"/icons/go-down.png")))
        self.removeButton.setIcon(QtGui.QIcon.fromTheme("list-remove",QtGui.QIcon(programPath+"/icons/list-remove.png")))
        self.addButton.setIcon(QtGui.QIcon.fromTheme("list-add",QtGui.QIcon(programPath+"/icons/list-add.png")))
        self.setDefaultButton.setIcon(QtGui.QIcon.fromTheme("go-home",QtGui.QIcon(programPath+"/icons/go-home.png")))

        self.osListWidget.currentRowChanged.connect(self.showEntry)

        self.osOptionsEdit.textChanged.connect(self.osOptionsChanged)

        self.upButton.clicked.connect(self.upButtonClicked)
        self.downButton.clicked.connect(self.downButtonClicked)

        self.setDefaultButton.clicked.connect(self.setDefault)

        self.timeoutBox.valueChanged.connect(self.setTimeout)

        self.removeButton.clicked.connect(self.removeClicked)

        self.saveButton.clicked.connect(self.save)
        self.resetButton.clicked.connect(self.reset)
        self.backupButton.clicked.connect(self.backup)
        self.restoreButton.clicked.connect(self.restore)

        self.addButton.clicked.connect(self.add)

        self.refresh()
        self.showEntry(0)

    def reset(self):
        DefaultGrubConfig.read()
        GrubCfgConfig.read()
        self.refresh()

    def save(self):
        DefaultGrubConfig.write()
        subprocess.call(["xterm", "-e", GRUB_UPDATE_COMMAND])
        GrubCfgConfig.write()
        self.refresh()

    def backup(self):
        subprocess.call(["xterm", "-e", "cp {0} {1}".format(DefaultGrubConfig.path, BACKUP_PATH)])
        subprocess.call(["xterm", "-e", "cp {0} {1}".format(GrubCfgConfig.path, BACKUP_PATH)])

    def restore(self):
        subprocess.call(["xterm", "-e", "cp {0}/grub {1}".format(BACKUP_PATH, DefaultGrubConfig.path)])
        subprocess.call(["xterm", "-e", "cp {0}/grub.cfg {1}".format(BACKUP_PATH, GrubCfgConfig.path)])
        DefaultGrubConfig.read()
        GrubCfgConfig.read()
        self.refresh()

    def refresh(self):
        self.timeoutBox.setValue(int(DefaultGrubConfig.settings["GRUB_TIMEOUT"]))

        try:
            selected=self.osListWidget.row(self.osListWidget.selectedItems()[0])
        except IndexError:
            selected=0

        self.osListWidget.clear()
        for i in GrubCfgConfig.entries:
            self.osListWidget.addItem(i["name"])

        default=int(DefaultGrubConfig.settings["GRUB_DEFAULT"])
        self.osListWidget.item(default).setIcon(QtGui.QIcon.fromTheme("go-home",QtGui.QIcon(programPath+"/icons/go-home.png")))

        self.osListWidget.setCurrentRow(selected)

    def add(self):
        GrubCfgConfig.entries.append({"name":"New Startup Entry", "content": "menuentry 'New Startup Entry' {\n set root=(hd0,4) \n }"})
        self.refresh()

    def removeClicked(self):
        try:
            selected=self.osListWidget.row(self.osListWidget.selectedItems()[0])
            default = int(DefaultGrubConfig.settings["GRUB_DEFAULT"])
            if selected < default:
                DefaultGrubConfig.settings["GRUB_DEFAULT"] = default - 1
            if selected == default :
                DefaultGrubConfig.settings["GRUB_DEFAULT"] = 0
        except IndexError:
            return
        del GrubCfgConfig.entries[selected]
        self.refresh()

    def showEntry(self, row):
        if row==0:
            self.upButton.setDisabled(True)
            self.downButton.setDisabled(False)
        elif row==len(GrubCfgConfig.entries)-1:
            self.downButton.setDisabled(True)
            self.upButton.setDisabled(False)
        else:
            self.upButton.setEnabled(True)
            self.downButton.setEnabled(True)

        self.osOptionsEdit.blockSignals(True)
        self.osOptionsEdit.setPlainText(GrubCfgConfig.entries[row]["content"])
        self.osOptionsEdit.blockSignals(False)

    def upButtonClicked(self):
        try:
            selected=self.osListWidget.selectedItems()[0]
        except IndexError:
            return
        index=self.osListWidget.row(selected)
        entry=GrubCfgConfig.entries[index]
        del GrubCfgConfig.entries[index]

        GrubCfgConfig.entries.insert(index-1, entry)
	

        self.refresh()
        self.osListWidget.setItemSelected(self.osListWidget.item(index-1), True)
        self.showEntry(index-1)
        if index-1==int(DefaultGrubConfig.settings["GRUB_DEFAULT"]):
	    DefaultGrubConfig.settings["GRUB_DEFAULT"]= index
	self.refresh()
            

    def downButtonClicked(self):
        try:
            selected=self.osListWidget.selectedItems()[0]
        except IndexError:
            return
        index=self.osListWidget.row(selected)
        entry=GrubCfgConfig.entries[index]
        del GrubCfgConfig.entries[index]

        GrubCfgConfig.entries.insert(index+1, entry)

        self.refresh()
        self.osListWidget.setItemSelected(self.osListWidget.item(index+1), True)
        self.showEntry(index+1)
        if index+1==int(DefaultGrubConfig.settings["GRUB_DEFAULT"]):
	    DefaultGrubConfig.settings["GRUB_DEFAULT"]= index
	self.refresh()
	
    def osOptionsChanged(self):
        selected=self.osListWidget.row(self.osListWidget.selectedItems()[0])
        GrubCfgConfig.entries[selected]["content"]=self.osOptionsEdit.toPlainText()
        try:
            newName=re.findall("menuentry ['\"](.*?)['\"]", self.osOptionsEdit.toPlainText())[0]
            GrubCfgConfig.entries[selected]["name"]=newName
            self.osListWidget.item(selected).setText(newName)
        except IndexError:
            pass

    def setDefault(self, row):
        selected = self.osListWidget.selectedItems()[0]
        DefaultGrubConfig.settings["GRUB_DEFAULT"]= self.osListWidget.row(selected)
        self.refresh()

    def setTimeout(self, timeout):
        DefaultGrubConfig.settings["GRUB_TIMEOUT"]= timeout
        self.refresh()

if not os.getuid()==0:
    subprocess.Popen(["gksudo", os.path.abspath(sys.argv[0])])
    sys.exit(0)

app=QtGui.QApplication(sys.argv)
g=Gui()
g.show()
app.exec_()
