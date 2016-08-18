# -*- coding: utf-8 -*-
#******************************************************************************
#
# Connect Points
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

import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from qgis.core import (
    QgsMapLayerRegistry,
    QgsApplication,
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsField
)

from qgis.gui import (
    QgsBusyIndicatorDialog,
    QgsMessageBar
)

from qgis_plugin import QgisPlugin
from dialog import Dialog
from worker import Worker


class ConnectPoints(QgisPlugin):
    def __init__(self, iface):
        QgisPlugin.__init__(self, iface)

        self.pointLayerName = ""
        self.polygonLayerName = ""
        self.fieldName = ""

    def tr(self, msg):
        return QtCore.QCoreApplication.translate(self.__class__.__name__, msg)

    def initGui(self):
        self.toolButton = QtGui.QToolButton()
        self.toolButton.setMenu(QtGui.QMenu())
        self.toolButton.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.toolBar = self._iface.addToolBarWidget(self.toolButton)

        actionRun = self.addAction(
            self.tr("Recalculate"),
            QtGui.QIcon(self.pluginDir + "/icons/connect_points.svg"),
            False,
            True,
        )
        actionRun.triggered.connect(self.run)

        actionSettings = self.addAction(
            self.tr("Settings"),
            QtGui.QIcon(self.pluginDir + "/icons/settings.svg"),
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
            settings.value("connect_points_plugin/result_layer_name", ""),
            self._iface.mainWindow()
        )
        res = dlg.exec_()
        if res == Dialog.Accepted:
            # QgisPlugin().plPrint("Save settings")
            plugin_settings = dlg.getSettings()
            settings.setValue("connect_points_plugin/point_layer_from", plugin_settings[0])
            settings.setValue("connect_points_plugin/polygin_layer_to", plugin_settings[1])
            settings.setValue("connect_points_plugin/filed_name_id_from", plugin_settings[2])
            settings.setValue("connect_points_plugin/filed_name_link", plugin_settings[3])
            settings.setValue("connect_points_plugin/filed_name_id_to", plugin_settings[4])
            settings.setValue("connect_points_plugin/result_layer_name", plugin_settings[5])

        dlg.deleteLater()
        del dlg

    def run(self):
        settings = QtCore.QSettings()

        self.plFromName = settings.value("connect_points_plugin/point_layer_from", "")
        self.plToName = settings.value("connect_points_plugin/polygin_layer_to", "")
        self.fIdFromName = settings.value("connect_points_plugin/filed_name_id_from", "")
        self.fLinkName = settings.value("connect_points_plugin/filed_name_link", "")
        self.fIdToName = settings.value("connect_points_plugin/filed_name_id_to", "")
        self.resLayerName = settings.value("connect_points_plugin/result_layer_name", "")

        # QgisPlugin().plPrint("self.pointLayerName: %s" % self.pointLayerName)
        # QgisPlugin().plPrint("self.polygonLayerName: %s" % self.polygonLayerName)
        # QgisPlugin().plPrint("self.fieldName: %s" % self.fieldName)

        if any([v == "" for v in [self.plFromName, self.plToName, self.fIdFromName, self.fLinkName, self.fIdToName]]):
            QgisPlugin().showMessageForUser(
                self.tr(u"Plugin settings are incorrect. Please, check settings!"),
                QgsMessageBar.CRITICAL,
                0
            )
            return

        plFrom_list = QgsMapLayerRegistry.instance().mapLayersByName(self.plFromName)
        if len(plFrom_list) == 0:
            QgisPlugin().showMessageForUser(
                self.tr(u"Layer with name '%s' not found!") % self.plFromName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        plFrom = plFrom_list[0]

        plTo_list = QgsMapLayerRegistry.instance().mapLayersByName(self.plToName)
        if len(plTo_list) == 0:
            QgisPlugin().showMessageForUser(
                self.tr(u"Layer with name '%s' not found!") % self.plToName,
                QgsMessageBar.CRITICAL,
                0
            )
            return
        plTo = plTo_list[0]

        layers = QgsMapLayerRegistry.instance().mapLayersByName(self.resLayerName)
        if len(layers) == 0:
            if self.resLayerName == "":
                self.resLayerName = "connect_points_result"
            else:
                QgisPlugin().showMessageForUser(
                    self.tr(u"Layer with name '%s' not found!") % self.resLayerName + " " + self.tr("New layer is created!"),
                    QgsMessageBar.WARNING,
                    0
                )
            self.resLayer = QgsVectorLayer(u"LineString?crs=EPSG:4326", self.resLayerName, u"memory")
        else:
            if layers[0].providerType() == u"ogr":
                self.resLayer = QgsVectorLayer(layers[0].source(), self.resLayerName, u"ogr")
                QgsMapLayerRegistry.instance().removeMapLayers([layers[0].id()])
            elif layers[0].providerType() == u"memory":
                self.resLayer = layers[0]

        result = self.addFields(self.resLayer)
        if result is False:
            QgisPlugin().showMessageForUser(
                self.tr(u"Layer with name '%s' can not be used for result output!") % self.resLayerName,
                QgsMessageBar.WARNING,
                0
            )
            return

        self.applyResultStyle(self.resLayer)

        progressDlg = QgsBusyIndicatorDialog(self.tr(u"Prepare"))
        progressDlg.setWindowTitle(self.tr(u"Calculation"))
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
        worker.progressChanged.connect(
            lambda x, y: progressDlg.setMessage(
                self.tr(u"Process %d points from %d") % (x, y)
            )
        )
        thread.start()

        self.thread = thread
        self.worker = worker

        progressDlg.exec_()

    def addFields(self, qgsMapLayer):
        self.lineFields = [
            QgsField(u"PNT1N", QtCore.QVariant.String),
            QgsField(u"PNT2N", QtCore.QVariant.String),
            QgsField(u"ID1", QtCore.QVariant.Int),
            QgsField(u"ID2", QtCore.QVariant.Int),
        ]
        self.resLayer.startEditing()

        # provider = qgsMapLayer.dataProvider()

        for need_field in self.lineFields:
            # for field in qgsMapLayer.fields():
            #     if field.name() == need_field.name():
            #         if field.type() == need_field.type():
            #             continue
            #         else:
            #             QgisPlugin().plPrint("field.type(): %d" % field.type())
            #             QgisPlugin().plPrint("need_field.type(): %d" % need_field.type())
            #             qgsMapLayer.commitChanges()
            #             return False

            qgsMapLayer.addAttribute(need_field)

        qgsMapLayer.commitChanges()
        return True

    def applyResultStyle(self, qgsMapLayer):
        qgsMapLayer.loadNamedStyle(
            os.path.join(self.pluginDir, "style.qml")
        )

        fi = QtCore.QFileInfo(qgsMapLayer.source())

        if not fi.isFile():
            return

        qgsMapLayer.saveNamedStyle(
            os.path.join(
                fi.absolutePath(),
                fi.baseName() + ".qml"
            )
        )

    def addLayerToProject(self):
        QgsMapLayerRegistry.instance().addMapLayer(self.resLayer)

    def showError(self, msg):
        QgisPlugin().showMessageForUser(msg, QgsMessageBar.CRITICAL, 0)
