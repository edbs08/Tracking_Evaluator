# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 08:25:17 2019

@author: Frances
"""

import numpy as np
import os.path



def initialize_workspace(data_path):
    #This function is to take the data from the dataset that the user provides
    #so once we read in file we check what trackers and sequences are available to compare/use

    trackers = os.listdir(data_path + '/trackers')
    sequences = os.listdir(data_path + '/sequences')
    
    return trackers, sequences
    
    
    
def load_data(data_path, sequences, trackers, experiment_name, sample_number):
    #This function needs to retrieve the correct output data from the tracker for a sequence
    #It also needs to retrieve the ground truth data and output it in a reasonable format    
    exists = os.path.isdir(data_path)
    if not exists:
        print("Invalid Data Path")
    

    data = {}

    for t in trackers:
        data[t] = {}
        for s in sequences:
            filename = s + '_00' + str(sample_number) + '.txt'
            gt_name = '\groundtruth.txt'
            output_path = os.path.join(data_path, 'trackers', t, experiment_name, s, filename)
            gt_path = os.path.join(data_path, 'sequences', s)
             
            output = []
            with open(output_path, "r") as filestream:
                for line in filestream:
                    currentline = line.split(",")
                    currentline = [float(i) for i in currentline]
                    output.append(currentline)        
            output = np.array(output)
            
            groundtruth = []
            with open(gt_path + gt_name, "r") as filestream: 
                for line in filestream:
                    currentline = line.split(",")
                    currentline = [float(i) for i in currentline]
                    groundtruth.append(currentline)
            groundtruth = np.array(groundtruth)
            
            cm = 0
            ic = 0
            mc = 0
            occ = 0
            sc = 0
            if os.path.isfile(gt_path + '\camera_motion.tag'):
                cm = np.loadtxt(gt_path + '\camera_motion.tag').astype(np.int)
            if os.path.isfile(gt_path +'\illum_change.tag'):
                ic = np.loadtxt(gt_path + '\illum_change.tag').astype(np.int)
            if os.path.isfile(gt_path +'\motion_change.tag'): 
                mc = np.loadtxt(gt_path + '\motion_change.tag').astype(np.int)
            if os.path.isfile(gt_path +'\occlusion.tag'): 
                occ = np.loadtxt(gt_path + '\occlusion.tag').astype(np.int)
            if os.path.isfile(gt_path +'\size_change.tag'): 
                sc = np.loadtxt(gt_path + '\size_change.tag').astype(np.int)  

            data[t][s] = { 'output': output, 'groundtruth': groundtruth,  'camera_motion': cm, 
                        'illum_change' : ic, 'motion_change': mc, 'occlusion' : occ, 'size_change' : sc}
    
    
    ##Test prints
    ##So accessing is data[tracker][sequence]['Key']([x][y] for individual values in the groundtruth or output
    print(data['DSiam']['ants1']['output'][3][3])
    print(data['ECO']['butterfly']['groundtruth'][0])
    
    return data



     