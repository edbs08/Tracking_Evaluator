# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 10:28:02 2019

@author: Frances
"""

import numpy as np
import copy
import warnings
import sys
from shapely.geometry import Polygon, box
from math import exp


def compute_AR(data, challenge):
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
            for s in data[t]:
                challenge_mask = extract_challenge_mask(data, c, t, s)
                if np.amax(challenge_mask) == 1:
                    #print('Computing accuracy for tracker: ', t, ' and sequence: ', s)
                    if len(data[t][s]['output']) < len(data[t][s]['groundtruth']):
                        print('For tracker:', t, 'sequence: ', s)
                        warnings.warn('Result and Groundtruth not equal length will use first frames of result')
                    
                    valid_seq = valid_seq + 1;
                    AR_data[c][t][s] = {}
                    ##retrieve ground-truth bounding boxes
                    gt_bboxes = np.array(data[t][s]['groundtruth'][:][:])
                    #print(gt_bboxes.shape[1])
                    
                    ##retrieve results bounding boxes
                    ## the 'output' data is stored slightly differently than groundtruth
                    ##it is stored as an object seems to be because there are a mixture of line sizes
                    ## e.g sometimes only one integer in a line
                    result_bboxes = np.array(data[t][s]['output'][:][:])
                    #print(len(result_bboxes[1]))
               
                    accuracy, mean_seq_acc = compute_iou(gt_bboxes, result_bboxes, challenge_mask)
                    seq_acc_sum = seq_acc_sum + mean_seq_acc
            
                    AR_data[c][t][s]['acc_per_frame'] = accuracy
                    AR_data[c][t][s]['sequence_acc'] = mean_seq_acc
                    accuracy_list = np.append(accuracy_list, accuracy[accuracy!=0])
                    robustness = count_failures(result_bboxes, challenge_mask)       
                    AR_data[c][t][s]['robust_per_frame'] = robustness
                    length = length + len(result_bboxes)
                    fail_count = fail_count + robustness
                    
            if valid_seq != 0:
                #accuracy_data[t]['tracker_acc'] = round(seq_acc_sum/valid_seq,4)
                #accuracy_data[t]['tracker_acc']  = round(sum(accuracy_list)/len(accuracy_list),4)
                AR_data[c][t]['tracker_acc'] = round(np.mean(np.array(accuracy_list)),4)
                AR_data[c][t]['tracker_failcount'] = fail_count
                AR_data[c][t]['tracker_failrate'] = round(fail_count/length,4)
                AR_data[c][t]['tracker_robust'] = exp(-(30*fail_count/length))
            else:
                print("The chosen sequences do not contain examples of the requested challenge")
                             
    return AR_data
    

def extract_challenge_mask(data, challenge, tracker, sequence):
    valid = False
    length = min(len(data[tracker][sequence]['output']), len(data[tracker][sequence]['groundtruth']))
    if(challenge == 'overall'):
            valid = True
            mask = np.ones([length])
            return mask
        
    challenges = ['occlusion', 'camera_motion', 'motion_change', 'illum_change', 'size_change']
    
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
    return
    

def compute_iou(gt_bboxes, result_bboxes, challenge_mask):


    ##correcting length of groundtruth to match output result so mean isn't incorrect.
    
    if(len(result_bboxes) != gt_bboxes.shape[0]):
        length = min(len(result_bboxes), gt_bboxes.shape[0])
        gt_bboxes = gt_bboxes[:length, :]
        result_bboxes = result_bboxes[:length][:]
    
    groundtruth = gt_bboxes[challenge_mask == 1]
    result = result_bboxes[challenge_mask == 1]

    iou = np.zeros((groundtruth.shape[0], 1))
    incl_frames = 0
    for i in range(len(result)):
         ##Not including first frame since tracker is just set, also excluding areas where tracker has failed as per VOT protocol
        if len(result[i]) < 4:
            iou[i, :] = 0
            continue
        incl_frames = incl_frames+1
        
        gt_poly = define_Polygon(groundtruth[i, :])
        result_poly = define_Polygon(result[i][:])
        
        eps = np.finfo(float).eps
        iou[i, :] = round(gt_poly.intersection(result_poly).area/(gt_poly.union(result_poly).area + eps),4)
        iou = np.clip(iou, 0.0, 1.0)

        
    if incl_frames == 0:
        mean_iou = 0
    else:
        mean_iou = round(np.sum(iou)/incl_frames,4)
        
    return iou, mean_iou

def count_failures(result, mask):
    count = 0
    r = result[mask == 1]
    
    for i in range(len(r)):
        if r[i] == [2.0]:
            count = count + 1
            
    return count
    
        
        
    
def define_Polygon(x):
    if len(x) == 4:
        return box(round(x[0]), round(x[1]), round(x[0])+round(x[2]), round(x[1])+round(x[3]))
    if len(x) == 8:
        return Polygon([(round(x[0]), round(x[1])), (round(x[2]), round(x[3])), (round(x[4]), round(x[5])), (round(x[6]), round(x[7]))])
    else:
        print('Groundtruth or output result incorrect shape')