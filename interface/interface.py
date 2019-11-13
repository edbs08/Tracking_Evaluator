# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:17:02 2019

@author: Daniel
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFileInfo

g_sequences = []
g_trackers = []

chall_available = ["Camera Motion","Illumination Changes","Motion Changes","Occlusion","Size change"]
metrics_available = ["Accuracy","Robustness","Precision(Center Location Error)"]

#final global outputs of interface
trackers_paths = []
trackers_extra = []
eval_type = []
sequences_final = []
challenges_final = []
metrics = []

def interface_main(sequences,trackers):
    global g_sequences
    global g_trackers
    g_trackers = trackers
    g_sequences = sequences
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
        self.createMetricsList()
        
        run_eval = QPushButton("Run")
        run_eval.clicked.connect(self.passEvaluatorConfig)
        
        
        
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.loadFiles,1,0)
        mainLayout.addWidget(self.trackerList, 2, 0 )
        
        
        self.check_eval_type()
        
        mainLayout.addWidget(self.evalType, 0, 1,1,2 )
        mainLayout.addWidget(self.sequences, 1,1 )
        mainLayout.addWidget(self.challenges, 1,2 )
        mainLayout.addWidget(self.metrics, 2,1 )
        mainLayout.addWidget(run_eval,2,2)
        self.setLayout(mainLayout)
        
        
    def createLoadFiles(self):
        self.loadFiles = QGroupBox("Load tracker Results")
        
        self.listwidget = QListWidget()
        self.listwidget.setUpdatesEnabled(True)
        
        btn1 = QPushButton("Load Trackers")
        btn1.clicked.connect(self.getfiles)
        
        clear_data = QPushButton("Clear")
        clear_data.clicked.connect(self.clearTrackers)
        
        layout = QVBoxLayout()
        layout.addWidget(self.listwidget)
        layout.addWidget(btn1)
        layout.addWidget(clear_data)
        self.loadFiles.setLayout(layout)  
        
    def getfiles(self):
       fname = QFileDialog.getOpenFileName(self, 'Open file', 
         'c:\\',"Text Files (*.txt)")
       fi = QFileInfo(fname[0])

       global trackers_paths
       trackers_paths.append(fname[0])
       self.trackers_res.append(fi.baseName())
       # update List Options
       self.listwidget.insertItem(len(self.trackers_res),"%s" % fi.baseName())
#       print(self.trackers_res)
       self.listwidget.repaint()
       self.update()
    
        
    def createSelectTrackers(self):
        self.trackerList = QGroupBox("Add trackers in the analysis")

        layout = QVBoxLayout()
        counter = 0;
        self.CheckBox_tr = [];
        for track in g_trackers:
            self.CheckBox_tr.append(QCheckBox(track))
            layout.addWidget(self.CheckBox_tr[counter])
            counter = counter+1;
    
        if len(self.CheckBox_tr) > 0:
            self.CheckBox_tr[0].setChecked(True)

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
        
        layout = QVBoxLayout()
        counter = 0
        self.CheckBox_seq = []
        for seq in g_sequences:
            self.CheckBox_seq.append(QCheckBox(seq))
            layout.addWidget(self.CheckBox_seq[counter])
            counter = counter + 1
            
        if len(self.CheckBox_seq) > 0:
            self.CheckBox_seq[0].setChecked(True)
        self.sequences.setLayout(layout) 
        
    def createChallengeList(self):
        self.challenges = QGroupBox("Challenges")
        
        self.CheckBox_chall = []
        layout = QVBoxLayout()
        counter = 0
        for ch in chall_available:
            self.CheckBox_chall.append(QCheckBox(ch))
            layout.addWidget(self.CheckBox_chall[counter])
            counter = counter + 1

        self.CheckBox_chall[0].setChecked(True)

        self.challenges.setLayout(layout) 
    
    def createMetricsList(self):
        self.metrics = QGroupBox("Metrics")
        
        self.CheckBox_metr = []
        layout = QVBoxLayout()
        
        counter = 0
        for mtr in metrics_available:
            self.CheckBox_metr.append(QCheckBox(mtr))
            layout.addWidget(self.CheckBox_metr[counter])
            counter = counter + 1


        self.CheckBox_metr[0].setChecked(True)
        self.metrics.setLayout(layout) 
        
        
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
        
    def clearTrackers(self):
        global trackers_paths
        self.listwidget.clear()
        self.trackers_res.clear()
        trackers_paths.clear()
        self.listwidget.repaint()
        self.update()
        
        
    def passEvaluatorConfig(self):
        #call callback for the evaluator
        self.update_global_current_state()
        print("Start Evaluation")
        
        global trackers_paths
        global trackers_extra
        global eval_type
        global sequences_final
        global challenges_final
        global metrics
        
#        ******************** Insert Frances function here
#        it should receive 6 parameters
#        example:
#        function(trackers_paths,trackers_extra,eval_type,sequences_final,challenges_final,metrics)
    
        
        return
    
    def update_global_current_state(self):
        global trackers_paths
        global trackers_extra
        global eval_type
        global sequences_final
        global challenges_final
        global metrics
        
#        trackers_paths done before
        
#        trackers_extra
        trackers_extra.clear()
        for tr in self.CheckBox_tr:
            if tr.isChecked():
                trackers_extra.append(tr.text())
                
#        eval_type 
        eval_type.clear();
        s = "sequence"
        if self.radioButton2.isChecked():
            s = "challenge"
        eval_type.append(s)
        
#        sequences_final
        sequences_final.clear()
        for tr in self.CheckBox_seq:
            if tr.isChecked():
                sequences_final.append(tr.text())
                
#        challenges_final
        challenges_final.clear()
        for ch in self.CheckBox_chall:
            if ch.isChecked():
                challenges_final.append(ch.text())
                
#        challenges_final
        metrics.clear()
        for mtr in self.CheckBox_metr:
            if mtr.isChecked():
                metrics.append(mtr.text())
        
#        print('*****************')
#        print(trackers_paths)
#        print(trackers_extra)
#        print(eval_type)
#        print(sequences_final)
#        print(challenges_final)
#        print(metrics)
#        print('*****************')
        
        

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    gallery = trackerApp()
    gallery.show()
    
    sys.exit(app.exec_()) 