# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:52:26 2019

@author: Frances
"""


import matplotlib.pyplot as plt
import numpy as np
import os
from evaluation.data import *
from evaluation.metrics import *
from evaluation.report import *
import dominate
from dominate import tags
from dominate.tags import *

markers = ['o', '+', 'x', '^', '.', ',', 'v',  '<', '>', 's', 'd']
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
plot_list = []
trackers = []
sequences = []
challenges = []
metrics = []
eval_type = []

def perform_analysis(tracks,eval_extras,eval_method,seqs,challs,mets):
    """Calls all analysis functions allows running of analysis from interface
    
    Args:
        data_path (path): path to directory containing sequences and trackers
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    """
    global trackers
    global sequences
    global challenges
    global metrics
    global eval_type
    data_path = os.getcwd()
    data_path = 'C:/Users/Frances/Documents/UBr/TRDP/PythonCode/WorkingFolder/'
    experiment = 'baseline'
    sample_num = '1'

    trackers = tracks
    sequences = seqs
    challenges = challs
    metrics = mets
    eval_type = eval_method
    
    if eval_type == ['sequence'] and len(sequences) > 10:
        sequenceMessage()
        return
    
    data = load_data(data_path, sequences, trackers, experiment, sample_num)
    
    if data == None:
        dataMessage()
        return
    
    AR_data = compute_ar_and_precision(data, challenges, metrics)
    
    if 'Accuracy' in metrics and 'Robustness' in metrics:
        basic_ar_plots(AR_data)
    else:
        print('Accuracy/Robustness plots not possible with selected metrics')
    if 'Accuracy' in metrics:
        accuracy_plots(AR_data)
    if 'Robustness' in metrics:
        robustness_plots(AR_data)
    if 'Precision(Center Location Error)' in metrics:
        cle_plots(AR_data)
        
    create_report('Analysis Report', AR_data, metrics)
    visualization_html('Analysis Report', AR_data, metrics)
    
    print('Evaluation Complete!')   
    
    return AR_data
    
def basic_ar_plots(data):
    """ Creates accuracy robustness plots
    
    Args:
        data (dictionary): dictionary containing output from metrics calculation should include accuracy and robustness metrics
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
    """
    for c in challenges:
        i = 0
        for t in trackers:
            accuracy = (data[c][t]['tracker_acc'])
            robustness = (data[c][t]['tracker_robust'])
            marker = (markers[i])
            i = i+1
            plt.plot(robustness, accuracy, marker, markersize = 8, label = t)
        plt.xlabel('Robustness')
        plt.xlim([0,1.1])
        plt.ylabel('Accuracy') 
        plt.ylim([0,1.1]) 
        plt.title('AR_%s'%c)
        plt.legend()
        plt.grid(b=True, which='major', linestyle='-')
        plt.xticks(np.arange(0,1.2,0.2))
        plt.yticks(np.arange(0,1.2,0.1))
        filename = "AR_%s.png" %c
        plot_list.append(filename)
        plt.savefig(filename)
        plt.close()
    
    return

def robustness_plots(data):
    """ Draws plots of total fail count for each challenge
    
    Args:
        data (dictionary): dictionary containing output from metrics calculation should include robustness metrics
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    
    """
    i = 0
    for t in trackers:
        challenges = data.keys()
        failcount = []
        for c in challenges:
            failcount.append(data[c][t]['tracker_failcount'])
          # failcount = data[c][t]['tracker_failcount']
        plt.plot(challenges, failcount, '--', color = colors[i], marker = markers[i], markersize = 8,  label = t)
           #plt.plot(c, failcount, label = t)
        i = i+1
    plt.legend()
    plt.xlabel('Challenge')
    plt.ylabel('Total failures')
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    filename = "Failcount.png"
    plot_list.append(filename)
    fig.savefig(filename)
    plt.close()
    
def accuracy_plots(data):

    i = 0
    for t in trackers:
        j = 0
        if eval_type == ['sequence']:
            for c in challenges:
                accuracy = []
                sequences_inc = []    
                for s in sequences:
                    if s in data[c][t].keys():
                        accuracy.append(data[c][t][s]['sequence_acc'])
                        sequences_inc.append(s)
                plt.scatter(sequences_inc, accuracy, marker = markers[j], color = colors[i], s = 100, label = t + ":" + c)
                j += 1
        elif eval_type == ['challenge']:
            accuracy = []
            for c in challenges:
                accuracy.append(data[c][t]['tracker_acc'])
            plt.scatter(challenges, accuracy, marker = markers[i], s = 100, label = t )
        i += 1
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.xlabel(eval_type[0])
    plt.ylabel('Accuracy')
    fig = plt.gcf()
    fig.set_size_inches(22.5, 10.5)
    filename = "Accuracy.png"
    fig.savefig(filename)
    plt.close()
    
def cle_plots(data):
    """Draws plots of center location error
    
    Args:
        data (dictionary): dictionary containing output from metrics calculation should include robustness metrics
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    """
    width = 1/(len(trackers)+1)
    pos = np.arange(len(challenges))
    for t in trackers:
        cle = []
        for c in challenges:
                cle.append(data[c][t]['tracker_precision'])
        plt.barh(pos, cle, width, label = t)
        pos = pos + width
    plt.yticks([r + width for r in range(len(pos))], challenges)
    plt.legend()
    plt.xlabel('Center Location Error')
    plt.ylabel('Challenge')
    fig = plt.gcf()
    fig.set_size_inches(15, 10.5)
    filename = "Precision.png"
    plot_list.append(filename)
    plt.savefig(filename)
    plt.close()


def visualization_html(header, data, metrics):
    challenges = data.keys()
    
#    geometry_options = {
#        "margin": "1.5in",
#        "headheight": "20pt",
#        "headsep": "10pt",
#        "includeheadfoot": True
#    }
#    doc = Document(header, page_numbers=True, geometry_options=geometry_options)
    doc1 = dominate.document(title='Tracking Evaluator')

    with doc1:
        with div():
            attr(cls='body')
            h1('Evaluation Results')
        with div():
            h2('Results table')
            tags.style(".calendar_table{width:880px;}")
            tags.style("body{font-family:Helvetica}")
            tags.style("h1{font-size:x-large}")
            tags.style("h2{font-size:large}")
            tags.style("table{border-collapse:collapse}")
            tags.style("th{font-size:small;border:1px solid gray;padding:4px;background-color:#DDD}")
            tags.style("td{font-size:small;text-align:center;border:1px solid gray;padding:4px}")
            with tags.table():
                with tags.thead():
                    tags.th("Challenge", style = "color:#ffffff;background-color:#6A75F2")
                    tags.th("Tracker", style = "color:#ffffff;background-color:#6A75F2")
                    for m in metrics:
                        tags.th(m, style = "color:#ffffff;background-color:#6A75F2")
    
                with tags.tbody():
                    for c in challenges:
                        with tags.tr(): #New row Challenges
                            tags.td(c, style = "font-size:small;text-align:center;padding:4px")
                        for t in data[c].keys():
                            with tags.tr(): #New row Data per tracker
                                tags.td(' ', style = "font-size:small;text-align:center;padding:4px")
                                tags.td(t, style = "font-size:small;text-align:center;padding:4px")
                                if 'Accuracy' in metrics:
                                    tags.td(data[c][t]['tracker_acc'], style = "font-size:small;text-align:center;padding:4px")
                                if 'Robustness' in metrics:
                                    tags.td(data[c][t]['tracker_robust'], style = "font-size:small;text-align:center;padding:4px")
                                if 'Precision(Center Location Error)' in metrics:
                                    tags.td(data[c][t]['tracker_precision'], style = "font-size:small;text-align:center;padding:4px")
        with div():
            h2('Graphs')
            for graph in plot_list:
                tags.img(src=graph,style='max-width:700px;margin-top: 50px;')
                tags.br()

    f= open(os.getcwd()+'/evaluation_results'+'.html', 'w')
    f.write(doc1.render())
    f.close()
    print(doc1.render())
    
class sequenceMessage(QWidget):
    """Class created to allow message to user if too many sequences selected.
    """
    def __init__(self):
        super().__init__()
        self.title = 'PyQT5 Message Box'
        self.left = 300
        self.top = 300
        self.width = 320
        self.height = 200
        self.sequence_limit()
        
        
    def sequence_limit(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        choice = QMessageBox.question(self, 'Message:',  "Please select up to 8 sequences for by sequence report.", QMessageBox.Ok)
        if choice == QMessageBox.Ok:
            return
        else:
            sys.exit()
        self.exec()

class dataMessage(QWidget):
    """Class created to allow message to user if too many sequences selected.
    """
    def __init__(self):
        super().__init__()
        self.title = 'PyQT5 Message Box'
        self.left = 300
        self.top = 300
        self.width = 320
        self.height = 200
        self.data_empty()
        
        
    def data_empty(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        choice = QMessageBox.question(self, 'Message:',  "No data for selected tracker-sequence combination, please make another selection", QMessageBox.Ok)
        if choice == QMessageBox.Ok:
            return
        else:
            sys.exit()
        self.exec()

    
    

    

    
        
    
    

            
            