# -*- coding: utf-8 -*-
"""
Visual video tracker evaluator 
    main.py

@authors: 
    E Daniel Bravo S
    Frances Ryan
"""

from evaluation.data import data_download
from interface.interface import interface_main
from PyQt5.QtWidgets import QApplication
import sys
import os.path


def read_workspace(data_path=os.getcwd()):
    """
    This function is to take the data from the dataset that the user provides.
    Is used to list the trackers and sequences available to compare/use.
    """
    if not os.path.isdir(os.path.join(data_path, 'trackers')) or not os.listdir(os.path.join
        (data_path, 'trackers')) or not os.path.isdir(os.path.join(data_path, 'sequences')) or not    		os.listdir(os.path.join(data_path, 'sequences')):
        app = QApplication(sys.argv)
        data_download()
	

    trackers_all = os.listdir(data_path + '/trackers')
    sequences_all = os.listdir(data_path + '/sequences')
    
    #List only folders in sequence, not files
    trackers = []
    for filename in trackers_all: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath(data_path + '/trackers'), filename)): # check whether the current object is a folder or not
            trackers.append(filename)
    
    #List only folders in sequence, not files
    sequences = []
    for filename in sequences_all: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath(data_path + '/sequences'), filename)): # check whether the current object is a folder or not
            sequences.append(filename)
    
    return trackers, sequences

if __name__ == "__main__":
    trackers, sequences = read_workspace()
    interface_main(sequences,trackers)
