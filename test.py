
"""
Created on Sat Oct 19 11:00:41 2019

@author: Frances
"""

from evaluation.data import *
from evaluation.metrics import *
from evaluation.visualization import *
from evaluation.report import *
from evaluation.verification import *
import time
import numpy as np
#data_path = 'C:\Users\Frances\Documents\UBr\TRDP\\ExampleDatasetandSequences'
##Save dataset to be used in directory of scripts labelled Dataset
data_path = os.getcwd()

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

#sequences = ['carDark', 'car4', 'david', 'david2', 'sylvester']
sequences = ['ants1', 'ball1', 'butterfly', 'tiger', 'fernando']
#sequences = ['bag', 'fish1', 'graduate', 'matrix', 'singer2']
#sequences = ['zebrafish1']
##some of these trackers also output polygons - ECO, UPDT
trackers = ['ECO', 'UPDT', 'srdcf_deep']
## trackers outputting rectangles
#trackers = ['ECO', 'UPDT', 'DSiam', 'DLSTpp','SiamVGG']
#trackers = ['DLSTpp', 'DSiam', 'SiamFC', 'SiamVGG']
#trackers = ['VR','TM','RS','PD','MS']
#trackers = ['Accuracy_tester']
#data = load_data(data_path, sequences, trackers, experiment, sample_num)
#challenges = ["Camera Motion","Illumination Changes","Motion Change","Occlusion","Size change"]
challenges = ["Overall", "Camera Motion"]
metrics = ["Accuracy","Robustness","Precision(Center Location Error)"]

start = time.time()

eval_extras = []
eval_type = ['challenge']
#download_VOT(data_path, '2015')
#perform_Analysis(data_path, sequences, trackers, challenges)
AR_data =perform_analysis(trackers,eval_extras,eval_type,sequences,challenges,metrics)
#AR_data = compute_ar_and_precision(data, challenges, metrics)
#
#if 'Accuracy' and 'Robustness' in metrics:
#    basic_ar_plots(AR_data, challenges, trackers)
#else:
#    print('Accuracy/Robustness plots not possible with selected metrics')
#if 'Robustness' in metrics:
#    robustness_plots(AR_data, challenges, trackers, sequences)
#if 'Precision(Center Location Error)' in metrics:
#    cle_plots(AR_data, challenges, trackers, sequences)
#    
#    
#create_report('example', AR_data)

calculation= ['acc_per_frame']

#verify_data(AR_data, trackers, sequences, calculation)
print('Evaluation Complete!')  
end = time.time()

elapsed_time = end-start
print('Time taken for evaluation: ', elapsed_time)

#for c in challenges:
#    for t in trackers:
#        print(t, c, 'Accuracy: ',  AR_data[c][t]['tracker_acc'])
#        print(t, c, 'Robustness: ', AR_data[c][t]['tracker_robust'])
#        print(t, c, 'Failure Count: ', AR_data[c][t]['tracker_failcount'])

#file2write=open("precision_VR.txt",'w')
#for i in AR_data['Overall']['VR']['carDark']['precision_per_frame']:
#    file2write.write(str(i[0]) + '\n')
#file2write.close()

#basic_AR_plots(AR_data, challenges, trackers)
        
        


