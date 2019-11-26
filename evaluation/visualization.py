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
import dominate
from dominate import tags
from dominate.tags import *

plot_list = []

def perform_analysis(trackers,eval_extras,eval_type,sequences,challenges,metrics):
    """Calls all analysis functions allows running of analysis from interface
    
    Args:
        data_path (path): path to directory containing sequences and trackers
        challenges(list): list of strings, challenges to include
        trackers(list): list of strings, trackers to be compared
        sequences(list): list of strings, sequences to include
    """
    data_path =  os.getcwd()
    #'C:/Users/Frances/Documents/UBr/TRDP/PythonCode/WorkingFolder/Dataset'
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
    visualization_html('Analysis Report', AR_data, metrics)
    
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
        plot_list.append(filename)
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
    plot_list.append(filename)
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
    
    

    

    
        
    
    

            
            