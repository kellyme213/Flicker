import sys 
from PySide2.QtWidgets import * 
from PySide2.QtGui import QFont  
from PySide2.QtCore import QTimer
from PySide2 import QtCore
from pymel.core import *
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile
import flickerUtils
import imp
import random
imp.reload(flickerUtils)

    
class FlickerView(QWidget):
    def __init__(self, uiFilePath):
        super(FlickerView, self).__init__()
        
        uiFile = QFile(uiFilePath)
        uiFile.open(QFile.ReadOnly)
        
        loader = QUiLoader()
        self.window = loader.load(uiFile)
        uiFile.close()

        
        self.loadLightsButton = self.window.findChild(QPushButton, 'loadLightsButton')
        self.loadLightsButton.clicked.connect(self.updateSelectedLights)
        
        self.lightComboBox = self.window.findChild(QComboBox, 'lightComboBox')
        self.lightComboBox.activated.connect(self.changeSelectedLight)
    
        self.keyTableWidget = self.window.findChild(QTableWidget, 'keyTableWidget')
        self.keyTableWidget.cellChanged.connect(self.tableChanged)

        self.keyRangeTextEdit = self.window.findChild(QTextEdit, 'keyRangeTextEdit')

        self.loadKeysButton = self.window.findChild(QPushButton, 'loadKeysButton')
        self.loadKeysButton.clicked.connect(self.loadKeys)
    


        self.keys = []
    
        self.window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.window.show()
        #self.initUI()

    def initUI(self):
        
        self.cb2 = QComboBox(self)
        self.cb2.move(20, 20)
        self.cb2.setMinimumWidth(150)
        self.cb2.activated.connect(self.changeSelectedLight)
        
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
        self.lightComboBox.activated.disconnect()
        self.lightComboBox.clear()
        newLights = []
        potentialLights = ls(sl=True)
        for pLight in potentialLights:
            children = listRelatives(pLight, s=True)
            for pChild in children:
                if nodeType(str(pChild)) in flickerUtils.exposureDict:
                    self.lightComboBox.addItem(str(pChild))
        self.lightComboBox.activated.connect(self.changeSelectedLight)

    
    def changeSelectedLight(self, i):
        lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]
        
        try:
            self.loadTable(lightName, exposureType)
        except AttributeError:
            self.createErrorPopup("Please enter a valid key range.")
            self.keyTableWidget.cellChanged.connect(self.tableChanged)
        

    #def loadKeys(self):
        #self.changeSelectedLight(0) #0 doesn't matter

    def loadTable(self, lightName, exposureType):
        self.keyTableWidget.cellChanged.disconnect()
        keys = keyframe(lightName + '.' + exposureType, time = (self.keyRange.start, self.keyRange.end), query = True, vc = True, tc = True)
        self.keys = keys
        self.keyTableWidget.clearContents()
        self.keyTableWidget.setRowCount(len(keys))
        #self.table.setColumnCount(2)
        #self.table.setRowCount(len(keys))
        #self.table.setHorizontalHeaderLabels(["Frame", "Exposure"])
        
        for x in range(0, len(keys)):
            itemLeft = QTableWidgetItem(str(keys[x][0]))
            itemRight = QTableWidgetItem(str(keys[x][1]))
            self.keyTableWidget.setItem(x, 0, itemLeft)
            self.keyTableWidget.setItem(x, 1, itemRight)
        
        self.keyTableWidget.cellChanged.connect(self.tableChanged)
                
    def tableChanged(self, row, column):
        
        timeItem = self.keyTableWidget.item(row, 0)
        exposureItem = self.keyTableWidget.item(row, 1)
        
        if (timeItem is not None) and (exposureItem is not None):
            try:
                time = float(timeItem.text())
                exposure = float(exposureItem.text())
                lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
                lightType = nodeType(lightName)
                exposureType = flickerUtils.exposureDict[lightType]
                
                
                oldTime = (self.keys[row][0])
                cutKey(lightName + '.' + exposureType, time = (oldTime, oldTime), option = 'keys')
                flickerUtils.setExposureKeyFrame(lightName, lightType, exposure, time)
                newTuple = (oldTime, exposure)
                self.keys[row] = newTuple  
                 
            except ValueError:
                self.createErrorPopup()
                self.keyTableWidget.item(row, column).setText(str(self.keys[row][column]))
      
    
    def generateRandomKey(self):
        lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
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
        keyRow = self.keyTableWidget.currentItem().row()
        lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]  
        oldTime = (self.keys[keyRow][0])              
        cutKey(lightName + '.' + exposureType, time = (oldTime, oldTime), option = 'keys')
        self.loadTable(lightName, exposureType)
        
    def loadKeys(self):
        try:
            keyText = self.keyRangeTextEdit.document().toPlainText()
            splitList = keyText.split(" ")
            keyStart = float(splitList[0])
            keyEnd = float(splitList[1])
            self.keyRange = flickerUtils.Range(keyStart, keyEnd)
        except ValueError:
            self.createErrorPopup("Please enter a valid key range.")
        
        
        
