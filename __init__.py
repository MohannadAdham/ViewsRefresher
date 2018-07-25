# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ViewsRefresher
                                 A QGIS plugin
 This plugin refreshes the views that control the quality of the data in a FTTH project.
                             -------------------
        begin                : 2018-07-25
        copyright            : (C) 2018 by Mohannad ADHAM / Axians
        email                : mohannad.adm@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ViewsRefresher class from file ViewsRefresher.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .views_refresher import ViewsRefresher
    return ViewsRefresher(iface)
