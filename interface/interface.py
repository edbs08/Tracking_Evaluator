# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:17:02 2019

@author: Daniel
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFileInfo

def interface_main():
    app = QApplication(sys.argv)
    track_app = trackerApp()
    track_app.show()
    track_app.exec_()


class trackerApp(QDialog):
    def __init__(self, parent=None):
        super(trackerApp, self).__init__(parent)
        self.trackers_res=[]
        self.originalPalette = QApplication.palette()
        
        self.createLoadFiles()
        self.createSelectTrackers()
        self.createEvalType()
        self.createSequenceList()
        self.createChallengeList()
        run_eval = QPushButton("Run")
    
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.loadFiles,1,0)
        mainLayout.addWidget(self.trackerList, 2, 0 )
        
        
        self.check_eval_type()
        
        mainLayout.addWidget(self.evalType, 0, 1,1,2 )
        mainLayout.addWidget(self.sequences, 1,1 )
        mainLayout.addWidget(self.challenges, 1,2 )
        mainLayout.addWidget(run_eval,2,1)
        self.setLayout(mainLayout)
        
        
    def createLoadFiles(self):
        self.loadFiles = QGroupBox("Load tracker Results")
        
        self.listwidget = QListWidget()
        self.listwidget.setUpdatesEnabled(True)
        
        btn1 = QPushButton("QFileDialog object")
        btn1.clicked.connect(self.getfiles)
        
        layout = QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addWidget(btn1)
        self.loadFiles.setLayout(layout)  
        
    def getfiles(self):
       fname = QFileDialog.getOpenFileName(self, 'Open file', 
         'c:\\',"Text Files (*.txt)")
       fi = QFileInfo(fname[0])
       self.trackers_res.append(fi.baseName())
       # update List Options
       self.listwidget.insertItem(len(self.trackers_res),"%s" % fi.baseName())
       print(self.trackers_res)
       self.listwidget.repaint()
       self.update()
    
        
    def createSelectTrackers(self):
        self.trackerList = QGroupBox("Add trackers in the analysis")

        CheckBox1 = QCheckBox("SIAMESE 1")
        CheckBox2 = QCheckBox("GoogleNet")
        CheckBox3 = QCheckBox("ResNet")
        CheckBox1.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(CheckBox1)
        layout.addWidget(CheckBox2)
        layout.addWidget(CheckBox3)
        layout.addStretch(1)
        self.trackerList.setLayout(layout) 
        
    def createEvalType(self):
        self.evalType = QGroupBox("Define type of evaluation")
        
        self.radioButton1 = QRadioButton("Per sequence")
        self.radioButton1.setChecked(True)
        self.radioButton2 = QRadioButton("Per challenge")
        
        self.radioButton1.toggled.connect(self.check_eval_type)

        
        layout = QVBoxLayout()
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)
        self.evalType.setLayout(layout) 
        
    def createSequenceList(self):
        self.sequences = QGroupBox("Sequences available")
        
        CheckBox1 = QCheckBox("basketball")
        CheckBox2 = QCheckBox("fernando")
        CheckBox3 = QCheckBox("girl")
        CheckBox4 = QCheckBox("graduate")
        CheckBox5 = QCheckBox("iceskater1")
        CheckBox6 = QCheckBox("matrix")
        CheckBox6 = QCheckBox("nature")
        CheckBox7 = QCheckBox("tiger")
        
        layout = QVBoxLayout()
        layout.addWidget(CheckBox1)
        layout.addWidget(CheckBox2)
        layout.addWidget(CheckBox3)
        layout.addWidget(CheckBox4)
        layout.addWidget(CheckBox5)
        layout.addWidget(CheckBox6)
        layout.addWidget(CheckBox7)
        self.sequences.setLayout(layout) 
        
    def createChallengeList(self):
        self.challenges = QGroupBox("Challenges")
        
        CheckBox1 = QCheckBox("Camera Motion")
        CheckBox2 = QCheckBox("Illumination Changes")
        CheckBox3 = QCheckBox("Motion Changes")
        CheckBox4 = QCheckBox("Occlusion")
        CheckBox5 = QCheckBox("Size change")

        layout = QVBoxLayout()
        layout.addWidget(CheckBox1)
        layout.addWidget(CheckBox2)
        layout.addWidget(CheckBox3)
        layout.addWidget(CheckBox4)
        layout.addWidget(CheckBox5)
        self.challenges.setLayout(layout) 
        
    def check_eval_type(self):
        if (self.radioButton2.isChecked()):
             self.sequences.setEnabled(False)
        else:
            self.sequences.setEnabled(True)
            
        if (self.radioButton1.isChecked()):
             self.challenges.setEnabled(False)
        else:
            self.challenges.setEnabled(True)
        self.listwidget.repaint()
        self.update()
        

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gallery = trackerApp()
    gallery.show()
    
    sys.exit(app.exec_()) 