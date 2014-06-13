from twindow.baseUI import tcloudWidget

"""
about ui
"""
class about(tcloudWidget):
    
    def __init__(self):
        tcloudWidget.__init__(self,"about.ui", "about")
        self.topwin.set_default_size(300,200)
        
    def show(self):
        self.topwin.present()
        
        
    
    