#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 21:29:09 2017

@author: corinnefarley
"""

import pandas, data_utils, itertools, numpy
from sklearn import ensemble, svm, feature_selection

# Provides dictionary with default values so user doesn't have to specify each one
def get_args():
    arguments = {'piece_size': 50, 'print_metrics': False, 
                  'plot_each_axis': True, 'xmin_index': 0, 'xmax_index': 700,
                  'classifiers': [ensemble.RandomForestClassifier(), svm.SVC(kernel = 'linear')],
                  'features': ["mean()", "median()", "max()", "min()", "var()", 
                               "std()", "quantile(0.25)", "quantile(0.50)", 
                               "quantile(0.75)", "kurt()", "skew()", 
                               "zero_cross", "fft", "peaks"],
                  'label_type': 'set_num', 'thresholds': [], 'set_labels': [],
                  'n_splits': 10, 'overlap': True, 'time_cutoffs': [], 
                  'title': 'title', 'average_type': 'weighted', 
                  'combinations': 'all_combos', 'undersample': False}
    return arguments


# Reads and formats data into readable DataFrames
# Each "data set" contains four files: Left AccX/Y/Z, Left GyrX/Y/Z, Right AccX/Y/Z, and Right GyrX/Y/Z
# Function takes a list of "data sets" so that multiple ones can be packaged without repeatedly calling the function
def package_data(raw_data_sets, keylog_files, mouselog_files):
    # List of normalized data sets, with each motions axes in a separate DataFrame
    normalized_raw_data_sets = []   
    # List of normalized data sets, with all motion axes for each set in one DataFrame
    combined_axes_sets = []
    # Indices of peaks for each column of combined
    peak_indices = []
    # List of keylog DataFrames
    keylogs = []
    # List of mouselog DataFrames
    mouselogs = []
    
    for data_set in raw_data_sets:
        
        # Makes DataFrames of imported data
        acc_dataR = pandas.read_csv(data_set[0], header = None, 
                                    names = ["Time", "ID", "AccXR", "AccYR", "AccZR"]).drop('ID', axis=1)
        gyr_dataR = pandas.read_csv(data_set[1], header = None, 
                                    names = ["Time", "ID", "GyrXR", "GyrYR", "GyrZR"]).drop('ID', axis=1)
        acc_dataL = pandas.read_csv(data_set[2], header = None, 
                                    names = ["Time", "ID", "AccXL", "AccYL", "AccZL"]).drop('ID', axis=1)
        gyr_dataL = pandas.read_csv(data_set[3], header = None, 
                                    names = ["Time", "ID", "GyrXL", "GyrYL", "GyrZL"]).drop('ID', axis=1)
        
        
        # Normalizes data
        normalized_data = data_utils.normalize_data([acc_dataR, gyr_dataR, acc_dataL, gyr_dataL])
        
        # Merges data (interpolates between data points to fill time gaps)
        combined = data_utils.merge_data(normalized_data)
        
        # Finds peaks in data; 
        # Threshold and min distance between peaks can be changed, but new indices for time sync will need to be found
        indices = data_utils.find_peaks(combined, 0.3, 10)
        
        # Adding to lists
        normalized_raw_data_sets.append(normalized_data)
        combined_axes_sets.append(combined)
        peak_indices.append(indices)
    
    # Makes DataFrames of imported data
    for keylog_name in keylog_files:
        keylog = pandas.read_csv(keylog_name, header = None, names = ["Time", "Char"])
        keylog = keylog.iloc[1:keylog.shape[0] - 1] # Deletes "logging started" and "logging ended" lines
        keylogs.append(keylog)
        
    if len(mouselog_files) > 0:
        for mouselog_name in mouselog_files:
            mouselog = pandas.read_csv(mouselog_name, header = None, 
                                       names = ["Time", "Type", "PosX", "PosY", "Button", "ClickCount"])
            mouselog = mouselog.iloc[8:mouselog.shape[0] - 1] # Deletes "logging started" and "logging ended" lines
            mouselog = mouselog[mouselog['Time'] != "'"]
            mouselog = mouselog[mouselog['Time'] != "Logging ended at 1501625043677"]
            mouselogs.append(mouselog)
       
    return [normalized_raw_data_sets, combined_axes_sets, peak_indices, keylogs, mouselogs]

# Synchronizes time stamps
def sync_time(data_set, correct_time):
    data_utils.sync_time(data_set, correct_time)
    return
        
# Generates plots for one data set
def generate_plots(normalized_raw_data, combined_axes, peak_indices, 
                   keylog, mouselog, args):
    plot_each_axis = args['plot_each_axis']
    time_cutoffs = args['time_cutoffs']
    xmin_index = args['xmin_index']
    xmax_index = args['xmax_index']
    
    # Plots data
    if plot_each_axis:
        # Each motion plotted individually, then together
        f, axes = data_utils.plot_motion(normalized_raw_data, True)
        # Keystrokes and peaks added to individual motion plots
        need_lines = [axes[0], axes[1], axes[2], axes[4], axes[5], axes[6], axes[8], 
                      axes[9], axes[10], axes[12], axes[13], axes[14]]
        # Time cutoffs between classes added to combined motion plots
        need_cutoffs = [axes[3], axes[7], axes[11], axes[15]]
        data_utils.add_lines_and_peaks(combined_axes, keylog, mouselog,
                                     need_lines, need_cutoffs, peak_indices, 
                                     time_cutoffs)
        data_utils.shift_plot(need_lines, combined_axes.index[xmin_index], 
                            combined_axes.index[xmax_index], -1, 1)
    else:
        # Motions plotted together
        f, axes = data_utils.plot_motion(combined_axes, False)
        data_utils.add_lines_and_peaks(combined_axes, keylog, mouselog, [], axes, peak_indices, 
                                     time_cutoffs)
    return

# Builds 2D arrays to feed to classifiers
def generate_data_arrays(all_sets, keylogs, set_names, peaks_times, args):
    label_type = args['label_type']
    title = args['title']
    set_labels = args['set_labels']
    combinations = args['combinations']
    thresholds = args['thresholds']
    undersample = args['undersample']
    if not len(set_labels):
        set_labels = list(range(len(all_sets)))
    
    # These types break data sets into classes based on keylogger data 
    # Each set in "all_sets" is generally a mix of classes
    # Will produce one sample array and one label array
    if label_type == 'char_thresholds' or label_type == 'num_chars':
        sets = []
        for count in range(len(all_sets)):
            sets.append(all_sets[count].reset_index())
        text_for_metrics = [[title, 'Comparing ' + str(len(thresholds)) + ' Speeds']]
        labels_for_classifier = [set_labels]
        sets_for_classifier = [sets]
        
    # This type breaks data sets into classes based on given labels 
    # Each set in "all_sets" is generally its own class
    # Will produce one sample array and one label array for EACH combination of classes to be compared
    elif label_type == 'set_num':
        # Building list of combination indices based on combinations argument
        # Default is all possible combinations of sets; can also be all sets or any custom combinations
        if combinations == 'all_combos':
            # Creates all possible combinations of sets
            indices_of_combinations = []
            set_indices = range(len(all_sets))
            for count in range(2, len(all_sets) + 1):
                indices_of_combinations.extend(list(itertools.combinations(set_indices, count)))
        elif combinations == 'all_sets':
            set_indices = range(len(all_sets))
            indices_of_combinations = [tuple(set_indices)]
        else:
            indices_of_combinations = combinations
            
        sets_for_classifier = []        # List of all set combos (will contain the actual data)
        text_for_metrics = []
        labels_for_classifier = []
        # For each combination of data sets, puts sets in list to make into data array
        for combination in indices_of_combinations:
            combo = []                          
            combo_indices = list(combination)
            combo_name = 'Comparing: '
            combo_labels = []
            for index in combo_indices:
                # Creates description for combo based on set titles
                combo.append(all_sets[index].reset_index())
                combo_name = combo_name + set_names[index] + ' '
                combo_labels.append(set_labels[index])
            # If multiple class types in combo (don't want to give data from only one class to classifier)
            if len(set(combo_labels)) > 1:
                # Adds list of data sets in this combo to list of all set combos
                sets_for_classifier.append(combo)   
                text_for_metrics.append([title, combo_name])
                labels_for_classifier.append(combo_labels)
    
    # Makes a data array for each set of data to be classified
    arrays_for_classifier = []
    
    for set_num in range(len(sets_for_classifier)):
        data_set = sets_for_classifier[set_num]
        labels = labels_for_classifier[set_num]
        allX, allY, delta_ts = data_utils.make_data_array(data_set, keylogs, label_type, labels, peaks_times, args)
        #allX = preprocessing.StandardScaler().fit_transform(allX)   # scales/standardizes features 
        if undersample:
            allX, allY = data_utils.undersample(allX, allY)
        
        arrays_for_classifier.append([allX, allY, delta_ts])
       
    return arrays_for_classifier, text_for_metrics

# Trains and validates, then makes DataFrame of scores; used to test multiple classifiers, piece sizes, etc.
def generate_metrics(arrays_for_classifier, text, args):
    all_metrics = []
    
    # Trains and validates using classifiers
    for array_pair in arrays_for_classifier:
        allX = array_pair[0]
        allY = array_pair[1]
        delta_ts = array_pair[2]
        metrics = data_utils.classify(allX, allY, delta_ts, args)
        all_metrics.append(metrics)
    # Builds DataFrame from results
    return data_utils.generate_metrics_df(all_metrics, text, args) 

# Allows user to retrieve a trained classifier for later use (once best classifier has been determined by generate_metrics)
def train_classifier(array_pair, classifier):
    allX = array_pair[0]
    allY = array_pair[1]    
    allY = numpy.reshape(allY, [allY.shape[0],])
    
    # Feature selection specific to classifier
    classifier.fit(allX, allY)
    model = feature_selection.SelectFromModel(classifier, prefit=True)
    features_selected = model.get_support()
    X_train = model.transform(allX)
    
    # Trains and validates
    reset_classifier = classifier
    trained_classifier = reset_classifier.fit(X_train, allY)
    
    return trained_classifier, features_selected

# Extracts time stamps from data for each peak index
def peak_indices_to_times(combined, peaks):
    peak_times = []
    for axis_num in range(combined.shape[1]):
        peak_times.append(combined.iloc[peaks[axis_num],axis_num].index)
    return peak_times

# Concatenates every two samples so that each new sample contains two time windows
# New labels are for second time window
def concat_samples(allX, allY):
    allX_even = allX[::2]
    allX_odd = allX[1::2]
    allY_odd = allY[1::2]
    allX_even = allX_even[:len(allX_odd)]
    allY_odd = allY_odd[:len(allX_odd)]
    concatenated_samples = numpy.concatenate((allX_even, allX_odd), axis=1)
    return concatenated_samples, allY_odd

def change_labels(label_array, old_vals, new_vals):
    new_label_array = numpy.copy(label_array)
    for index in range(len(old_vals)):
        old_label = old_vals[index]
        new_label = new_vals[index]
        new_label_array[label_array == old_label] = new_label
    return new_label_array

def undersample(allX, allY):
    return data_utils.undersample(allX, allY)
    
