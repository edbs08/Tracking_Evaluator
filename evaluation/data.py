# -*- coding: utf-8 -*-
"""
Visual video tracker evaluator 
    data.py

@authors: 
    E Daniel Bravo S
    Frances Ryan
"""
import wget
import os
import json
import zipfile
from PyQt5.QtWidgets import QMessageBox, QWidget, QInputDialog
import numpy as np
import os.path
import sys
from urllib.request import urlopen
import shutil

def initialize_workspace(data_path):
    """
    Used for unit test of the evaluation module
    """

    trackers = os.listdir(data_path + '/trackers')
    sequences = os.listdir(data_path + '/sequences')
    
    return trackers, sequences

def data_download():
    """ This function prompts the user to select one of the possible 
    datasets for comparison with their tracker. It allows the download of
    the VOT sequences and results from 2013-2019 and the OTB results from 2013.
    """
    
    choice = downloadData().ans
    src = choice.split('-')[0]
    version = choice.split('-')[1]
    
    if src == 'OTB':
        download_OTB()
    elif src == 'VOT':
        download_VOT_seq(version)
        download_VOT_trackers(version)
    
    return
      
def load_data(data_path, sequences, trackers, experiment_name, sample_number):
    """This function retrieves the correct output data from the tracker for a sequence
    
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
            gt_name = 'groundtruth.txt'
            output_path = os.path.join(data_path, 'trackers', t, experiment_name, s, filename)
            
            if os.path.isfile(output_path):
                gt_path = os.path.join(data_path, 'sequences', s)
                output = []
                with open(output_path, "r") as filestream:
                    for line in filestream:
                        currentline = line.split(",")
                        currentline = [float(i) for i in currentline]
                        output.append(currentline)        
                output = np.array(output)
                
                groundtruth = []
                with open(os.path.join(gt_path, gt_name), "r") as filestream: 
                    for line in filestream:
                        currentline = line.split(",")
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


def download_VOT_seq(version):
    """ Script to download VOT sequences   
    Args:
        version (string): what version of VOT sequences to download
    """
    print("Beginning download of VOT %s sequences"%version)
    if version == '2013' or version == '2014' or version == '2015':
        url = 'http://data.votchallenge.net/vot%s/dataset/' %version
        bundle_url = os.path.join(url, 'description.json')
    if version == '2016' or version == '2017' or version == '2018' or version == '2019':
        url = 'http://data.votchallenge.net/vot%s/main/' %version
        bundle_url = os.path.join(url, 'description.json')
    
    data_path = os.getcwd()
    sequence_path = os.path.join(data_path, 'sequences')
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
            if not os.path.isfile(anno_file):
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
        
    for file in os.listdir(sequence_path):
        if file.endswith(".zip"):
            os.remove(os.path.join(sequence_path, file))
            
    print("Download Complete")
    return


def download_VOT_trackers(version):
    """Function to download VOT tracker results from 
    selected year
    
    Args: version(string): year of the VOT results to download
    """
    print("Beginning download of VOT %s results"%version)

    url = 'http://data.votchallenge.net/vot%s' %version
    url = url + '/vot%s_results.zip' %version
    tracker_path = os.path.join(os.getcwd(), 'trackers')
    if not os.path.isdir(tracker_path):
        os.mkdir(tracker_path)
    
    file_name = 'vot%s_results.zip'%version
    if not os.path.isfile(file_name):
        try:  
             req = urlopen(url)
             with open(file_name, 'wb') as fp:
                 shutil.copyfileobj(req, fp, 16*1024)
             print("Results data download complete")
        except:
            print("Connection unstable results should be downloaded manually to continue: http://cvlab.hanyang.ac.kr/tracker_benchmark/v1.1/pami15_TRE.zip")
            return
    
    with zipfile.ZipFile(file_name) as z:
         z.extractall('trackers')

    for file in os.listdir(tracker_path): 
         if file.endswith(".zip"):
             with zipfile.ZipFile(os.path.join(tracker_path, file)) as z:
                 z.extractall('trackers')
                 os.remove(os.path.join(tracker_path,file))
   
    print("Download Complete")
    return

def download_OTB():
     """Function to download the 2013 results from the OTB benchmark
     Aligns the OTB annotations with the VOT annotations
     """
     # importing here so that it is an optional dependency for user
     from scipy.io import loadmat
     print("Beginning download of OTB results")
     url = "http://cvlab.hanyang.ac.kr/tracker_benchmark/v1.0/tracker_benchmark_v1.0_results.zip"
     
     sequences_ic = ['basketball', 'car4', 'carDark', 'david', 'ironman', 'liquor', 'matrix',
                     'motorRolling', 'shaking', 'singer2', 'skating1', 'skiing', 'soccer', 'sylvester', 
                     'tiger2', 'trellis', 'woman', 'coke', 'doll', 'faceocc2', 'fish', 'lemming', 'mhyang', 
                     'singer1', 'tiger1']
     sequences_sc = ['car4', 'carScale', 'couple', 'david', 'dudek', 'freeman4', 'girl', 'ironman', 'liquor', 
                     'matrix', 'motorRolling', 'shaking', 'skating1', 'skiing', 'soccer', 'trellis', 'walking',
                     'walking2', 'woman', 'boy', 'crossing', 'dog', 'dog1', 'doll', 'fleetface', 'freeman1', 
                     'freeman3', 'lemming', 'singer1']     
     sequences_occ = ['basketball', 'bolt', 'carScale', 'david', 'dudek', 'football', 'freeman4', 'girl', 'ironman', 
                      'liquor', 'matrix', 'skating1', 'soccer',  'tiger2', 'walking', 'walking2', 'woman', 
                      'coke', 'david3', 'doll', 'faceocc1', 'faceocc2', 'jogging-1', 'jogging-2', 'singer1'
                      'subway', 'suv', 'tiger1']
     sequences_mc = ['carScale', 'couple', 'deer', 'dudek', 'ironman', 'jumping', 'liquor', 'matrix', 'motorRolling', 
                     'soccer', 'tiger2', 'woman', 'boy', 'coke', 'crossing', 'fleetface', 'lemming', 'tiger1', 'david']
     sequences_cm = ['david', 'deer', 'ironman', 'jumping', 'liquor', 'motorRolling', 'soccer', 'tiger2', 'woman', 'boy'
                     'fleetface', 'tiger1']
     sequence_cats = [(sequences_ic, "illum_change.tag"), (sequences_sc, "size_change.tag"), (sequences_occ, "occlusion.tag"),
                     (sequences_mc, "motion_change.tag"), (sequences_cm, "camera_motion.tag")]
     data_path = os.getcwd()
     sequence_path = os.path.join(data_path, 'sequences')
     tracker_path = os.path.join(data_path, 'trackers')
     if not os.path.isdir(sequence_path):
        os.mkdir(sequence_path)
     if not os.path.isdir(tracker_path):
        os.mkdir(tracker_path)
        

     file_name = 'tracker_benchmark_results.zip'
     if not os.path.isfile(file_name):
         try:
             req = urlopen(url)
             with open(file_name, 'wb') as fp:
                 shutil.copyfileobj(req, fp, 32*1024)
             print("Results data download complete")
         except:
             print("Connection unstable results should be downloaded manually to continue: http://cvlab.hanyang.ac.kr/tracker_benchmark/v1.1/pami15_TRE.zip")
             return
     
     otb_loc = os.path.join('otb_results', 'results')
     with zipfile.ZipFile(file_name) as z:
         z.extractall('otb_results')
     not_needed = ['results_OPE', 'results_SRE', 'results_SRE_CVPR13', 'results_TRE']
     for n in not_needed:
         shutil.rmtree(os.path.join(otb_loc, n))
     otb_loc = os.path.join(otb_loc,'results_TRE_CVPR13' )
     
     available = os.listdir(os.path.join(otb_loc))
     s_name = []
     t_name = []
     for name in available:
         s_name.append(name.split('_')[0])
         t = name.split('_')[1]
         t_name.append(t.split('.')[0])
    
     s_name = list(set(s_name))
     t_name = list(set(t_name))
     not_include = ['ASLA', 'ivt', 'IVT', 'L1APG', 'MTT', 'ORIA', 'SCM']
     s_not_include = ['coke']
     for s in s_name:
         if s in s_not_include:
             continue
         for t in t_name:
             if t in not_include:
                 continue
             mat_read= loadmat(os.path.join(otb_loc, s + '_' + t + '.mat'))
             t_path = os.path.join(tracker_path,t)
             if not os.path.isdir(t_path):
                 os.mkdir(t_path)
                 os.mkdir(os.path.join(t_path, 'baseline'))
             if not os.path.isdir(os.path.join(t_path, 'baseline', s)):
                 tp_full = os.path.join(t_path, 'baseline', s)
                 os.mkdir(tp_full)
             if not os.path.isdir(os.path.join(sequence_path, s)):
                 s_path = os.path.join(sequence_path, s)
                 os.mkdir(s_path)
                 os.mkdir(os.path.join(sequence_path, s, 'color'))
             
                 gt = mat_read['results'][0]                
                 if len(gt[0].item(0)[-1]) < 2:
                     gt = gt[0].item(0)[-2]
                 else:
                     gt = gt[0].item(0)[-1]
    
                 f= open(os.path.join(s_path, "groundtruth.txt"),"w+")
                 for line in gt:
                     for i in range(len(line)):
                         if i == 0:
                             f.write(str(line[i]))
                         else:
                             f.write("," + str(line[i]))
                     f.write('\n')
                 f.close()
                 
                 for i in range(len(sequence_cats)):                     
                     if s in sequence_cats[i][0]:
                         f= open(os.path.join(s_path, sequence_cats[i][1]),"w+")
                         for i in range(gt.shape[0]):
                             f.write(str(1) + '\n')
                     f.close()

             otb_out = mat_read['results'][0]
             if len(otb_out[0].item(0)[0]) < 2:
                 otb_out = otb_out[0].item(0)[1]
             else:
                 otb_out = otb_out[0].item(0)[0]
            
             f = open(os.path.join(tp_full, s + '_001.txt'), "w+")
             for line in otb_out:
                 for i in range(len(line)):
                     if i == 0:
                         f.write(str(line[i]))
                     else:
                         f.write("," + str(line[i]))
                 f.write('\n')
             f.close()
     print("Download Complete")
     return
 
    
     
class downloadMessage(QWidget):
    """Class created to allow warning message to user if sequences already downloaded.
    """
    def __init__(self):
        super().__init__()
        self.title = 'Warning'
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
        
class downloadData(QWidget):
    """Class created to ask user about downloading data
    """
    def __init__(self):
        super().__init__()
        self.title = 'Data Download'
        self.left = 300
        self.top = 400
        self.width = 400
        self.height = 400
        self.resize(400,400)
        self.ans = self.getChoice()
        
    def getChoice(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        choice = QMessageBox.question(self, 'Data Download',  "Would you like to download some data for making comparisons?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            items = ("OTB-2013","VOT-2013","VOT-2014", "VOT-2015", "VOT-2016", "VOT-2017", "VOT-2018", "VOT-2019")
            item, okPressed = QInputDialog.getItem(self, "Options","Datasets:", items, 0, False)
            if okPressed and item:
                return item
        else:
            return




     
