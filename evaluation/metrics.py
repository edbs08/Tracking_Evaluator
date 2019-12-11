# -*- coding: utf-8 -*-
"""
Visual video tracker evaluator 
    metrics.py
    File used to compute the metrics of the evaluation

@authors: 
    E Daniel Bravo S
    Frances Ryan
"""

import numpy as np
import warnings
import sys
import copy
from shapely.geometry import Polygon, box
from math import exp, sqrt, log


def compute_ar_and_precision(data, challenge, sequences, trackers, eval_extras, metrics):
    """Calculates and collects accuracy, robustness and precision as selected
    
    Args: 
        data (dict): dictionary of dictionaries containing froundtruth and result
            data loaded for each tracker and sequence. Also includes tags loaded for challenges.
        challenge (list): list of strings - challenges to be assessed in this evaluation
        sequences(list): list of strings- sequences to be used in evaluation
        trackers(list): list of strings - trackers to be compared
        eval_extras(list): list of strings- if low frame search needed
        metrics (list): list of strings - metrics to be calculated during this evaluation
    
    Returns: 
        Dictionary containing data for metrics as per metrics list.
    """
    AR_data = {}
    for c in challenge:
        print('Processing challenge: ', c)
        AR_data[c] = {}
        for t in trackers:
            print('Tracker:', t)
            seq_acc_sum = 0
            AR_data[c][t] = {}
            fail_count = 0
            length = 0
            valid_seq = 0
            accuracy_list = []
            cle_list = []
            min_acc_frames = []
            for s in data[t].keys():
                # retrieve mask to apply when calculating challenge metrics
                challenge_mask, frame_idx = extract_challenge_mask(data, c, t, s)
                
                # if sequence is relevant for challenge then proceed
                if np.amax(challenge_mask) == 1:
                    if len(data[t][s]['output']) < len(data[t][s]['groundtruth']):
                        print('For tracker:', t, 'sequence: ', s)
                        warnings.warn('Result and Groundtruth not equal length will use first frames of result')
                    
                    valid_seq = valid_seq + 1;
                    AR_data[c][t][s] = {}
                    AR_data[c][t][s]['frame_indices'] = frame_idx
                    gt_bboxes = np.array(data[t][s]['groundtruth'][:][:])                    
                    result_bboxes = np.array(data[t][s]['output'][:][:])
                    
                    accuracy, mean_seq_acc, cle, mean_seq_cle = compute_iou_and_cle(gt_bboxes, result_bboxes, frame_idx, metrics)
                    if 'Accuracy' in metrics or 'Robustness' in metrics:
                        seq_acc_sum = seq_acc_sum + mean_seq_acc
                        AR_data[c][t][s]['acc_per_frame'] = accuracy
                        AR_data[c][t][s]['sequence_acc'] = mean_seq_acc
                        accuracy_list = np.append(accuracy_list, accuracy[~np.isnan(accuracy)])
                        if "Display Error Frames" in eval_extras:
                            min_frames = extract_min_frames(accuracy, frame_idx, s)
                            if min_frames != None:
                                min_acc_frames.extend(min_frames)
                    if 'Robustness' in metrics:
                        failures, f_i = count_failures(accuracy, result_bboxes, challenge_mask, s)
                        AR_data[c][t][s]['failures_per_sequence'] = failures
                        if failures > 1:
                            fragment = calc_fragment(failures, f_i, len(result_bboxes))
                            AR_data[c][t][s]['seq_fragment'] = fragment
                        length = length + len(result_bboxes)
                        fail_count = fail_count + failures
                    if 'Precision(Center Location Error)' in metrics:
                        AR_data[c][t][s]['precision_per_frame'] = cle
                        cle_list = np.append(cle_list, cle)
                        AR_data[c][t][s]['sequence_precision'] = mean_seq_cle
                     
            if valid_seq != 0:
                if 'Accuracy' in metrics:
                    AR_data[c][t]['tracker_acc'] = round(np.mean(np.array(accuracy_list)),4)
                    if "Display Error Frames" in eval_extras: 
                        low_frames = collect_low_frames(min_acc_frames)
                        if low_frames != None:
                            AR_data[c][t]['min_acc_frames'] =  low_frames
                if 'Robustness' in metrics:
                    AR_data[c][t]['tracker_failcount'] = fail_count
                    AR_data[c][t]['tracker_failrate'] = round(fail_count/length,4)
                    AR_data[c][t]['tracker_robust'] = round(exp(-(30*fail_count/length)), 4)
                if 'Precision(Center Location Error)' in metrics:
                    AR_data[c][t]['tracker_precision'] = round(np.mean(np.array(cle_list)),4)
            else:
                print("No data available with these sequences for challenge: ", c)
                    
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
            challenge_frames = np.arange(length)
            return mask, challenge_frames
        
    challenges = ["Camera Motion","Illumination Changes","Motion Change","Occlusion","Size change"]
    
    # Calculation of new mask necessary(instead of original tag file) as some tag files appear to be incomplete
    # with only start of sequences annotated with challenges e.g 'bag' - camera motion
    mask = np.zeros([length])
    for c in challenges:
        if(challenge == c):
            valid = True
            challenge_frames = np.where(data[tracker][sequence][challenge][:length] == 1)
            if len(challenge_frames[0]) > 0:
                mask[challenge_frames] = 1
            return mask,challenge_frames[0]
            
    if not valid:
            sys.exit('Challenge name not recognized')
            return None
    

