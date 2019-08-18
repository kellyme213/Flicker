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
        self.loadLightsButton.clicked.connect(self.getSelectedLights)
        
        self.lightComboBox = self.window.findChild(QComboBox, 'lightComboBox')
        self.lightComboBox.activated.connect(self.loadSelectedLight)
    
        self.keyTableWidget = self.window.findChild(QTableWidget, 'keyTableWidget')
        self.keyTableWidget.cellChanged.connect(self.tableChanged)

        self.keyRangeTextEdit = self.window.findChild(QTextEdit, 'keyRangeTextEdit')

        self.loadKeysButton = self.window.findChild(QPushButton, 'loadKeysButton')
        self.loadKeysButton.clicked.connect(self.loadKeys)
    
        self.randomKeyButton = self.window.findChild(QPushButton, 'randomKeyButton')
        self.randomKeyButton.clicked.connect(self.generateRandomKey)

        self.deleteKeyButton = self.window.findChild(QPushButton, 'deleteKeyButton')
        self.deleteKeyButton.clicked.connect(self.deleteKey)
        
        self.biasTextEdit = self.window.findChild(QTextEdit, 'biasTextEdit')
        
        self.generateKeysButton = self.window.findChild(QPushButton, 'generateKeysButton')
        self.generateKeysButton.clicked.connect(self.generateRandomKeys)
        
        self.exposureRange1TextEdit = self.window.findChild(QTextEdit, 'exposureRange1TextEdit')
        self.exposureRange2TextEdit = self.window.findChild(QTextEdit, 'exposureRange2TextEdit')

        self.timeRange1TextEdit = self.window.findChild(QTextEdit, 'timeRange1TextEdit')
        self.timeRange2TextEdit = self.window.findChild(QTextEdit, 'timeRange2TextEdit')

        self.keys = []
    
        self.window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.window.show()
        #self.initUI()

    def initUI(self):
        
        self.cb2 = QComboBox(self)
        self.cb2.move(20, 20)
        self.cb2.setMinimumWidth(150)
        self.cb2.activated.connect(self.loadSelectedLight)
        
        self.btn = QPushButton(self)
        self.btn.setText('boop')
        self.btn.clicked.connect(self.generateRandomKey)
        self.btn.move(20, 50)
        
        self.btn2 = QPushButton(self)
        self.btn2.setText('load lights')
        self.btn2.clicked.connect(self.getSelectedLights)
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
    
    

    def getSelectedLights(self):
        self.lightComboBox.activated.disconnect()
        self.lightComboBox.clear()
        newLights = []
        potentialLights = ls(sl=True)
        for pLight in potentialLights:
            children = listRelatives(pLight, s=True)
            for pChild in children:
                if nodeType(str(pChild)) in flickerUtils.exposureDict:
                    self.lightComboBox.addItem(str(pChild))
        self.lightComboBox.activated.connect(self.loadSelectedLight)

    
    def loadSelectedLight(self, i):
        lightName = self.lightComboBox.itemText(i)
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]
        
        try:
            self.loadKeyRange()
            self.loadTable(lightName, exposureType)
        except AttributeError:
            self.createErrorPopup("Please enter a valid key range.")
            self.keyTableWidget.cellChanged.connect(self.tableChanged)

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
      

    def generateRandomFloatInRange(self, start, end):
        return ((end - start) * random.random()) + start

    def generateRandomValueInRange(self, range):
        return self.generateRandomFloatInRange(range.start, range.end)
    
    def generateRandomIntInRange(self, range):
        return random.randint(range.start, range.end)
    
    def generateRangeFromText(self, text, shouldBeIntegers = False):
        try:
            textList = text.split(" ")
            start = float(textList[0])
            end = float(textList[1])
            
            if (shouldBeIntegers):
                if (abs(start - int(start)) > 0.001 or abs(end - int(end)) > 0.001):
                    self.createErrorPopup("Warning: converting " + start + " and " + end + "to integers.")
                start = int(start)
                end = int(end)
            
            return flickerUtils.Range(start, end)
        except ValueError:
            self.createErrorPopup("Cannot generate range from " + text + ". A range should be two numbers separated by a space.")
    
    def generateRandomExposure(self, randomNum = 0.0):
        try:
            bias = float(self.biasTextEdit.document().toPlainText())
            exposureRangeText = ""
        
            if (randomNum > bias):
                exposureRangeText = self.exposureRange1TextEdit.document().toPlainText()
            else:
                exposureRangeText = self.exposureRange2TextEdit.document().toPlainText()

            exposureRange = self.generateRangeFromText(exposureRangeText)
    
            return self.generateRandomValueInRange(exposureRange)

        except ValueError:
            self.createErrorPopup("Please enter valid values.")
    
    def generateRandomKey(self):
        lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
        lightType = nodeType(lightName)
        e = self.generateRandomExposure(random.random())
        t = random.randint(self.keyRange.start, self.keyRange.end)
        flickerUtils.setExposureKeyFrame(lightName, lightType, e, t)
        exposureType = flickerUtils.exposureDict[lightType]
        self.loadTable(lightName, exposureType)

    def generateRandomKeys(self):
        self.loadKeyRange()
        currentFrame = self.keyRange.start
        lightName = self.lightComboBox.itemText(self.lightComboBox.currentIndex())
        lightType = nodeType(lightName)
        exposureType = flickerUtils.exposureDict[lightType]
        
        while (currentFrame <= self.keyRange.end):
            randomNum = random.random()
            bias = float(self.biasTextEdit.document().toPlainText())
            randomExposure = self.generateRandomExposure(randomNum)
            rangeText = ""

            if (randomNum > bias):
                rangeText = self.timeRange1TextEdit.document().toPlainText()
            else:
                rangeText = self.timeRange2TextEdit.document().toPlainText()

            timeRange = self.generateRangeFromText(rangeText, True)
            randomFrameJump = self.generateRandomIntInRange(timeRange)

            flickerUtils.setExposureKeyFrame(lightName, lightType, randomExposure, currentFrame)

            currentFrame += randomFrameJump

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


    def loadKeyRange(self):
        try:
            keyText = self.keyRangeTextEdit.document().toPlainText()
            splitList = keyText.split(" ")
            keyStart = float(splitList[0])
            keyEnd = float(splitList[1])
            self.keyRange = flickerUtils.Range(keyStart, keyEnd)
        except ValueError:
                self.createErrorPopup("Please enter a valid key range.")

    def loadKeys(self):
        self.loadKeyRange()
        self.loadSelectedLight(self.lightComboBox.currentIndex())
        
        
        
