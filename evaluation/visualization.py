# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:52:26 2019

@author: Frances
"""


import matplotlib.pyplot as plt
import numpy as np
import os, shutil
import cv2
from evaluation.data import *
from evaluation.metrics import *
from evaluation.report import *
import dominate
from dominate import tags
from dominate.tags import *

markers = ['o', '+', 'x', '^', '.', ',', 'v',  '<', '>', 's', 'd']
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
plot_list = []
frame_list = {}

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
    #data_path = 'C:/Users/Frances/Documents/UBr/TRDP/PythonCode/WorkingFolder/'
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
    
    AR_data = compute_ar_and_precision(data, challenges, sequences, trackers, eval_extras, metrics)
    
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
    
    if "Export to LaTex" in eval_extras:
        create_report("Analysis Report", AR_data, metrics)
    
    if "Display Error Frames" in eval_extras:
        display_low_frames(AR_data, data)
    
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
    for c in data.keys():
        i = 0
        if data[c]:
            for t in data[c].keys():
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
        failcount = []
        j = 0
        if eval_type == ['sequence']:
            for c in challenges:
                if data[c]:
                    if data[c][t]:
                        failcount = []
                        sequences_inc = []
                        for s in sequences:
                            if s in data[c][t].keys():
                                failcount.append(data[c][t][s]['failures_per_sequence'])
                                sequences_inc.append(s)
                        if len(sequences_inc) > 0:
                            plt.scatter(sequences_inc, failcount, color = colors[i], marker = markers[j], s = 200,  label = t + ':' + c)
                        else:
                            print('Insufficient data for robustness plots with selection')
                        j = j + 1
        elif eval_type == ['challenge']:
            challs = []
            for c in challenges:
                if data[c]:
                    if data[c][t]:
                        challs.append(c)
                        failcount.append(data[c][t]['tracker_failrate'])
                  # failcount = data[c][t]['tracker_failcount']
            if len(challs) > 0:
                plt.plot(challs, failcount, '--', color = colors[i], marker = markers[i], markersize = 10,  label = t)
            else:
                print("Insufficient data for robustness plots with selection")
                return
           #plt.plot(c, failcount, label = t)
        i = i+1
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.xlabel(eval_type[0])
    plt.ylabel('Failure Rate')
    plt.grid(b=True, which='major', linestyle='-')
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    filename = "Failure Rate.png"
    fig.savefig(filename)
    plot_list.append(filename)
    plt.close()
    
def accuracy_plots(data):

    i = 0
    for t in trackers:
        if eval_type == ['sequence']:
            j = 0
            for c in challenges:
                if data[c]:
                    if data[c][t]:
                        accuracy = []
                        sequences_inc = []    
                        for s in sequences:
                            if s in data[c][t].keys():
                                accuracy.append(data[c][t][s]['sequence_acc'])
                                sequences_inc.append(s)
                        if len(sequences_inc) > 0:
                            plt.scatter(sequences_inc, accuracy, marker = markers[j], color = colors[i], s = 200, label = t + ":" + c)
                        else:
                            print('Insufficient data for accuracy plots with selection')
                        j += 1
        elif eval_type == ['challenge']:
            accuracy = []
            challs = []
            for c in challenges:
                if data[c]:
                    if data[c][t]:
                        challs.append(c);
                        accuracy.append(data[c][t]['tracker_acc'])
            if len(challs) > 0:
                plt.scatter(challs, accuracy, marker = markers[i], s = 200, label = t )
            else:
                print("Insufficient data for accuracy plots with selection")
                return
        i += 1
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.xlabel(eval_type[0])
    plt.ylabel('Accuracy')
    plt.grid(b=True, which='major', linestyle='-')
    plt.title('Average Overlap')
    fig = plt.gcf()
    fig.set_size_inches(22.5, 10.5)
    filename = "Accuracy.png"
    plot_list.append(filename)
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
    
    width = min(0.2, 1/(len(trackers)+1))  
    valid = 0
    if eval_type == ['sequence']:
        pos = np.arange(len(sequences))
#        pos = pos_s
        for c in challenges:
                if data[c]:
#                    width = 0
                    for t in trackers:
                        cle = []
                        if data[c][t]:
                            sequences_inc = []
                            for s in sequences:
                                    if s in data[c][t].keys():
                                        valid = 1
                                        cle.append(data[c][t][s]['sequence_precision'])
#                                        sequences_inc.append(s)
                                    else:
                                        cle.append(0)
#                            if len(sequences_inc) > 0:
#                                pos = np.arange(len(sequences_inc))+width
                            plt.barh(pos, cle, width, label = t)
                            pos = pos + width
#                            labels = sequences_inc
                    if valid == 1:
                        plt.yticks([r + width for r in range(len(pos))], sequences)
                        plt.legend()
                        plt.xlabel('Center Location Error')
                        plt.ylabel('Sequence')
                        plt.title('Precision for Challenge: %s'%c)
                        fig = plt.gcf()
                        fig.set_size_inches(15, 10.5)
                        filename = "Precision%s.png"%c
                        plot_list.append(filename)
                        plt.savefig(filename)
                        plt.close()
        if valid == 0:
            print('Insufficient data for Precision plots')
            return
    elif eval_type == ['challenge']:
#        width = 0
        pos = np.arange(len(challenges))
        for t in trackers:
            cle = []
            challs = []
            for c in challenges:
                if data[c]:
                    if data[c][t]:
                        cle.append(data[c][t]['tracker_precision'])
                        valid = 1
#                        challs.append(c)
                    else:
                        cle.append(0)
                
#                pos = np.arange(len(challens)) + width
            plt.barh(pos, cle, width, label = t)
            pos = pos + width
#                labels = challs
    if valid == 1:
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
    else:
        print('Insufficient data for Precision Plots')
        return


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
                        for t in trackers:
                            if data[c][t]:
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
                
        if frame_list:
                for c in challenges:
                    if frame_list[c]:
                        for t in frame_list[c].keys():
                            with figure():
                                h3('Low Frames for tracker: %s'%t + ' challenge: %s'%c)
                                for i in range(len(frame_list[c][t])):
                                    tags.img(src = frame_list[c][t][i][0], style="width:340px;margin-top: 50px")
                                    tags.i(frame_list[c][t][i][1])
                                
            

    f= open(os.getcwd()+'/evaluation_results'+'.html', 'w')
    f.write(doc1.render())
    f.close()
#    print(doc1.render())
    
def display_low_frames(AR_data, data):
    if os.path.isdir('low frames'):
       shutil.rmtree('low frames') 
    os.mkdir('low frames')
    
    for c in AR_data.keys():
        if AR_data[c]:
            frame_list[c] = {}
            for t in AR_data[c].keys():
                fig = []
                for i in range(len(AR_data[c][t]['min_acc_frames'])):
                    fig_name = '00000000'
                    s = AR_data[c][t]['min_acc_frames'][i][2]
                    idx = AR_data[c][t]['min_acc_frames'][i][1]
                    fig_path = os.path.join('sequences',s,'color')
                    if os.path.isdir(fig_path):
                        frame_num = str(AR_data[c][t]['min_acc_frames'][i][1] + 1)
                        fig_length = len(frame_num)
                        fig_name = fig_name[fig_length:] + frame_num + '.jpg'
                        fig_path = os.path.join(fig_path, fig_name)
                        
                        gt = data[t][s]['groundtruth'][idx]
                        result = data[t][s]['output'][idx]
                        
                        fig_name = '%s_'%c + '%s_'%t + '%s_'%s + '%s.jpg'%frame_num
                        img = draw_bbox_fig(fig_name, fig_path, gt, result)
                        cv2.imwrite(os.path.join('low frames',fig_name), img)
                        
                        fig.append(tuple((os.path.join('low frames',fig_name), '%s_'%s + '%s'%frame_num)))
                frame_list[c][t] = fig
            
def draw_bbox_fig(fig_name,fig_path, gt, result):
    
    img = cv2.imread(fig_path)
    
    if len(gt) > 4:
        gt_pts = np.array([[gt[0], gt[1]], [gt[2], gt[3]],[gt[4], gt[5]],[gt[6], gt[7]]], np.int32)
        cv2.polylines(img, [gt_pts],  True, (0,255,0), 2)
    else: 
        
        cv2.rectangle(img, (int(gt[0]), int(gt[1])), (int(gt[0]) + int(gt[2]),
                            int(gt[1])+int(gt[3])), (0,255,0), 2)
    if len(result) > 4:
        result_pts = np.array([[result[0], result[1]], [result[2], result[3]],[result[4], result[5]],
                           [result[6], result[7]]], np.int32)
        cv2.polylines(img, [result_pts],  True, (255,0,0), 2)
    else:
        cv2.rectangle(img, (int(result[0]), int(result[1])), (int(result[0]) + int(result[2]),
                            int(result[1])+int(result[3])), (255,0,0), 2)
        
    return img
    
    
    
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
        choice = QMessageBox.question(self, 'Message:',  "Please select up to 10 sequences for by sequence report.", QMessageBox.Ok)
        if choice == QMessageBox.Ok:
            return
        else:
            sys.exit()
        self.exec()

class dataMessage(QWidget):
    """Class created to allow message to user if not enough data with selected options.
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

    
    

    

    
        
    
    

            
            