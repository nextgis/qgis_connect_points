# -*- coding: utf-8 -*-
#******************************************************************************
#
# qgis_plugin_base
# ---------------------------------------------------------
# Base Class for qgis plugins
#
# Author:   Alexander Lisovenko, alexander.lisovenko@nextgis.ru
# *****************************************************************************
# Copyright (c) 2015-2016. NextGIS, info@nextgis.com
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#*****************************************************************************

from PyQt4 import QtGui
from qgis.core import (
    QgsMessageLog,
)

from qgis.gui import (
    QgsMessageBar,
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if Singleton not in cls._instances:
            cls._instances[Singleton] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[Singleton]


class Plugin():
    __metaclass__ = Singleton

    def __init__(self, iface, pluginName):
        self._iface = iface
        self._name = pluginName

        self.__actions = []

    def plPrint(self, msg, level=QgsMessageLog.INFO):
        QgsMessageLog.logMessage(
            msg,
            self._name,
            level
        )

    def showMessageForUser(self, msg, level=QgsMessageBar.INFO, timeout=2):
        self._iface.messageBar().pushMessage(
            self._name,
            msg,
            level,
            timeout
        )

    def addAction(self, name, iconSrc, addToToolBar=True, addToMenu=True):
        action = QtGui.QAction(name, self._iface.mainWindow())
        action.setIcon(QtGui.QIcon(iconSrc))

        self.__actions.append(action)
        index = len(self.__actions) - 1

        if addToMenu:
            self._iface.addPluginToMenu(self._name, self.__actions[index])

        if addToToolBar:
            self._iface.addToolBarIcon(self.__actions[index])

        return self.__actions[index]

    def delAllActions(self):
        for action in self.__actions:
            self._iface.removeToolBarIcon(action)
            self._iface.removePluginMenu(self._name, action)

    def getPluginName(self):
        return self._name
