# -*- coding: utf-8 -*-
# ******************************************************************************
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
# *****************************************************************************
import os
import configparser


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if Singleton not in cls._instances:
            cls._instances[Singleton] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[Singleton]


class QgisPluginBase:
    __metaclass__ = Singleton

    def __init__(self):
        self.__plugin_dir = os.path.dirname(__file__)
        self.__readMeta()

    def __readMeta(self):
        meta_filename = os.path.join(self.__plugin_dir, "metadata.txt")
        config = configparser.ConfigParser()
        config.read([meta_filename])

        self._name = config.get("general", "name")
        self._version = config.get("general", "version")

    def normalizePluginName(self):
        return self._name.lower().replace(" ", "_")

    @property
    def i18nPath(self):
        return os.path.join(self.__plugin_dir, "i18n")

    @property
    def pluginDir(self):
        return self.__plugin_dir

    @property
    def pluginName(self):
        return self._name

    @property
    def pluginVersion(self):
        return self._version
