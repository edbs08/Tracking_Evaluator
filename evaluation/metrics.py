# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 10:28:02 2019

@author: Frances
"""

import numpy as np
import warnings
import sys
from shapely.geometry import Polygon, box
from math import exp, sqrt


def compute_ar_and_precision(data, challenge, metrics):
    """Calculates and collects accuracy, robustness and precision as selected
    
    Args: 
        data (dict): dictionary of dictionaries containing froundtruth and result
            data loaded for each tracker and sequence. Also includes tags loaded for challenges.
        challenge (list): list of strings - challenges to be assessed in this evaluation
        metrics (list): list of strings - metrics to be calculated during this evaluation
    
    Returns: 
        Dictionary containing data for metrics as per metrics list.
    """
    AR_data = {}
    for c in challenge:
        print('Processing challenge: ', c)
        AR_data[c] = {}
        for t in data:
            print('Tracker:', t)
            seq_acc_sum = 0
            AR_data[c][t] = {}
            fail_count = 0
            length = 0
            valid_seq = 0
            accuracy_list = []
            cle_list = []
            for s in data[t]:
                # retrieve mask to apply when calculating challenge metrics
                challenge_mask = extract_challenge_mask(data, c, t, s)
                
                # if sequence is relevant for challenge then proceed
                if np.amax(challenge_mask) == 1:
                    if len(data[t][s]['output']) < len(data[t][s]['groundtruth']):
                        print('For tracker:', t, 'sequence: ', s)
                        warnings.warn('Result and Groundtruth not equal length will use first frames of result')
                    
                    valid_seq = valid_seq + 1;
                    AR_data[c][t][s] = {}
                    gt_bboxes = np.array(data[t][s]['groundtruth'][:][:])                    
                    result_bboxes = np.array(data[t][s]['output'][:][:])
                    
                    if 'Accuracy' in metrics:
                        accuracy, mean_seq_acc, cle, mean_seq_cle = compute_iou_and_cle(gt_bboxes, result_bboxes, challenge_mask)
                        seq_acc_sum = seq_acc_sum + mean_seq_acc
                        AR_data[c][t][s]['acc_per_frame'] = accuracy
                        AR_data[c][t][s]['sequence_acc'] = mean_seq_acc
                        accuracy_list = np.append(accuracy_list, accuracy[accuracy!=0])
                    if 'Robustness' in metrics:
                        failures = count_failures(result_bboxes, challenge_mask)       
                        AR_data[c][t][s]['failures_per_frame'] = failures
                        length = length + len(result_bboxes)
                        fail_count = fail_count + failures
                    if 'Precision(Center Location Error)' in metrics:
                        AR_data[c][t][s]['precision_per_frame'] = cle
                        cle_list = np.append(cle_list, cle[cle!=0])
                        AR_data[c][t][s]['sequence_precision'] = mean_seq_cle
                    
            if valid_seq != 0:
                if 'Accuracy' in metrics:
                    AR_data[c][t]['tracker_acc'] = round(np.mean(np.array(accuracy_list)),4)
                if 'Robustness' in metrics:
                    AR_data[c][t]['tracker_failcount'] = fail_count
                    AR_data[c][t]['tracker_failrate'] = round(fail_count/length,4)
                    AR_data[c][t]['tracker_robust'] = round(exp(-(30*fail_count/length)), 4)
                if 'Precision(Center Location Error)' in metrics:
                    AR_data[c][t]['tracker_precision'] = round(np.mean(np.array(cle_list)),4)                
            else:
                print("The chosen sequences do not contain examples of the requested challenge")
                             
    return AR_data
    

def extract_challenge_mask(data, challenge, tracker, sequence):
    """ Retrieve boolean mask indicating frames which contain certain challenge
    
    Args: 
        data (dict): dictionary of dictionaries containing froundtruth and result
            data loaded for each tracker and sequence. Also includes tags loaded for challenges.
        challenge (string): relevant challenge
        tracker (string): relevant tracker
        sequence (string): relevant sequence
    
    Returns:
        Boolean list for given sequence and challenge
    """
    valid = False
    length = min(len(data[tracker][sequence]['output']), len(data[tracker][sequence]['groundtruth']))
    if(challenge == 'Overall'):
            valid = True
            mask = np.ones([length])
            return mask
        
    challenges = ["Camera Motion","Illumination Changes","Motion Change","Occlusion","Size change"]
    
    mask = np.zeros([length])
    
    for c in challenges:
        if(challenge == c):
            valid = True
            challenge_frames = np.where(data[tracker][sequence][challenge][:length] == 1)
            if len(challenge_frames[0]) > 0:
                mask[challenge_frames] = 1
            return mask
            
    if not valid:
            sys.exit('Challenge name not recognized')
            return None
    

def compute_iou_and_cle(gt_bboxes, result_bboxes, challenge_mask):
    """ Calculate region overlap and center location error
    
    Args:
        gt_bboxes (list): list of floats of length 4 or 8 containing groundtruth polygon
        result_bboxes (list): list of floats of length 4 or 8 containing result polygon
        challenge_mask (boolean list): for including only relevant frames
    
    Returns: 
        iou (list): overlap for each frame of sequence
        mean_iou (float): mean for whole sequence
        cle (list): center location error for each frame
        mean_cle (float): mean for whole sequence
    
    """
    # correcting length of groundtruth to match output result
    if(len(result_bboxes) != gt_bboxes.shape[0]):
        length = min(len(result_bboxes), gt_bboxes.shape[0])
        gt_bboxes = gt_bboxes[:length, :]
        result_bboxes = result_bboxes[:length][:]
    
    groundtruth = gt_bboxes[challenge_mask == 1]
    result = result_bboxes[challenge_mask == 1]

    iou = np.zeros((groundtruth.shape[0], 1))
    cle = np.zeros((groundtruth.shape[0],1))
    incl_frames = 0
    for i in range(len(result)):
         # Not including first frame since tracker is just set, also excluding areas where tracker has failed as per VOT protocol
        if len(result[i]) < 4:
            iou[i, :] = 0
            continue
        incl_frames = incl_frames+1
        
        gt_poly = define_polygon(groundtruth[i, :])
        result_poly = define_polygon(result[i][:])
        
        eps = np.finfo(float).eps
        iou[i, :] = round(gt_poly.intersection(result_poly).area/(gt_poly.union(result_poly).area + eps),4)
        iou = np.clip(iou, 0.0, 1.0)
        
        gt_center= gt_poly.centroid.coords
        result_center = result_poly.centroid.coords
        
        cle[i,:] = sqrt((gt_center[0][0]-result_center[0][0])*(gt_center[0][0]-result_center[0][0])
            + ((gt_center[0][1]-result_center[0][1])*(gt_center[0][1]-result_center[0][1])))
        
        
    if incl_frames == 0:
        mean_iou = 0
        mean_cle = 0
    else:
        mean_iou = round(np.sum(iou)/incl_frames,4)
        mean_cle = round(np.sum(cle)/incl_frames,4)
        
    return iou, mean_iou, cle, mean_cle

def count_failures(result, mask):
    """ Counts number of failures in given sequence
    
    Args: 
        result (list): list of floats containing result polygon info
        mask (list): boolean list containing challenges in each frame
    
    Returns:
        Number of failures in sequence
    """
    count = 0
    r = result[mask == 1]
    
    for i in range(len(r)):
        if r[i] == [2.0]:
            count = count + 1
            
    return count

    
    
def define_polygon(x):
    """ Uses shapely library to define polygon or box object
    
    Args:
        x (list): list of floats containing groundtruth or result polygon information
    
    Returns:
        Shapely object polygon or box
    """
    if len(x) == 4:
        return box(round(x[0]), round(x[1]), round(x[0])+round(x[2]), round(x[1])+round(x[3]))
    if len(x) == 8:
        return Polygon([(round(x[0]), round(x[1])), (round(x[2]), round(x[3])), (round(x[4]), round(x[5])), (round(x[6]), round(x[7]))])
    else:
        print('Groundtruth or output result incorrect shape')
        return None
        
