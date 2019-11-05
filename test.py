# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 11:00:41 2019

@author: Frances
"""

from evaluation.data import *
from evaluation.metrics import *

#data_path = 'C:\Users\Frances\Documents\UBr\TRDP\\ExampleDatasetandSequences'
##Save dataset to be used in directory of scripts labelled Dataset
data_path = 'Dataset'

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


sequences = ['ants1', 'ball1', 'butterfly']
trackers = ['DSiam', 'ECO']
data = load_data(data_path, sequences, trackers, experiment, sample_num)

accuracy_data = compute_accuracy(data, 'overall')



