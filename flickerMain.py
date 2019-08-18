#~/Library/Preferences/Autodesk/maya/<version>/scripts
#sys.pathToUserData is set here
import flickerView
import flickerUtils
import imp
import sys 
 
imp.reload(flickerView)
imp.reload(flickerUtils)
if __name__ == "__main__":
    ex = flickerView.FlickerView(sys.pathToUserData + 'test.ui')