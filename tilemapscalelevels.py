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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from qgis.core import *
from qgis.gui import *
import os
import math

# Initialize Qt resources from file resources.py
import resources_rc

class TileMapScaleLevelPlugin():

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # initialize plugin directories
        self.workingDir = os.path.dirname(os.path.abspath(__file__))        
        self.datasetDir = os.path.join(self.workingDir, "datasets")
        if not os.path.exists(self.datasetDir):
            self.iface.messageBar().pushMessage("Error", "Can't find %s. You wont't be able to load any datasets." % self.datasetDir, QgsMessageBar.CRITICAL)
        
        # initialize locale
        localePath = ""
        locale = QSettings().value("locale/userLocale", type=str)[0:2]

        if QFileInfo(self.workingDir).exists():
            localePath = self.workingDir + "/i18n/tilemapscalelevels_" + locale + ".qm"

        if QFileInfo(localePath).exists():
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/icons/icon.png"),
            u"Tile Map Scale Plugin", self.iface.mainWindow())

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Tile Map Scale Plugin", self.action)
        #QObject.connect(self.action, SIGNAL("triggered()"), self.showDock)
        self.action.triggered.connect(self.showDock)
                	
	self.dock = uic.loadUi(os.path.join(self.workingDir, "ui_tilemapscalelevels.ui"))
	
	self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock)

	self.projection = self.canvas.mapRenderer().destinationCrs()

	self.canvas.enableAntiAliasing(True)
               
	self.readStatus()
        QObject.connect(self.canvas, SIGNAL("scaleChanged(double)"), self.scaleChanged)
        #self.canvas.scaleChanged.connect(self.scaleChanged)

	self.dock.sliderZoomlevels.sliderReleased.connect(self.sliderReleased)
        self.dock.spinBoxZoomlevels.editingFinished.connect(self.editingFinished)
        self.dock.checkBoxIsActive.stateChanged.connect(self.activationStateChanged)
        self.dock.checkBoxUseMercator.stateChanged.connect(self.useMercator)
        self.dock.checkBoxUseOnTheFlyTransformation.stateChanged.connect(self.useOnTheFlyTransformation)
        
        self.dock.buttonLoadOSM.clicked.connect(self.loadOSM)
        
        self.dock.buttonLoadUserDataset.clicked.connect(self.loadSelectedUserDataset)
        self.dock.buttonLoadRefreshUserDatasets.clicked.connect(self.initUserDatasets)
        
	self.scaleCalculator = TileMapScaleLevels()

	self.initUserDatasets()
	
    def showDock(self):
	if self.dock.isVisible():
	  self.dock.hide()
	else:
	  self.dock.show()
    
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Tile Map Scale Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)

    def sliderReleased(self):
	zoomlevel = self.dock.sliderZoomlevels.value()
	scale = self.scaleCalculator.getScale(zoomlevel)
	self.scaleChanged(scale)

    def editingFinished(self):
	zoomlevel = self.dock.spinBoxZoomlevels.value()
	scale = self.scaleCalculator.getScale(zoomlevel)
	self.scaleChanged(scale)
	
    def setScaleWithSlider(self):
	pass
      
    def setScaleWithSpinBox(self):
	pass
      
    def loadOSM(self):
        datasetPath = os.path.join(self.datasetDir, "osm_mapnik.xml")
        if os.path.exists(datasetPath):
            self.iface.addRasterLayer(datasetPath, "OpenStreetMap - Mapnik")
        else:
            self.iface.messageBar().pushMessage("Error", "Unable to load file %s" % datasetPath, QgsMessageBar.CRITICAL)

    def initUserDatasets(self):
        self.dock.comboBoxUserDatasets.clear()
        for filename in os.listdir(self.datasetDir):
            if not filename.endswith('.xml'): continue
            print filename
            self.dock.comboBoxUserDatasets.addItem(filename)

    def loadSelectedUserDataset(self):
        selectedDataset = self.dock.comboBoxUserDatasets.currentText()
        datasetPath = os.path.join(self.datasetDir, selectedDataset)
        errorMessage = "Unable to load file %s" % datasetPath
        if (selectedDataset == ""):            
            self.iface.messageBar().pushMessage("Error", errorMessage, QgsMessageBar.CRITICAL)
        elif os.path.exists(datasetPath):
            self.iface.addRasterLayer(datasetPath, selectedDataset)
        else:
            self.iface.messageBar().pushMessage("Error", errorMessage, QgsMessageBar.CRITICAL)
        
        
    def scaleChanged(self, scale):
	if self.dock.checkBoxIsActive.isChecked():
            #print scale
	    ## Disconnect to prevent infinite scaling loop
	    QObject.disconnect(self.canvas, SIGNAL("scaleChanged(double)"), self.scaleChanged)
	    ##self.canvas.scaleChanged.disconnect(self.scaleChanged)
	    
	    zoomlevel = self.scaleCalculator.getZoomlevel(scale)
	    if zoomlevel <> None:
		newScale = self.scaleCalculator.getScale(zoomlevel)
		self.canvas.zoomScale(newScale)
		self.dock.sliderZoomlevels.setValue(zoomlevel)
	    QObject.connect(self.canvas, SIGNAL("scaleChanged(double)"), self.scaleChanged)
	    ##self.canvas.scaleChanged.connect(self.scaleChanged)

    def activationStateChanged(self):
        if self.dock.checkBoxIsActive.isChecked():
            self.dock.groupBox.show()
        else:
            self.dock.groupBox.hide()
        self.storeStatus()

    def useMercator(self):       
        if self.dock.checkBoxUseMercator.isChecked():
            coordinateReferenceSystem = QgsCoordinateReferenceSystem()
            createCrs = coordinateReferenceSystem.createFromString("EPSG:3857")

            if self.projection != coordinateReferenceSystem:
                self.projection = self.canvas.mapRenderer().destinationCrs()
            
            self.canvas.mapRenderer().setDestinationCrs(coordinateReferenceSystem)
        else:
            self.canvas.mapRenderer().setDestinationCrs(self.projection)
    
    def useOnTheFlyTransformation(self):
        if self.dock.checkBoxUseOnTheFlyTransformation.isChecked():
            self.canvas.mapRenderer().setProjectionsEnabled(True)
        else:
            self.canvas.mapRenderer().setProjectionsEnabled(False)            
      
    def storeStatus(self):
        s = QSettings()
        s.setValue("tilemapscalelevels/active", self.dock.checkBoxIsActive.isChecked())

    def readStatus(self):
        s = QSettings()
        isActive = s.value("tilemapscalelevels/active", True, type=bool)
        self.dock.checkBoxIsActive.setChecked(isActive)
	    

class TileMapScaleLevels:
    #import math
    def __init__(self, dpi = 96):
        self.dpi = dpi
        self.inchesPerMeter = 39.37
        self.maxScalePerPixel = 156543.04

    def getScale(self, zoomlevel):
	if zoomlevel < 0:
	    return (self.dpi * self.inchesPerMeter * self.maxScalePerPixel) / (math.pow(2, 0))
	else:
	    zoomlevel = int(zoomlevel)
	    return (self.dpi * self.inchesPerMeter * self.maxScalePerPixel) / (math.pow(2, zoomlevel))
	    
    def getZoomlevel(self, scale):
	if scale <> 0:
	    return int(round(math.log( ((self.dpi * self.inchesPerMeter * self.maxScalePerPixel) / scale), 2 ), 0))