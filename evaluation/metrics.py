# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 15:14:01 2019

@author: Frances
"""

import numpy as np
from collections import namedtuple

def compute_accuracy(data, challenge):
    accuracy_data = {}
    if(challenge == 'overall'):  
        for t in data:
            seq_acc_sum = 0
            accuracy_data[t] = {}
            for s in data[t]:
                accuracy_data[t][s] = {}
                ##retrieve ground-truth bounding boxes
                gt_bboxes = np.array(data[t][s]['groundtruth'][:][:])
                print(gt_bboxes.shape[1])
            
                ##retrieve results bounding boxes
                ## the 'output' data is stored slightly differently than groundtruth
                ##it is stored as an object seems to be because there are a mixture of line sizes
                ## e.g sometimes only one integer in a line
                result_bboxes = np.array(data[t][s]['output'][:][:])
                print(len(result_bboxes[1]))
                
                accuracy, mean_seq_acc = compute_iou(gt_bboxes, result_bboxes)
                seq_acc_sum = seq_acc_sum + mean_seq_acc
                
               
                accuracy_data[t][s]['per_frame'] = accuracy
                accuracy_data[t][s]['sequence_acc'] = mean_seq_acc
            accuracy_data[t]['tracker_acc'] = seq_acc_sum/len(data[t])
        
    return accuracy_data

                
#                
def compute_iou(gt_bboxes, result_bboxes):
    ##currently just converting polygons to rectangles similar to VOT example ncc_initialize in ncc.m
    
    if gt_bboxes.shape[1] > 4:
        gt_bboxes = AABB(gt_bboxes[:, 0::2], gt_bboxes[:, 1::2])

    iou = np.zeros((gt_bboxes.shape[0], 1))
    for i in range(gt_bboxes.shape[0]):
        if len(result_bboxes[i]) < 4:
            if (result_bboxes[i] == [1.0]):
                iou[i, :] = 1.0
            else:
                iou[i,:] = 0
            continue  
        if len(result_bboxes[i]) > 4:
            result_bboxes[i] = AABB(result_bboxes[i][0::2], result_bboxes[i][1::2])
            result_bboxes[i] = np.squeeze(result_bboxes[i])
        w_O = min(gt_bboxes[i, 0]+ gt_bboxes[i,2], result_bboxes[i][0]+result_bboxes[i][2]) - max(gt_bboxes[i,0], result_bboxes[i][0])
        h_O = min(gt_bboxes[i,1]+gt_bboxes[i,3], result_bboxes[i][1] + result_bboxes[i][3]) - max(gt_bboxes[i,1], result_bboxes[i][1])
        overlap = w_O*h_O
        
        GboxArea = (gt_bboxes[i,2])*(gt_bboxes[i, 3])
        RboxArea = (result_bboxes[i][2] )*(result_bboxes[i][3] )
        
        iou[i, :] = overlap/float(GboxArea + RboxArea - overlap)
    
    mean_iou = np.mean(iou)
        
    return iou, mean_iou
        
        
    
def AABB(x, y):
    ##Computing axis-aligned bounding box from polygons according to how visual object tracking toolbox do this
        if len(x) > 4:
            x1 = np.amin(x, axis = 1)
            y1 = np.amin(y, axis = 1)
            x2= np.amax(x, axis = 1)
            y2 = np.amax(y, axis =1)
        else:
            x1 = np.amin(np.array(x))
            y1 = np.amin(np.array(y))
            x2 = np.amax(np.array(x))
            y2 = np.amax(np.array(y))
        region = np.column_stack((x1,y1,(x2-x1),(y2-y1)))
        return region