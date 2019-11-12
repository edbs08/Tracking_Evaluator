# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 11:00:41 2019

@author: Frances
"""

from evaluation.data import *
from evaluation.metrics import *
from evaluation.visualization import *
import time

#data_path = 'C:\Users\Frances\Documents\UBr\TRDP\\ExampleDatasetandSequences'
##Save dataset to be used in directory of scripts labelled Dataset
data_path = 'C:/Users/Frances/Documents/UBr/TRDP/PythonCode/WorkingFolder/Dataset'

#Not sure if we should use other experiment types from VOT - could just make baseline the default
#and not have it as input to function
experiment = 'baseline'

#number of times to test on a sequence, as tracker may have been run multiple times
#can be read in from user as int or string whichever is easiest
sample_num = '1'
#sample_num = 1

# this is to assess dataset provided by user and produce list on the interface
#user can then select certain trackers/sequences they want to use? 
trackers, sequences = initialize_workspace(data_path)


#sequences = ['ants1', 'ball1', 'butterfly', 'tiger', 'fernando']
#sequences = ['ants1']
##some of these trackers also output polygons - ECO, UPDT
#trackers = ['ECO', 'UPDT', 'srdcf_deep']
## trackers outputting rectangles
#trackers = ['DSiam']
trackers = ['DLSTpp', 'DSiam', 'SiamFC', 'SiamVGG']
#trackers = ['Accuracy_tester']
data = load_data(data_path, sequences, trackers, experiment, sample_num)
challenges = ['overall', 'occlusion', 'camera_motion', 'motion_change', 'size_change', 'illum_change']

start = time.time()
AR_data = compute_AR(data, challenges)

end = time.time()

elapsed_time = end-start
print('Time taken for evaluation: ', elapsed_time)

for c in challenges:
    for t in trackers:
        print(t, c, 'Accuracy: ',  AR_data[c][t]['tracker_acc'])
        print(t, c, 'Robustness: ', AR_data[c][t]['tracker_robust'])
        print(t, c, 'Failure Count: ', AR_data[c][t]['tracker_failcount'])
        

basic_AR_plots(AR_data, challenges, trackers)    
        
        


