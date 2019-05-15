import sys 
from PySide2.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton) 
from PySide2.QtGui import QFont  
from pymel.core import *  

exposureDict = {
    "aiAreaLight": "aiExposure",
    "aiMeshLight": "aiExposure",
    "aiSkyDomeLight": "aiExposure",
    "aiPhotometricLight": "aiExposure",
    "PxrRectLight": "exposure",
    "PxrDiskLight": "exposure",
    "PxrSphereLight": "exposure",
    "PxrCylinderLight": "exposure",
    "PxrMeshLight": "exposure",
}

def collectNamesOfType(_type):
    names = ls(type=_type)
    ret = []
    for n in names:
        ret.append(n)
    return ret
    
def setExposureKeyFrame(lightName, lightType, exposure, time):
    setKeyframe(lightName, at=exposureDict[lightType], t=time, v=exposure)
    
class Range:
    def __init__(self, s, e):
        self.start = s
        self.end = e