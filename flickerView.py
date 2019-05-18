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
        self.cb2.currentIndexChanged.connect(self.changeSelectedLight)
        
        self.btn = QPushButton(self)
        self.btn.setText('boop')
        self.btn.clicked.connect(self.generateRandomKey)
        self.btn.move(20, 50)
        
        self.btn2 = QPushButton(self)
        self.btn2.setText('load lights')
        self.btn2.clicked.connect(self.updateSelectedLights)
        self.btn2.move(220, 20)
        
        self.btn3 = QPushButton(self)
        self.btn3.setText('Delete Key')
        self.btn3.clicked.connect(self.deleteKey)
        self.btn3.move(70, 50)
        
        self.table = QTableWidget(self)
        self.table.move(20, 90)
        self.table.cellChanged.connect(self.tableChanged)
        
        self.frameRangeText = QTextEdit(self)
        self.frameRangeText.move(300, 20)
        self.frameRangeText.setGeometry(300, 20, 70, 25)
        
        self.btn3 = QPushButton(self)
        self.btn3.setText('Load Keys')
        self.btn3.move(400, 20)
        self.btn3.clicked.connect(self.loadKeys)
      
        
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
        self.cb2.currentIndexChanged.connect(self.changeSelectedLight)

    
    def changeSelectedLight(self, i):
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]
        
        if self.keyRange is not None:
            self.loadTable(lightName, exposureType)
        else:
            print('boo')
        
    
    def loadTable(self, lightName, exposureType):
        self.table.cellChanged.disconnect()
        keys = keyframe(lightName + '.' + exposureType, time = (self.keyRange.start, self.keyRange.end), query = True, vc = True, tc = True)
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
                self.createErrorPopup()
                self.table.item(row, column).setText(str(self.keys[row][column]))
      
    
    def generateRandomKey(self):
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        e = random.random()
        t = random.randint(1,10)
        flickerUtils.setExposureKeyFrame(lightName, lightType, e, t)
        exposureType = flickerUtils.exposureDict[lightType]
        self.loadTable(lightName, exposureType)

    
    def createErrorPopup(self, str = "Please enter a valid value."):
        messageBox = QMessageBox(self)
        messageBox.setText(str)
        messageBox.setIcon(QMessageBox.Critical)
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.show()
    
    
    def deleteKey(self):
        #rendundant code with tablechanged
        keyRow = self.table.currentItem().row()
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]  
        oldTime = (self.keys[keyRow][0])              
        cutKey(lightName + '.' + exposureType, time = (oldTime, oldTime), option = 'keys')
        self.loadTable(lightName, exposureType)
        
    def loadKeys(self):
        try:
            keyText = self.frameRangeText.document().toPlainText()
            splitList = keyText.split(" ")
            keyStart = float(splitList[0])
            keyEnd = float(splitList[1])
            self.keyRange = flickerUtils.Range(keyStart, keyEnd)
            #self.changeSelectedLight(0) #0 doesnt matter
        except ValueError:
            self.createErrorPopup()  
        
        
        
