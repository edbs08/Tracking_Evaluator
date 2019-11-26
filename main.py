# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:11:53 2019

@author: Daniel
"""
import evaluation
from interface.interface import interface_main
import os.path
#
#def main():
#    print("Hello World!")

def read_workspace(data_path=os.getcwd()):
    #This function is to take the data from the dataset that the user provides
    #so once we read in file we check what trackers and sequences are available to compare/use

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
    # manually input directory because I didn't want to copy all sequences to new directory. 
   # trackers, sequences = read_workspace('C:/Users/Frances/Documents/UBr/TRDP/PythonCode/WorkingFolder/')
    trackers, sequences = read_workspace()
#    trackers, sequences = read_workspace(os.getcwd())
    interface_main(sequences,trackers)