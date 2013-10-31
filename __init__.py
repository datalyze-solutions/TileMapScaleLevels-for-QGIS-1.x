# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TileMapScaleLevels
                                 A QGIS plugin
 Set the scale to the next matching Tile Map Scale.
                             -------------------
        begin                : 2013-01-23
        copyright            : (C) 2013 by Matthias Ludwig - Datalyze Solutions
        email                : development@datalyze-solutions.com
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

def name():
    return "Tile Map Scale Plugin"

def description():
    return "Sets the scale to the next matching Tile Map scale."

def version():
    return "Version 0.4"

def icon():
    return "icon.png"

def qgisMinimumVersion():
    return "1.8"

def author():
    return "Matthias Ludwig - Datalyze Solutions"

def email():
    return "development@datalyze-solutions.com"

def classFactory(iface):
    # load TileMapScaleLevels class from file TileMapScaleLevels
    from tilemapscalelevels import TileMapScaleLevelPlugin
    return TileMapScaleLevelPlugin(iface)