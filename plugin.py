# -*- coding: utf-8 -*-
#******************************************************************************
#
# ConnectPoints
# ---------------------------------------------------------
# This plugin convert lesis GIS working dir structure to sqlite data base
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
#******************************************************************************

from PyQt4 import QtCore
from PyQt4 import QtGui

from qgis.core import (
    QgsMapLayerRegistry,
    QgsApplication,
    QgsVectorLayer,
    QgsMapLayerRegistry
)

from qgis.gui import (
    QgsBusyIndicatorDialog,
    QgsMessageBar
)

from qgis_plugin_base import Plugin
from dialog import Dialog
from worker import Worker


class ConnectPoints(Plugin):
    def __init__(self, iface):
        Plugin.__init__(self, iface, "ConnectPoints")

        userPluginPath = QtCore.QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + '/python/plugins/connect_points'
        systemPluginPath = QgsApplication.prefixPath() + '/python/plugins/connect_points'

        overrideLocale = QtCore.QSettings().value('locale/overrideFlag', False, type=bool)
        if not overrideLocale:
            localeFullName = QtCore.QLocale.system().name()[:2]
        else:
            localeFullName = QtCore.QSettings().value("locale/userLocale", "")

        if QtCore.QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + '/i18n/connect_points_' + localeFullName + '.qm'
            self.pluginPath = userPluginPath
        else:
            translationPath = systemPluginPath + '/i18n/connect_points_' + localeFullName + '.qm'
            self.pluginPath = systemPluginPath

        self.localePath = translationPath
        if QtCore.QFileInfo(self.localePath).exists():
            self.translator = QtCore.QTranslator()
            self.translator.load(self.localePath)
            QgsApplication.installTranslator(self.translator)

        self.pointLayerName = ""
        self.polygonLayerName = ""
        self.fieldName = ""

    def initGui(self):
        self.toolButton = QtGui.QToolButton()
        self.toolButton.setMenu(QtGui.QMenu())
        self.toolButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.toolBar = self._iface.addToolBarWidget(self.toolButton)

        actionRun = self.addAction(
            u"Перерасчитать",
            QtGui.QIcon(self.pluginPath + "/icons/connect_points.svg"),
            False,
            True,
        )
        actionRun.triggered.connect(self.run)

        actionSettings = self.addAction(
            u"Настройки",
            QtGui.QIcon(self.pluginPath + "/icons/settings.svg"),
            False,
            True,
        )
        actionSettings.triggered.connect(self.showSettings)

        m = self.toolButton.menu()
        m.addAction(actionRun)
        m.addAction(actionSettings)
        self.toolButton.setDefaultAction(actionRun)

    def unload(self):
        self.delAllActions()
        self._iface.removeToolBarIcon(self.toolBar)

    def showSettings(self):
        settings = QtCore.QSettings()

        dlg = Dialog(
            settings.value("connect_points_plugin/point_layer_from", ""),
            settings.value("connect_points_plugin/polygin_layer_to", ""),
            settings.value("connect_points_plugin/filed_name_id_from", ""),
            settings.value("connect_points_plugin/filed_name_link", ""),
            settings.value("connect_points_plugin/filed_name_id_to", ""),
            # settings.value("connect_points_plugin/result_filename", ""),
            self._iface.mainWindow()
        )
        res = dlg.exec_()
        if res == Dialog.Accepted:
            # Plugin().plPrint("Save settings")
            plugin_settings = dlg.getSettings()
            settings.setValue("connect_points_plugin/point_layer_from", plugin_settings[0])
            settings.setValue("connect_points_plugin/polygin_layer_to", plugin_settings[1])
            settings.setValue("connect_points_plugin/filed_name_id_from", plugin_settings[2])
            settings.setValue("connect_points_plugin/filed_name_link", plugin_settings[3])
            settings.setValue("connect_points_plugin/filed_name_id_to", plugin_settings[4])
            # settings.setValue("connect_points_plugin/result_filename", plugin_settings[5])

    def run(self):
        settings = QtCore.QSettings()

        self.plFromName = settings.value("connect_points_plugin/point_layer_from", "")
        self.plToName = settings.value("connect_points_plugin/polygin_layer_to", "")
        self.fIdFromName = settings.value("connect_points_plugin/filed_name_id_from", "")
        self.fLinkName = settings.value("connect_points_plugin/filed_name_link", "")
        self.fIdToName = settings.value("connect_points_plugin/filed_name_id_to", "")

        # Plugin().plPrint("self.pointLayerName: %s" % self.pointLayerName)
        # Plugin().plPrint("self.polygonLayerName: %s" % self.polygonLayerName)
        # Plugin().plPrint("self.fieldName: %s" % self.fieldName)

        if any([v == "" for v in [self.plFromName, self.plToName, self.fIdFromName, self.fLinkName, self.fIdToName]]):
            Plugin().showMessageForUser(
                u"Плагин настроен не корректно. Проверте настройки!",
                QgsMessageBar.CRITICAL,
                0
            )
            return

        plFrom_list = QgsMapLayerRegistry.instance().mapLayersByName(self.plFromName)
        if len(plFrom_list) == 0:
            Plugin().showMessageForUser(
                u"Слой с именем '%s' не найден!" % self.plFromName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        plFrom = plFrom_list[0]

        plTo_list = QgsMapLayerRegistry.instance().mapLayersByName(self.plToName)
        if len(plTo_list) == 0:
            Plugin().showMessageForUser(
                u"Слой с именем '%s' не найден!" % self.plToName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        plTo = plTo_list[0]

        self.resLayer = QgsVectorLayer(u"LineString?crs=EPSG:4326", "result_lines", "memory")

        progressDlg = QgsBusyIndicatorDialog(u"Подготовка")
        progressDlg.setWindowTitle(u"Идёт расчет")
        worker = Worker(plFrom, plTo, self.fIdFromName, self.fLinkName, self.fIdToName, self.resLayer)
        thread = QtCore.QThread(self._iface.mainWindow())

        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.stoped.connect(self.addLayerToProject)
        worker.stoped.connect(thread.quit)
        worker.stoped.connect(worker.deleteLater)
        worker.stoped.connect(thread.deleteLater)
        worker.stoped.connect(progressDlg.close)
        worker.error.connect(self.showError)
        worker.error.connect(progressDlg.close)
        worker.progressChanged.connect(lambda x, y: progressDlg.setMessage(u"Обработано %d точек из %d" % (x, y)))
        thread.start()

        self.thread = thread
        self.worker = worker

        progressDlg.exec_()

    def addLayerToProject(self):
        QgsMapLayerRegistry.instance().addMapLayer(self.resLayer)

    def showError(self, msg):
        Plugin().showMessageForUser(msg, QgsMessageBar.CRITICAL, 0)
