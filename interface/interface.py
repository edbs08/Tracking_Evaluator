# -*- coding: utf-8 -*-
"""
Visual video tracker evaluator 
    interface.py
    Creates the user's interface of the evaluator

@authors: 
    E Daniel Bravo S
    Frances Ryan
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QFileInfo
from PyQt5.QtGui import QPixmap
from evaluation.visualization import *

g_sequences = []
g_trackers = []

eval_options = ["Display Error Frames","Export to LaTex"]
chall_available = ["Overall","Camera Motion","Illumination Changes","Motion Change","Occlusion","Size change"]
metrics_available = ["Accuracy","Robustness","Precision(Center Location Error)"]

#final global outputs of interface
trackers_paths = [] 
trackers_results = []
eval_extras = []
eval_type = []
sequences_final = []
challenges_final = []
metrics = []

def interface_main(sequences,trackers):
    """
    Used for unit test of the interface module
    Args:
        sequences : list of sequences to include in the analysis
        trackers : list of trackers to include in the analysis
    """
    global g_sequences
    global g_trackers
    g_trackers = trackers
    g_sequences = sequences
    app = QApplication(sys.argv)
    track_app = trackerApp()
    track_app.show()
    track_app.exec_()


class trackerApp(QDialog):
    """
    Class to define the Evaluator widget 
    """
    def __init__(self, parent=None):
        super(trackerApp, self).__init__(parent)
        self.trackers_res=[]
        self.originalPalette = QApplication.palette()
        logo = QPixmap('./IPCV_logo.PNG')
        logo = logo.scaledToWidth(200)
        label_logo = QLabel()
        label_logo.setPixmap(logo)
        
        self.createSelectTrackers()
        self.createEvalOptions()
        self.createEvalType()
        self.createSequenceList()
        self.createChallengeList()
        self.createMetricsList()
        
        run_eval = QPushButton("Run")
        run_eval.clicked.connect(self.passEvaluatorConfig)
        
        scroll = QScrollArea()
        scroll.setWidget(self.sequences)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(300)
        
        scroll2 = QScrollArea()
        scroll2.setWidget(self.trackerList)
        scroll2.setWidgetResizable(True)
        scroll2.setFixedHeight(300)
        scroll2.setFixedWidth(200)
        
        mainLayout = QGridLayout()
        mainLayout.addWidget(label_logo,0,0)
        mainLayout.addWidget(scroll2,1,0)
        mainLayout.addWidget(self.evalOptions, 2, 0 )
        
        mainLayout.addWidget(self.evalType, 0, 1,1,2 )
        mainLayout.addWidget(scroll, 1,1 )
        mainLayout.addWidget(self.challenges, 1,2 )
        mainLayout.addWidget(self.metrics, 2,1 )
        mainLayout.addWidget(run_eval,2,2)
        self.setLayout(mainLayout)
        
    def createLoadFiles(self):
        """ 
        Used to load results files in white box
        """
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
        """ 
        Load files from directory 
        """
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
        """ 
        Create the tracker list box 
        """
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
        
    def createEvalOptions(self):
        """
        List the evaluation options
        """
        self.evalOptions = QGroupBox("Select Evaluation Extras")
        
        self.CheckBox_eval_op = []
        layout = QVBoxLayout()
        counter = 0
        for ch in eval_options:
            self.CheckBox_eval_op.append(QCheckBox(ch))
            layout.addWidget(self.CheckBox_eval_op[counter])
            counter = counter + 1

        self.evalOptions.setLayout(layout) 
        
        
    def createEvalType(self):
        """ 
        List evaluation type options
        """
        self.evalType = QGroupBox("Define type of Results")
        
        self.radioButton1 = QRadioButton("Per sequence")
        self.radioButton1.setChecked(True)
        self.radioButton2 = QRadioButton("Per challenge")
        
        self.radioButton1.toggled.connect(self.check_eval_type)

        layout = QVBoxLayout()
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)
        self.evalType.setLayout(layout) 
        
    def createSequenceList(self):
        """
        List the sequences available for analysis
        """
        self.sequences = QGroupBox("Sequences available")
        
        layout = QVBoxLayout()
        counter = 0
        self.CheckBox_seq = []
        self.CheckBox_seq.append(QCheckBox("- Select/Remove all -"))
        for seq in g_sequences:
            self.CheckBox_seq.append(QCheckBox(seq))
            layout.addWidget(self.CheckBox_seq[counter])
            counter = counter + 1
            
        if len(self.CheckBox_seq) > 2:
            self.CheckBox_seq[1].setChecked(True)
            
            
        self.CheckBox_seq[0].toggled.connect(self.selectAllSeq)
        
        self.sequences.setLayout(layout) 
    
    def selectAllSeq(self):
        """
        Method to select all options available
        """
        flag = False
        if self.CheckBox_seq[0].isChecked():
            flag = True
        
        for i in self.CheckBox_seq:
            i.setChecked(flag)
            
        
    def createChallengeList(self):
        """
        List challenges available
        """
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
        """
        List the metrics available for analysis
        """
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
        """
        Limit options available depending on the evaluation type
        - Functionality currently not active
        """
#        if (self.radioButton2.isChecked()):
#             self.sequences.setEnabled(False)
#        else:
#            self.sequences.setEnabled(True)
#            
#        if (self.radioButton1.isChecked()):
#             self.challenges.setEnabled(False)
#        else:
#            self.challenges.setEnabled(True)
#        
#        self.update()
        return
        
    def clearTrackers(self):
        """
        Clear trackers in selection box
        """
        global trackers_paths
        self.listwidget.clear()
        self.trackers_res.clear()
        trackers_paths.clear()
        self.listwidget.repaint()
        self.update()
        
        
    def passEvaluatorConfig(self):
        """
        Function to comunicate with the evaluation module
        Pass the configuration acquired by the interface
        """
        #call callback for the evaluator
        self.update_global_current_state()
        print("Start Evaluation")
        
        global trackers_results
        global eval_extras
        global eval_type
        global sequences_final
        global challenges_final
        global metrics
        
        perform_analysis(trackers_results,eval_extras,eval_type,sequences_final,challenges_final,metrics)
        
        return
    
    def update_global_current_state(self):
        """
        Update global variables for sending to evaluator
        """
        global trackers_results
        global eval_extras
        global eval_type
        global sequences_final
        global challenges_final
        global metrics
        
        
#        trackers_results
        trackers_results.clear()
        for tr in self.CheckBox_tr:
            if tr.isChecked():
                trackers_results.append(tr.text())

#       eval_extras
        eval_extras.clear()
        for ev_ext in self.CheckBox_eval_op:
            if ev_ext.isChecked():
                eval_extras.append(ev_ext.text())
                
#        eval_type 
        eval_type.clear();
        s = "sequence"
        if self.radioButton2.isChecked():
            s = "challenge"
        eval_type.append(s)
        
#        sequences_final
        sequences_final.clear()
        self.CheckBox_seq.pop(0) #Remove the "select all" item
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
        
        """Uncomment for verbose"""
#        print('*****************')
#        print(trackers_results)
#        print(eval_extras)
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