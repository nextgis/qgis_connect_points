# -*- coding: utf-8 -*-
# ******************************************************************************
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
# ******************************************************************************


from qgis.PyQt import QtWidgets

from qgis.core import (
    QgsProject,
    QgsMapLayerProxyModel,
    QgsFieldProxyModel,
    Qgis,
    QgsVectorLayer,
)

from qgis.gui import (
    QgsMapLayerComboBox,
    QgsFieldComboBox,
)

from .qgis_plugin import QgisPlugin


class Dialog(QtWidgets.QDialog):
    def __init__(
        self,
        curPointsLayerFrom,
        curPointsLayerTo,
        curFNIdFrom,
        curFNLink,
        curFNIdTo,
        curResultLayerName,
        iface,
        parent=None,
    ):
        QtWidgets.QDialog.__init__(self, parent)

        self._iface = iface

        self.resize(500, 200)

        self.setWindowTitle(QgisPlugin(self._iface).pluginName)
        self.__mainLayout = QtWidgets.QVBoxLayout(self)
        self.__layout = QtWidgets.QGridLayout(self)

        l1 = QtWidgets.QLabel(self.tr("Point layer 'FROM'") + ":")
        l1.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        self.__layout.addWidget(l1, 0, 0)
        self.pointsLayerFrom = QgsMapLayerComboBox()
        self.pointsLayerFrom.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.pointsLayerFrom.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.pointsLayerFrom.setEditable(True)
        # self.pointsLayerFrom.setEditText(curPointsLayerFrom)
        self.pointsLayerFrom.layerChanged.connect(self.choozeLayerFrom)
        self.__layout.addWidget(self.pointsLayerFrom, 0, 1)

        l2 = QtWidgets.QLabel(self.tr("Point layer 'TO'") + ":")
        l2.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        self.__layout.addWidget(l2, 1, 0)
        self.pointsLayerTo = QgsMapLayerComboBox()
        self.pointsLayerTo.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.pointsLayerTo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.pointsLayerTo.setEditable(True)
        # self.pointsLayerTo.setEditText(curPointsLayerTo)
        self.pointsLayerTo.layerChanged.connect(self.choozeLayerTo)
        self.__layout.addWidget(self.pointsLayerTo, 1, 1)

        self.__layout.addWidget(
            QtWidgets.QLabel(self.tr("Point 'FROM' id field") + ":"), 2, 0
        )
        self.fnIdFrom = QgsFieldComboBox()
        self.fnIdFrom.setFilters(
            QgsFieldProxyModel.Int | QgsFieldProxyModel.LongLong
        )
        self.fnIdFrom.setEditable(True)
        # self.fnIdFrom.setEditText(curFNIdFrom)
        self.fnIdFrom.fieldChanged.connect(self.filedChooze)
        self.__layout.addWidget(self.fnIdFrom, 2, 1)

        self.__layout.addWidget(
            QtWidgets.QLabel(self.tr("Link field") + ":"), 3, 0
        )
        self.fnLink = QgsFieldComboBox()
        self.fnLink.setFilters(
            QgsFieldProxyModel.Int | QgsFieldProxyModel.LongLong
        )
        self.fnLink.setEditable(True)
        # self.fnLink.setEditText(curFNLink)
        self.fnLink.fieldChanged.connect(self.filedChooze)
        self.__layout.addWidget(self.fnLink, 3, 1)

        self.__layout.addWidget(
            QtWidgets.QLabel(self.tr("Point 'TO' id field") + ":"), 4, 0
        )
        self.fnIdTo = QgsFieldComboBox()
        self.fnIdTo.setFilters(
            QgsFieldProxyModel.Int | QgsFieldProxyModel.LongLong
        )
        self.fnIdTo.setEditable(True)
        # self.fnIdTo.setEditText(curFNIdTo)
        self.fnIdTo.fieldChanged.connect(self.filedChooze)
        self.__layout.addWidget(self.fnIdTo, 4, 1)

        self.__layout.addWidget(
            QtWidgets.QLabel(self.tr("Save result in layer") + ":"), 5, 0
        )
        self.linesLayer = QgsMapLayerComboBox()
        self.linesLayer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.linesLayer.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.linesLayer.setEditable(True)
        self.linesLayer.layerChanged.connect(self.choozeResultLayer)
        self.__layout.addWidget(self.linesLayer, 5, 1)

        # self.__layout4resultFileChoose = QtGui.QHBoxLayout()
        # self.leResultFilename = QtWidgets.QLineEdit(curResultFilename)
        # self.__layout4resultFileChoose.addWidget(self.leResultFilename)
        # self.pbChooseResultFilename = QtGui.QPushButton(u"Выбрать")
        # self.pbChooseResultFilename.released.connect(self.chooseResultFilename)
        # self.__layout4resultFileChoose.addWidget(self.pbChooseResultFilename)
        # self.__layout.addLayout(self.__layout4resultFileChoose, 6, 0, 2, 0)

        self.pointsLayerFrom.layerChanged.connect(self.fnIdFrom.setLayer)
        self.pointsLayerFrom.layerChanged.connect(self.fnLink.setLayer)

        self.pointsLayerTo.layerChanged.connect(self.fnIdTo.setLayer)

        self.__mainLayout.addLayout(self.__layout)

        self.__bbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self.__bbox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.__bbox.accepted.connect(self.accept)
        self.__mainLayout.addWidget(self.__bbox)

        self.fillControls(
            curPointsLayerFrom,
            curPointsLayerTo,
            curFNIdFrom,
            curFNLink,
            curFNIdTo,
            curResultLayerName,
        )

    def fillControls(
        self,
        curPointsLayerFrom,
        curPointsLayerTo,
        curFNIdFrom,
        curFNLink,
        curFNIdTo,
        curResultLayerName,
    ):
        QgisPlugin(self._iface).plPrint(
            "curPointsLayerFrom: " + curPointsLayerFrom
        )
        QgisPlugin(self._iface).plPrint(
            "curPointsLayerTo: " + curPointsLayerTo
        )
        QgisPlugin(self._iface).plPrint("curFNIdFrom: " + curPointsLayerFrom)
        QgisPlugin(self._iface).plPrint("curFNLink: " + curFNIdFrom)
        QgisPlugin(self._iface).plPrint("curPointsLayerFrom: " + curFNLink)
        QgisPlugin(self._iface).plPrint("curFNIdTo: " + curFNIdTo)
        QgisPlugin(self._iface).plPrint(
            "curResultLayerName: " + curResultLayerName
        )

        layerFrom = self.getQGISLayer(curPointsLayerFrom)
        layerTo = self.getQGISLayer(curPointsLayerTo)
        layerResult = self.getQGISLayer(curResultLayerName, True)

        if layerFrom is None:
            self.pointsLayerFrom.setCurrentIndex(-1)
            self.pointsLayerFrom.setEditText(curPointsLayerFrom)
        else:
            self.pointsLayerFrom.setLayer(layerFrom)

        if layerTo is None:
            self.pointsLayerTo.setCurrentIndex(-1)
            self.pointsLayerTo.setEditText(curPointsLayerTo)
        else:
            self.pointsLayerTo.setLayer(layerTo)

        if layerResult is None:
            self.linesLayer.setCurrentIndex(-1)
            self.linesLayer.setEditText(curResultLayerName)
        else:
            self.linesLayer.setLayer(layerResult)

        # self.fnIdFrom.clear()
        # self.fnLink.clear()
        # self.fnIdTo.clear()

        # self.fnIdFrom.setField(curFNIdFrom)
        self.fnIdFrom.setCurrentIndex(-1)
        self.fnIdFrom.setEditText(curFNIdFrom)
        # self.fnLink.setField(curFNLink)
        self.fnLink.setCurrentIndex(-1)
        self.fnLink.setEditText(curFNLink)
        # self.fnIdTo.setField(curFNIdTo)
        self.fnIdTo.setCurrentIndex(-1)
        self.fnIdTo.setEditText(curFNIdTo)

    def getQGISLayer(self, layerName, silent=False):
        if layerName is None:
            return
        if layerName == "":
            return

        layers = QgsProject.instance().mapLayersByName(layerName)
        if len(layers) == 0:
            if silent is False:
                QgisPlugin(self._iface).showMessageForUser(
                    self.tr("Layer with name '%s' not found!") % layerName,
                    Qgis.Critical,
                    0,
                )
            return None
        return layers[0]

    def choozeLayerFrom(self, qgsMapLayer):
        if isinstance(qgsMapLayer, QgsVectorLayer):
            self.pointsLayerFrom.setEditText(qgsMapLayer.name())

    def choozeLayerTo(self, qgsMapLayer):
        if isinstance(qgsMapLayer, QgsVectorLayer):
            self.pointsLayerTo.setEditText(qgsMapLayer.name())

    def choozeResultLayer(self, qgsMapLayer):
        if isinstance(qgsMapLayer, QgsVectorLayer):
            self.linesLayer.setEditText(qgsMapLayer.name())

    def filedChooze(self, fieldName):
        self.sender().setEditText(fieldName)

    def chooseResultFilename(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("Choose file for save result"),
            self.curResultFilename,
            # QtCore.QFileInfo(self.curResultFilename).absolutePath()
        )
        self.leResultFilename.setText(filename)

    def getSettings(self):
        return [
            self.pointsLayerFrom.currentText(),
            self.pointsLayerTo.currentText(),
            self.fnIdFrom.currentText(),
            self.fnLink.currentText(),
            self.fnIdTo.currentText(),
            self.linesLayer.currentText(),
        ]
