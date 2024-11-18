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

from qgis.PyQt import QtCore

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)


class Worker(QtCore.QObject):
    started = QtCore.pyqtSignal()
    stoped = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int, int)
    error = QtCore.pyqtSignal(str)

    def __init__(
        self,
        plFrom: QgsVectorLayer,
        plTo: QgsVectorLayer,
        fIdFromName,
        fLinkName,
        fIdToName,
        resLayer,
    ) -> None:
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

            # print(f'{self.plFrom.crs()=}', f'{self.plTo.crs()=}')

            from_transform = QgsCoordinateTransform(
                self.plFrom.crs(), self.resLayer.crs(), QgsProject.instance()
            )
            to_transform = QgsCoordinateTransform(
                self.plTo.crs(), self.resLayer.crs(), QgsProject.instance()
            )

            featureCounter = 0
            featureCount = self.plFrom.featureCount()
            for featureFrom in self.plFrom.getFeatures():
                self.progressChanged.emit(featureCounter, featureCount)
                for featureTo in self.plTo.getFeatures():
                    forignKey = featureFrom.attribute(self.fLinkName)
                    primaryKey = featureTo.attribute(self.fIdToName)
                    if forignKey == primaryKey:
                        # Plugin().plPrint("feature: %d - %d" % (forignKey, primaryKey))

                        from_geometry: QgsGeometry = featureFrom.geometry()
                        from_geometry.transform(from_transform)
                        to_geometry: QgsGeometry = featureTo.geometry()
                        to_geometry.transform(to_transform)

                        point_from = from_geometry.vertexAt(0)
                        point_to = to_geometry.vertexAt(0)

                        if QgsWkbTypes.hasZ(
                            point_to.wkbType()
                        ) and not QgsWkbTypes.hasZ(point_from.wkbType()):
                            point_from.addZValue()

                        if QgsWkbTypes.hasZ(
                            point_from.wkbType()
                        ) and not QgsWkbTypes.hasZ(point_to.wkbType()):
                            point_to.addZValue()

                        lineFeature = QgsFeature()
                        lineFeature.setGeometry(
                            QgsGeometry.fromPolyline([point_from, point_to])
                        )
                        lineFeature.setAttributes(
                            [
                                self.plFrom.name(),
                                self.plTo.name(),
                                featureFrom.attribute(self.fIdFromName),
                                primaryKey,
                            ]
                        )

                        provider.addFeatures([lineFeature])

                featureCounter += 1
            self.stoped.emit()
        except KeyError as e:
            self.error.emit("There is no attribute with name: " + str(e))
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.resLayer.commitChanges()
