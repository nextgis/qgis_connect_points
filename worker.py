# -*- coding: utf-8 -*-
#******************************************************************************
#
# Points2Lines
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

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFeatureRequest,
    QgsGeometry,
)

from qgis_plugin_base import Plugin


class Worker(QtCore.QObject):

    started = QtCore.pyqtSignal()
    stoped = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int, int)
    error = QtCore.pyqtSignal(unicode)

    def __init__(self, plFrom, plTo, fIdFromName, fLinkName, fIdToName, resLayer):
        QtCore.QObject.__init__(self)

        # Plugin().plPrint("Worker __init__")

        self.plFrom = plFrom
        self.plTo = plTo
        self.fIdFromName = fIdFromName
        self.fLinkName = fLinkName
        self.fIdToName = fIdToName

        self.resLayer = resLayer

    def run(self):
        self.started.emit()

        try:
            self.resLayer.startEditing()

            for feature in self.resLayer.getFeatures():
                self.resLayer.deleteFeature(feature.id())

            self.resLayer.commitChanges()

            self.resLayer.startEditing()

            provider = self.resLayer.dataProvider()

            featureCounter = 0
            featureCount = self.plFrom.featureCount()
            for featureFrom in self.plFrom.getFeatures():
                self.progressChanged.emit(featureCounter, featureCount)
                for featureTo in self.plTo.getFeatures():
                    forignKey = featureFrom.attribute(self.fLinkName)
                    primaryKey = featureTo.attribute(self.fIdToName)
                    if forignKey == primaryKey:
                        # Plugin().plPrint("feature: %d - %d" % (forignKey, primaryKey))
                        lineFeature = QgsFeature()
                        lineFeature.setGeometry(
                            QgsGeometry.fromPolyline([
                                featureFrom.geometry().asPoint(),
                                featureTo.geometry().asPoint(),
                            ])
                        )
                        lineFeature.setAttributes(
                            [
                                self.plFrom.name(),
                                self.plTo.name(),
                                featureFrom.attribute(self.fIdFromName),
                                primaryKey
                            ]
                        )

                        provider.addFeatures([lineFeature])
                featureCounter += 1
            self.stoped.emit()
        except KeyError as e:
            self.error.emit(u"There is no attribute with name: " + unicode(e))
        except Exception as e:
            self.error.emit(unicode(e))
        finally:
            self.resLayer.commitChanges()
