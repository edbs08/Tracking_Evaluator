# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:52:26 2019

@author: Frances
"""


import matplotlib.pyplot as plt
import numpy as np
from evaluation.data import *
from evaluation.metrics import *
from evaluation.report import *

def perform_analysis(data_path, trackers, sequences,challenges, metrics):
    """Calls all analysis functions allows running of analysis from interface
    
    Args:
        data_path (path): path to directory containing sequences and trackers
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    """
    experiment = 'baseline'
    sample_num = '1'
    
    data = load_data(data_path, sequences, trackers, experiment, sample_num)
    
    AR_data = compute_ar_and_precision(data, challenges, metrics)
    
    if 'Accuracy' and 'Robustness' in metrics:
        basic_ar_plots(AR_data, challenges, trackers)
    else:
        print('Accuracy/Robustness plots not possible with selected metrics')
    if 'Robustness' in metrics:
        robustness_plots(AR_data, challenges, trackers, sequences)
    if 'Precision(Center Location Error)' in metrics:
        cle_plots(AR_data, challenges, trackers, sequences)
        
    create_report('Analysis Report', AR_data, metrics)
    
    print('Evaluation Complete!')   
    
    return AR_data
    
def basic_ar_plots(data, challenges, trackers):
    """ Creates accuracy robustness plots
    
    Args:
        data (dictionary): dictionary containing output from metrics calculation should include accuracy and robustness metrics
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
    """
    markers = ['o', '+', 'x', '^', '.', ',', 'v',  '<', '>', 's', 'd']
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
        plt.savefig(filename)
        plt.close()
    
    return

def robustness_plots(data, challenges, trackers, sequences):
    """ Draws plots of total fail count for each challenge
    
    Args:
        data (dictionary): dictionary containing output from metrics calculation should include robustness metrics
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    
    """
    markers = ['o', '+', 'x', '^', '.', ',', 'v',  '<', '>', 's', 'd']
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
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
    fig.savefig(filename)
    plt.close()
    
def cle_plots(data, challenges, trackers, sequences):
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
    plt.savefig(filename)
    plt.close()


    

    
        
    
    

            
            