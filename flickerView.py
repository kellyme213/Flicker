import sys 
from PySide2.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QComboBox) 
from PySide2.QtGui import QFont  
from PySide2.QtCore import QTimer
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
        self.cb = QComboBox(self)
        for val in flickerUtils.exposureDict:
            self.cb.addItem(val)
        self.cb.move(20, 20)
        self.cb.currentIndexChanged.connect(self.selectionChange)
        
        self.cb2 = QComboBox(self)
        self.cb2.move(20, 70)
        
        self.btn = QPushButton(self)
        self.btn.setText('boop')
        self.btn.clicked.connect(self.pushButton)
        self.btn.move(20, 120)
        
        self.btn2 = QPushButton(self)
        self.btn2.setText('hi')
        self.btn2.clicked.connect(self.updateSelectedLights)
        self.btn2.move(220, 20)
        
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Flicker')
        
        self.show()
    
    def selectionChange(self, i):
        lightType = self.cb.itemText(i)
        names = flickerUtils.collectNamesOfType(lightType)
        self.cb2.clear()
        for name in names:
            self.cb2.addItem(str(name))
        #self.cb2.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLength)
        self.cb2.setMinimumWidth(150)#self.cb2.minimumSizeHint().width())

    def updateSelectedLights(self):
        self.cb2.clear()
        newLights = []
        potentialLights = ls(sl=True)
        for pLight in potentialLights:
            children = listRelatives(pLight, s=True)
            for pChild in children:
                if nodeType(str(pChild)) in flickerUtils.exposureDict:
                    #print(pLight)
                    self.cb2.addItem(str(pChild))

    
    def selectionChange2(self, i):
        print('hi')
        
    def pushButton(self):
        lightName = self.cb2.itemText(self.cb2.currentIndex())
        lightType = nodeType(lightName)
        e = random.random()
        t = random.randint(1,10)
        flickerUtils.setExposureKeyFrame(lightName, lightType, e, t)
        print(e, t)
        #setAttr(lightName + '.' + flickerUtils.exposureDict[lightType], random.random())

    
    
    
        