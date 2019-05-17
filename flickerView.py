import sys 
from PySide2.QtWidgets import * 
from PySide2.QtGui import QFont  
from PySide2.QtCore import QTimer
from PySide2 import QtCore
from pymel.core import *  
import flickerUtils
import imp
import random
imp.reload(flickerUtils)

    
class FlickerView(QWidget):
    def __init__(self):
        super(FlickerView, self).__init__()
        self.initUI()

    def initUI(self):
        
        self.cb2 = QComboBox(self)
        self.cb2.move(20, 20)
        self.cb2.setMinimumWidth(150)
        self.cb2.currentIndexChanged.connect(self.selectionChange2)
        
        self.btn = QPushButton(self)
        self.btn.setText('boop')
        self.btn.clicked.connect(self.pushButton)
        self.btn.move(20, 50)
        
        self.btn2 = QPushButton(self)
        self.btn2.setText('load lights')
        self.btn2.clicked.connect(self.updateSelectedLights)
        self.btn2.move(220, 20)
        
        self.table = QTableWidget(self)
        self.table.move(20, 90)
        self.table.cellChanged.connect(self.tableChanged)
        
        self.keys = []
        
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Flicker')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)        
        self.show()
    
    

    def updateSelectedLights(self):
        self.cb2.currentIndexChanged.disconnect()
        self.cb2.clear()
        newLights = []
        potentialLights = ls(sl=True)
        for pLight in potentialLights:
            children = listRelatives(pLight, s=True)
            for pChild in children:
                if nodeType(str(pChild)) in flickerUtils.exposureDict:
                    self.cb2.addItem(str(pChild))
        self.cb2.currentIndexChanged.connect(self.selectionChange2)

    
    def selectionChange2(self, i):
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]
        self.loadTable(lightName, exposureType)
        
    
    def loadTable(self, lightName, exposureType):
        self.table.cellChanged.disconnect()
        keys = keyframe(lightName + '.' + exposureType, time = (0, 10), query = True, vc = True, tc = True)
        self.keys = keys
        self.table.clear()
        self.table.setColumnCount(2)
        self.table.setRowCount(len(keys))
        self.table.setHorizontalHeaderLabels(["Frame", "Exposure"])
        
        for x in range(0, len(keys)):
            itemLeft = QTableWidgetItem(str(keys[x][0]))
            itemRight = QTableWidgetItem(str(keys[x][1]))
            self.table.setItem(x, 0, itemLeft)
            self.table.setItem(x, 1, itemRight)
        
        self.table.cellChanged.connect(self.tableChanged)
                
    def tableChanged(self, row, column):
        
        timeItem = self.table.item(row, 0)
        exposureItem = self.table.item(row, 1)
        
        if (timeItem is not None) and (exposureItem is not None):
            #print(row, column)
            try:
                time = float(timeItem.text())
                exposure = float(exposureItem.text())
                lightName = self.cb2.itemText(self.cb2.currentIndex())
                lightType = nodeType(lightName)
                exposureType = flickerUtils.exposureDict[lightType]
                
                
                oldTime = (self.keys[row][0])
                cutKey(lightName + '.' + exposureType, time = (oldTime, oldTime), option = 'keys')
                flickerUtils.setExposureKeyFrame(lightName, lightType, exposure, time)
                newTuple = (oldTime, exposure)
                self.keys[row] = newTuple  
                 
            except ValueError:
                messageBox = QMessageBox(self)
                messageBox.setText("Please enter a float.")
                messageBox.setIcon(QMessageBox.Critical)
                messageBox.setStandardButtons(QMessageBox.Ok)
                messageBox.show()
                self.table.item(row, column).setText(str(self.keys[row][column]))
                     
    
    def pushButton(self):
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        e = random.random()
        t = random.randint(1,10)
        flickerUtils.setExposureKeyFrame(lightName, lightType, e, t)

    
    
    
        