def compute_iou_and_cle(gt_bboxes, result_bboxes, frame_idx, metrics):
    """ Calculate region overlap and center location error
    
    Args:
        gt_bboxes (list): list of floats of length 4 or 8 containing groundtruth polygon
        result_bboxes (list): list of floats of length 4 or 8 containing result polygon
        frame_idx (list of indices): for including only relevant frames of selected challenge
        metrics(list): list of strings of metrics to be calculated - in this case precision and/or accuracy
    
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
    
    groundtruth = gt_bboxes[frame_idx]
    result = result_bboxes[frame_idx]

    iou = np.zeros((groundtruth.shape[0], 1))
    cle = np.zeros((groundtruth.shape[0],1))
    incl_frames = 0
    for i in range(len(result)):
         # Not including first frame since tracker is just set, also excluding areas where tracker has failed as per VOT protocol
        if len(result[i]) < 4:
            iou[i, :] = np.nan
            continue
        incl_frames = incl_frames+1
        
        gt_poly = define_polygon(groundtruth[i, :])
        result_poly = define_polygon(result[i][:])
        
        eps = np.finfo(float).eps
        if 'Accuracy' in metrics or 'Robustness' in metrics:
            iou[i, :] = round(gt_poly.intersection(result_poly).area/(gt_poly.union(result_poly).area + eps),4)
            iou = np.clip(iou, 0.0, 1.0)
        
        if 'Precision(Center Location Error)' in metrics:
            gt_center= gt_poly.centroid.coords
            result_center = result_poly.centroid.coords
            
            cle[i,:] = sqrt((gt_center[0][0]-result_center[0][0])*(gt_center[0][0]-result_center[0][0])
                + ((gt_center[0][1]-result_center[0][1])*(gt_center[0][1]-result_center[0][1])))

    if incl_frames == 0:
        mean_iou = 0
        mean_cle = 0
    else:
        mean_iou = round(np.sum(iou[~np.isnan(iou)])/incl_frames, 4)
        mean_cle = round(np.sum(cle)/incl_frames,4)
        
    return iou, mean_iou, cle, mean_cle


def count_failures(acc, result, mask,s):
    """ Counts number of failures in given sequence
    
    Args: 
        acc(list): list of floats containing accuracy results for calcualting non-VOT data failures
        result (list): list of floats containing result polygon info - needed for calculating VOT data failures
        mask (list): boolean list containing challenges in each frame
    
    Returns:
        Number of failures in sequence
    """
    count = 0
    count1 = 0
    vot = False;
    length = min(len(mask), len(result))
    if len(result.shape) > 1:
        r1 = result[:length, :][mask == 1]
    else:
        r1 = result[:length][mask == 1]
    f_i1 = []
    f_i = []
    
    for i in range(len(r1)):
        if all(np.array(r1[i]) == [2.0]):
            vot = True
            f_i1.append(i)
            count1 += 1
        if acc[i] == [0] or acc[i] == 0:
            if i > 0 and acc[i-1] != [0]:
                f_i.append(i)
                count += 1

            
    if vot is True:
        return count1, f_i1
    else:
        return count, f_i
    
def calc_fragment(fail_count, f_i, N):
    """ Function for calculating fragmentation information where sequence failures were > 1
    
    Args:
        fail_count(int): number of failures from sequence
        f_i(list): list of ints with indices where failures occurred
        N(int): length of sequence
    
    Returns:
        Tuple containing fragmentation information
    """
    
    frag = 0
    for i in range(fail_count):
        if i != (fail_count-1):
            del_f = f_i[i+1] - f_i[i]
        else:
            del_f = f_i[1] + N - f_i[i]
        frag += -(del_f/N)*log(del_f/N) 
    
    frag = frag/log(fail_count)
    
    frag_tup = tuple((frag, f_i, N))
    
    return frag_tup
        
    
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
    
def extract_min_frames(val_list, idx_list,s):
    """Function for extracting minimum frames from given sequence
    
    Args:
        val_list(list): list of floats- overlap values
        idx_list(list): list of ints - frame indices
        s(string): name of sequence
    
    Returns:
        Tuple of low-frame search information
    """
    
    values = copy.deepcopy(val_list)
    length = len(values[~np.isnan(values)])
    if length == 0:
        return None
    elif length < 5:
        num_frames = 1
    else:
        num_frames = 5
    values = values.tolist()
    indices = copy.deepcopy(idx_list)
    indices = indices.tolist()
    min_vals = []
    for i in range(num_frames):
        min_loc = np.nanargmin(values)
        min_vals.append(tuple((values[min_loc][0], indices[min_loc], s)))
        del values[min_loc]
        del indices[min_loc]
    
    return min_vals
    
    
        
def collect_low_frames(min_list):
    """Function to collect low-performing frames from full evaluation
    
    Args:
        min_list(list): List containing tuples of previously collected information from low-performing frames
        
    Returns:
        tuple of overall minimum performing frames
    """
    if  len(min_list) == 0:
        return None
    elif len(min_list) < 5:
        num_frames = 1
    else:
        num_frames = 5
    min_frames = copy.deepcopy(min_list)
    final_mins = []
    for i in range(num_frames):
        min_loc = np.argmin([i[0] for i in min_frames])
        final_mins.append(tuple(min_frames[min_loc]))
        del min_frames[min_loc]
    
    return final_mins
#        
