# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 16:30:32 2018

@author: aungkon
"""

import os, json
import pandas as pd
import numpy as np
import gzip
# this finds our json files

#path = 'E:\Keylogs\mustafa\Data/7c7278f1-be44-41e4-b0d9-d9fa99116ce6/md2k/apiserver/data'                   #input directory (the folder I told you to remember)
path = 'E:/Keylogs/New_folder' 
output = 'E:\Keylogs\Extracted'                                         #output directory where the data will be saved
participant_dir = list(os.listdir(path))
for participant in participant_dir:
    path_to_date = path + '\\'+str(participant)
    date_dir = list(os.listdir(path_to_date))
    if date_dir == []:
        continue
    for date in date_dir:
        os.makedirs(output+str(participant)+'\\'+str(date))
        list_rip = []
        list_rip_baseline = []
        list_rip_seq = []
        list_acl_left = []
        list_acl_right = []
        list_ecg = []
        list_label = []
        list_raw_motionsense_left = []
        list_raw_motionsense_right = []
        path_to_uid = path_to_date + '\\' + str(date)
        for uid in os.listdir(path_to_uid):
            path_to_json = path_to_uid + '\\' + str(uid)
            json_list = list(filter(lambda x: str(x).endswith('.json'),os.listdir(path_to_json)))
            json_path = path_to_json+'\\'+str(json_list[0])
            try:
                data = json.load(open(json_path,'r'))
                if data['name']=='LABEL--org.md2k.studymperflab':
                    for json_name in json_list:
                        list_label.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name']=='RESPIRATION--org.md2k.autosenseble--AUTOSENSE_BLE--CHEST':
                    for json_name in json_list:
                        list_rip.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name']=='RESPIRATION_BASELINE--org.md2k.autosenseble--AUTOSENSE_BLE--CHEST':
                    for json_name in json_list:
                        list_rip_baseline.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name']=='SEQUENCE_NUMBER--org.md2k.autosenseble--AUTOSENSE_BLE--CHEST':
                    for json_name in json_list:
                        list_rip_seq.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name']=='ACCELEROMETER--org.md2k.motionsense--MOTION_SENSE_HRV--LEFT_WRIST':
                    for json_name in json_list:
                        list_acl_left.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name']=='ACCELEROMETER--org.md2k.motionsense--MOTION_SENSE_HRV--RIGHT_WRIST':
                    for json_name in json_list:
                        list_acl_right.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name'] == 'ECG--org.md2k.autosenseble--AUTOSENSE_BLE--CHEST':
                    for json_name in json_list:
                        list_ecg.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name'] == 'RAW--org.md2k.motionsense--MOTION_SENSE_HRV--LEFT_WRIST':
                    for json_name in json_list:
                        list_raw_motionsense_left.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
                if data['name'] == 'RAW--org.md2k.motionsense--MOTION_SENSE_HRV--RIGHT_WRIST':
                    for json_name in json_list:
                        list_raw_motionsense_right.append(path_to_json+'\\'+str(json_name).split('.')[0]+'.gz')
            except:
                print('Error occured')
        frame_label = []
        for index,file in enumerate(list_label):
            # print(participant,date,file)
            start = []
            tz = []
            annot = []
            with gzip.open(file,'rb') as z:
                for line in z:
                    print(str(line).split(','))
                    if str(line).split(',')[0][1]=='"':
                        start.append(np.int64(str(line).split(',')[0].split('"')[1]))
                    else:
                        start.append(np.int64(str(line).split(',')[0].split("'")[1]))
                    tz.append(np.int64(str(line).split(',')[1]))
                    annot.append(" ".join(str(line).split(',')[2:]).split('\\')[0])
            df = pd.DataFrame(np.column_stack([start, tz, annot]), columns=['start', 'tz', 'label']).sort_values(by='start')
            frame_label.append(df)
        if len(frame_label) > 0:
            lw = pd.concat(frame_label).sort_values(by='start').reset_index().set_index('start',drop=True)
            lw.to_csv(output+str(participant)+'\\'+str(date)+'\\label.csv',sep=',')
        frames_rip = []
        frames_rip_baseline = []
        frames_rip_seq = []
        frames_acl_left = []
        frames_acl_right = []
        frames_ecg = []
        frames_motionsense_left_raw = []
        frames_motionsense_right_raw = []
        for index,file in enumerate(list_raw_motionsense_left):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(22)])
            frames_motionsense_left_raw.append(df)
        for index,file in enumerate(list_raw_motionsense_right):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(22)])
            frames_motionsense_right_raw.append(df)
        for index,file in enumerate(list_rip):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(3)])
            frames_rip.append(df)
        for index,file in enumerate(list_rip_baseline):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(3)])
            frames_rip_baseline.append(df)
        for index,file in enumerate(list_rip_seq):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(3)])
            frames_rip_seq.append(df)
        for index,file in enumerate(list_acl_left):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(5)])
            frames_acl_left.append(df)
        for index,file in enumerate(list_acl_right):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(5)])
            frames_acl_right.append(df)
        for index,file in enumerate(list_ecg):
            df = pd.read_csv(file, compression='gzip', sep=',', quotechar='"',names=[str(i) for i in range(3)])
            frames_ecg.append(df)
        if len(frames_rip) > 0:
            rip = pd.concat(frames_rip).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\rip.csv',rip.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'rip')
        if len(frames_rip_baseline) > 0:
            base = pd.concat(frames_rip_baseline).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\baseline.csv',base.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'baseline')
        if len(frames_rip_seq) > 0:
            seq = pd.concat(frames_rip_seq).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\seq.csv',seq.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'seq')
        if len(frames_acl_left) > 0:
            acl_left = pd.concat(frames_acl_left).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\acl_left.csv',acl_left.as_matrix(),delimiter=',',fmt='%.15f')
            print(participant,date,'left')
        if len(frames_acl_right) > 0:
            acl_right = pd.concat(frames_acl_right).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\acl_right.csv',acl_right.as_matrix(),delimiter=',',fmt='%.15f')
            print(participant,date,'right')
        if len(frames_ecg) > 0:
            ecg = pd.concat(frames_ecg).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\ecg.csv',ecg.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'ecg')
        if len(frames_motionsense_left_raw) > 0:
            acl_left_raw = pd.concat(frames_motionsense_left_raw).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\acl_left_raw.csv',acl_left_raw.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'acl_left_raw')
        if len(frames_motionsense_right_raw) > 0:
            acl_right_raw = pd.concat(frames_motionsense_left_raw).sort_values(by=['0'])
            np.savetxt(output+str(participant)+'\\'+str(date)+'\\acl_right_raw.csv',acl_right_raw.as_matrix(),delimiter=',',fmt='%13d')
            print(participant,date,'acl_right_raw')
            
