# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:52:26 2019

@author: Frances
"""


import matplotlib.pyplot as plt
import numpy as np

def basic_AR_plots(data, challenges, trackers):
    markers = ['o', '+', 'x', '^', '.', ',', 'v',  '<', '>', 's', 'd']
    for c in challenges:
        i = 0
        for t in trackers:
            accuracy = (data[c][t]['tracker_acc'])
            robustness = (data[c][t]['tracker_robust'])
            marker = (markers[i])
            i = i+1
            plt.plot(robustness, accuracy, marker, label = t)
        plt.xlabel('Robustness')
        plt.xlim([0,1])
        plt.ylabel('Accuracy')  
        plt.ylim([0,1])
        plt.legend()
        plt.grid(b=True, which='major', linestyle='-')
        plt.xticks(np.arange(0,1,0.2))
        plt.yticks(np.arange(0,1,0.1))
        filename = "%s.png" %c
        plt.savefig(filename)
        plt.clf()
    
    return
            
            
            