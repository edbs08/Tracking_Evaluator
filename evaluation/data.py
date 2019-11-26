# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 08:25:17 2019

@author: Frances
"""
import wget
import os
import json
import zipfile
from PyQt5.QtWidgets import QMessageBox, QWidget
import numpy as np
import os.path
import sys

def initialize_workspace(data_path):
    #This is a function only required for easy testing remove for final versions!!

    trackers = os.listdir(data_path + '/trackers')
    sequences = os.listdir(data_path + '/sequences')
    
    return trackers, sequences
      
def load_data(data_path, sequences, trackers, experiment_name, sample_number):
    """This function needs retrieves the correct output data from the tracker for a sequence
    
    Args:
        data_path (path): path to data i.e where sequences and trackers folder is
        sequences (list): list of strings of sequences to be included
        trackers (list): list of strings of trackers to be included
        experiment_name (string): required for VOT data but currently only default - baseline
        sample_number (string): required for VOT data but currently only default - 1
        
    Returns: Dictionary of dictionaries containing results for each tracker and groundtruth for each sequence along with tags
    """
    exists = os.path.isdir(data_path)
    if not exists:
        print("Invalid Data Path")
    

    data = {}
    valid = False

    for t in trackers:
        data[t] = {}
        for s in sequences:
            filename = s + '_00' + str(sample_number) + '.txt'
            gt_name = '\groundtruth.txt'
            output_path = os.path.join(data_path, 'trackers', t, experiment_name, s, filename)
            
            if os.path.isfile(output_path):
                gt_path = os.path.join(data_path, 'sequences', s)
                output = []
                with open(output_path, "r") as filestream:
                    for line in filestream:
                        currentline = line.split(",")
#                        currentline = line.split("\t")
                        currentline = [float(i) for i in currentline]
                        output.append(currentline)        
                output = np.array(output)
                
                groundtruth = []
                with open(gt_path + gt_name, "r") as filestream: 
                    for line in filestream:
                        currentline = line.split(",")
#                        currentline = line.split("\t")
                        currentline = [float(i) for i in currentline]
                        groundtruth.append(currentline)
                groundtruth = np.array(groundtruth)
                
                cm = np.zeros(len(groundtruth))
                ic = np.zeros(len(groundtruth))
                mc = np.zeros(len(groundtruth))
                occ = np.zeros(len(groundtruth))
                sc = np.zeros(len(groundtruth))
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
                
            

                data[t][s] = { 'output': output, 'groundtruth': groundtruth,  'Camera Motion': cm, 
                            'Illumination Changes' : ic, 'Motion Change': mc, 'Occlusion' : occ, 'Size change' : sc}
            else:
                print('No output data for tracker:', t, 'sequence: ', s)
                
        if data[t]:
            valid = True
    if valid == True:
        return data
    else:
        return None


def download_VOT(data_path, version):
    """ Script to download VOT sequences
    
    Args:
        data_path (path): where to store  data
        version (string): what version of VOT sequences to download
    """
    if version == '2013' or version == '2014' or version == '2015':
        url = 'http://data.votchallenge.net/vot%s/dataset/' %version
        bundle_url = os.path.join(url, 'description.json')
    if version == '2016' or version == '2017' or version == '2018' or version == '2019':
        url = 'http://data.votchallenge.net/vot%s/main/' %version
        bundle_url = os.path.join(url, 'description.json')
    
    
    sequence_path = os.path.join(data_path, 'sequences%s'%version)
    if os.path.isdir(sequence_path):
        items = os.listdir(sequence_path)
        if len(items) > 0:
            downloadMessage()
    if not os.path.isdir(sequence_path):
        os.mkdir(sequence_path)
    bundle_file = 'description%s.json'%version
    bundle_loc = os.path.join(data_path, bundle_file)
    if not os.path.isfile(bundle_loc):
        wget.download(bundle_url, bundle_file)

    with open(bundle_file) as f:
            bundle = json.load(f)
    
    seq_names = []
    for seq in bundle['sequences']:
            seq_name = seq['name']
            seq_names.append(seq_name)    
            channels = seq['channels'].keys()
            
            seq_files = [] 
            for cn in channels:
                seq_url = seq['channels'][cn]['url']
                seq_url = bundle['homepage'] + seq_url[seq_url.find('sequence'):]
                seq_file = os.path.join(sequence_path,'{}_{}.zip'.format(seq_name, cn))
                wget.download(seq_url, seq_file)
                seq_files.append(seq_file)
                
            
            anno_url = url + '%s.zip' % seq_name 
            anno_file = os.path.join(sequence_path, seq_name + '_anno.zip')  
            wget.download(anno_url, anno_file)
            
            seq_dir = os.path.join(sequence_path, seq_name)
            
            img_dir = os.path.join(seq_dir, 'color')
            for seq_file in seq_files:
                os.makedirs(seq_dir)
                os.makedirs(img_dir)
                with zipfile.ZipFile(seq_file) as z:
                    z.extractall(img_dir)
            with zipfile.ZipFile(anno_file) as z:
                z.extractall(seq_dir)
                
class downloadMessage(QWidget):
    """Class created to allow warning message to user if sequences already downloaded.
    """
    def __init__(self):
        super().__init__()
        self.title = 'PyQT5 Message Box'
        self.left = 300
        self.top = 300
        self.width = 320
        self.height = 200
        self.download_check()
        
        
    def download_check(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        choice = QMessageBox.question(self, 'Warning!',  "These sequences may already been downloaded, continue?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            print('Continuing download')
        else:
            sys.exit()
        self.exec()



     