# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:17:02 2019

@author: Daniel
"""

import sys
from PyQt5.QtWidgets import *

def interface_main():
    app = QApplication(sys.argv)
    track_app = trackerApp()
    track_app.show()
    track_app.exec_()


class trackerApp(QDialog):
    def __init__(self, parent=None):
        super(trackerApp, self).__init__(parent)
        self.originalPalette = QApplication.palette()
        
        self.createTopLeftGroupBox()
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.topLeftGroupBox, 1, 0)
        self.setLayout(mainLayout)
        
        
    def createTopLeftGroupBox(self):
        self.topLeftGroupBox = QGroupBox("Add trackers in the analysis")

        radioButton1 = QRadioButton("SIAMESE 1")
        radioButton2 = QRadioButton("GoogleNet")
        radioButton3 = QRadioButton("ResNet")
        radioButton1.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(radioButton1)
        layout.addWidget(radioButton2)
        layout.addWidget(radioButton3)
        layout.addStretch(1)
        self.topLeftGroupBox.setLayout(layout)  


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gallery = trackerApp()
    gallery.show()
    
    sys.exit(app.exec_()) 