# -*- coding: utf-8 -*-
#******************************************************************************
#
# qgis_plugin
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
import os

from PyQt4 import QtGui
from PyQt4 import QtCore

from qgis.core import (
    QgsMessageLog,
)
from qgis.gui import (
    QgsMessageBar,
)

from qgis_plugin_base import QgisPluginBase


class QgisPlugin(QgisPluginBase):
    def __init__(self, iface):
        QgisPluginBase.__init__(self)

        self._iface = iface

        self.__actions = []

        # initialize locale
        locale = QtCore.QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.i18nPath,
            '%s_%s.qm' % (self.normalizePluginName(), locale)
        )

        if os.path.exists(locale_path):
            self.translator = QtCore.QTranslator()
            self.translator.load(locale_path)

            QtCore.QCoreApplication.installTranslator(self.translator)
        # else:
        #     self.plPrint(
        #         QtCore.QCoreApplication.translate(
        #             "QgisPlugin",
        #             "Translation file %s not found!" % locale_path
        #         ),
        #         QgsMessageLog.WARNING
        #     )

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
