#!/usr/bin/env python
# coding: utf-8

# # My Custom Module
# Il programma apre un file .txt di misure di sweep di tensione, ricostruisce le liste di misure originali, le plotta e ne salva le immagini. Ciascun plot può essere sovrapposto o affiancato. 
# 

# In[1]:


# Required imports
import sys
username = 'admin' # 'admin' for BO1 lab
sys.path.append('c:/users/'+ username +'/miniconda3/lib/site-packages')
import matplotlib.pyplot as plt
import qontrol
import time
import numpy as np
import datetime
import os

# Set the right path and file
lines = [] # list of lines of the .txt file
file_name = "Qontrol_and_Picoscope_IF_2021_03_26_11_35_16.txt"

# Variable declarations
F_overlapping_plots = 1 # 0 for non overlapping plots, not 0 otherwise
voltage_start = [] # list of voltage starting values for each channel/try
voltage_stop = []  # list of voltage stopping values for each channel/try
voltage_step = []  # list of voltage steps for each channel/try


# In[2]:


def from_linenumb_to_active_channel(line_numb, channel_steps):
    """
    map the line number to the active channel number. 
    N.B: the active channel is the one under sweeping
    """
    total_steps = 0
    for counter in range(len(channel_steps)):
        if (line_numb >= total_steps) and (line_numb < total_steps+channel_steps[counter]):
            return counter # the counter is exactly the active channel 
        total_steps += channel_steps[counter]        
        
def write_fit_file(filename, P_heater, PD_voltage):
    fitfile = open(filename+'_fit.txt','w')
    for i in range(len(P_heater)):
        for j in range(len(P_heater[i][i])):
            fitfile.write('{:+010.6f}\t{:+010.6f}\n' .format(P_heater[i][i][j],  PD_voltage[i][j]))
    fitfile.close()

def read_data(data_filename, FILE_PV = False):
    # Variable re-initialization
    lines = []
    voltage_start = [] 
    voltage_stop = []  
    voltage_step = []  

    file1 = open(data_filename,"r") 
    filename = file1.name.strip(".txt")

    # extract the voltage_start, voltage_stop, voltage_step and triangular from the file
    for i in range(9):
        line = file1.readline()
        if i == 5:
            # split into individual values and stripping the % and the \n
            voltage_start = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')] 
        elif i == 6:
            voltage_stop = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')]
        elif i == 7:
            voltage_step = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')]
        elif i == 8:
            F_triangular = int(line.rstrip('\n').strip('%')) # FLAG : 0 for ramp sweep, 1 for triangular sweep
        else:
            pass        

    # save each line as a list in the 'lines' list 
    for line in file1:
        if line[0] != '%':
            lines.append(line.rstrip('\n').split('\t'))

    # compute the number of channels/tries
    channels = int(len(lines[0])/2-1) # /2 because they are grouped in couples (current-voltages), 
                                      # -1 because first two columns are for PD

    # compute the total steps for each channel/try        
    channel_steps = [int((F_triangular+1)*(voltage_stop[j]-voltage_start[j])/voltage_step[j]) for j in range(channels)]

    # re-build the original measured_voltage, measured_current, PD_voltage and PD_current
    # measured_voltage[channels][channel_under_sweep][measurement]
    measured_voltage = [[[] for i in range(channels)] for j in range(channels)] 
    measured_current = [[[] for i in range(channels)] for j in range(channels)]
    PD_voltage = [[] for i in range(channels)]
    PD_current = [[] for i in range(channels)]
    P_heater = [[[] for i in range(channels)] for j in range(channels)]

    # populate each list
    for i in range(len(lines)):
        for channel in range(0,len(lines[0]),2):
            if channel == 0: # first two columns of the file are for the PD voltage and current
                PD_voltage[from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel]))
                PD_current[from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel+1]))
            else: # remaining columns are for the actual channels
                measured_voltage[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel]))
                measured_current[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel+1]))          
                if FILE_PV:
                    P_heater[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel])*float(lines[i][channel+1]))

    # Close the log file
    file1.close()

    if FILE_PV:
        # Write the fit file
        write_fit_file(filename,P_heater,PD_voltage)
    if FILE_PV:
        return {'measured voltage' : measured_voltage, 'measured current' : measured_current, 'PD voltage' : PD_voltage, 'PD current' : PD_current, 'P heater' : P_heater, 'channels' : channels}
    else:
        return {'measured voltage' : measured_voltage, 'measured current' : measured_current, 'PD voltage' : PD_voltage, 'PD current' : PD_current, 'channels' : channels}


# os.chdir('./Log') 
# total_data = {}
# # sequentially open each file and perform information extraction and data visualization   
# data_filename = 'Qontrol_and_Picoscope_IF_2021_03_26_11_35_16.txt' # 2-2
# data = read_data(data_filename, FILE_PV = True)
# total_data['2-2'] = data
# 
# # Plot results
# fig, axs = plt.subplots(3,2)
# #fig.suptitle(filename)
# 
# axs[0, 0].set_title('2-2 vs 2-1 : Ch. V vs Ch. I')
# axs[0, 0].set_xlabel('Voltage [V]')
# axs[0, 0].set_ylabel('Current [mA]')
# axs[1, 0].set_title('2-2 vs 2-1 : Ch. V vs -PD V')
# axs[1, 0].set_xlabel('Samples')
# axs[1, 0].set_ylabel('Voltage [mV]')
# axs[2, 0].set_title('2-2 vs 2-1 : P heater vs -PD V')
# axs[2, 0].set_xlabel('Power [mW]')
# axs[2, 0].set_ylabel('Voltage [mV]')
# 
# for i in range(data['channels']):
#     #print("\nPLOTS FOR DRIVING CHANNEL {:} \n" .format(channels[i]))
#     if F_overlapping_plots == 0:
#         axs[0, 0].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['measured current'][i][i])
#         axs[1, 0].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['PD voltage'][i])
#     else:
#         axs[0, 0].plot(data['measured voltage'][i][i], data['measured current'][i][i])
#         axs[1, 0].plot(range(len(data['measured current'][i][i])), data['PD voltage'][i])
#         #axs[2, 0].plot(range(len(measured_current[i][i])), P_heater[i][i])
#         axs[2, 0].plot(data['P heater'][i][i], data['PD voltage'][i])
#     #plt.xticks(np.arange(min(measured_current[i][i]), max(measured_current[i][i])))
#     #plt.xticks(np.arange(min(PD_current[i]), max(PD_current[i])+1))
# 
# plt.tight_layout()
# #plt.savefig('../Figures/' + filename + '.png')
# data_filename = 'Qontrol_and_Picoscope_IF_2021_03_26_11_46_38.txt' #2-1
# data = read_data(data_filename, FILE_PV = True)
# total_data['2-1'] = data
# 
# # Plot results
# 
# axs[0, 0].set_title('2-2 vs 2-1 : Ch. V vs Ch. I')
# axs[0, 0].set_xlabel('Voltage [V]')
# axs[0, 0].set_ylabel('Current [mA]')
# axs[1, 0].set_title('2-2 vs 2-1 : Ch. V vs -PD V')
# axs[1, 0].set_xlabel('Samples')
# axs[1, 0].set_ylabel('Voltage [mV]')
# axs[2, 0].set_title('2-2 vs 2-1 : P heater vs - PD V')
# axs[2, 0].set_xlabel('Power [mW]')
# axs[2, 0].set_ylabel('Voltage [mV]')
# 
# for i in range(data['channels']):
#     #print("\nPLOTS FOR DRIVING CHANNEL {:} \n" .format(channels[i]))
#     if F_overlapping_plots == 0:
#         axs[0, 0].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['measured current'][i][i])
#         axs[1, 0].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['PD voltage'][i])
#     else:
#         axs[0, 0].plot(data['measured voltage'][i][i], data['measured current'][i][i])
#         axs[1, 0].plot(range(len(data['measured current'][i][i])), data['PD voltage'][i])
#         #axs[2, 0].plot(range(len(measured_current[i][i])), P_heater[i][i])
#         axs[2, 0].plot(data['P heater'][i][i], data['PD voltage'][i])
#     #plt.xticks(np.arange(min(measured_current[i][i]), max(measured_current[i][i])))
#     #plt.xticks(np.arange(min(PD_current[i]), max(PD_current[i])+1))
# 
# plt.tight_layout()
# #plt.savefig('../Figures/' + filename + '.png')
# 
# data_filename = 'Qontrol_and_Picoscope_IF_2021_03_26_11_55_09.txt' #1-1
# data = read_data(data_filename, FILE_PV = True)
# total_data['1-1'] = data
# 
# # Plot results
# 
# axs[0, 1].set_title('1-1 vs 1-2 : Ch. V vs Ch. I')
# axs[0, 1].set_xlabel('Voltage [V]')
# axs[0, 1].set_ylabel('Current [mA]')
# axs[1, 1].set_title('1-1 vs 1-2 : Ch. V vs -PD V')
# axs[1, 1].set_xlabel('Samples')
# axs[1, 1].set_ylabel('Voltage [mV]')
# axs[2, 1].set_title('1-1 vs 1-2 : P heater vs -PD V')
# axs[2, 1].set_xlabel('Power [mW]')
# axs[2, 1].set_ylabel('Voltage [mV]')
# 
# for i in range(data['channels']):
#     #print("\nPLOTS FOR DRIVING CHANNEL {:} \n" .format(channels[i]))
#     if F_overlapping_plots == 0:
#         axs[0, 1].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['measured current'][i][i])
#         axs[1, 1].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['PD voltage'][i])
#     else:
#         axs[0, 1].plot(data['measured voltage'][i][i], data['measured current'][i][i])
#         axs[1, 1].plot(range(len(data['measured current'][i][i])), data['PD voltage'][i])
#         #axs[2, 1].plot(range(len(measured_current[i][i])), P_heater[i][i])
#         axs[2, 1].plot(data['P heater'][i][i], data['PD voltage'][i])
#     #plt.xticks(np.arange(min(measured_current[i][i]), max(measured_current[i][i])))
#     #plt.xticks(np.arange(min(PD_current[i]), max(PD_current[i])+1))
# 
# plt.tight_layout()   
# #plt.savefig('../Figures/' + filename + '.png')
# 
# data_filename = 'Qontrol_and_Picoscope_IF_2021_03_26_12_01_38.txt' #1-2
# data = read_data(data_filename, FILE_PV = True)
# total_data['1-2'] = data
# 
# # Plot results
# 
# axs[0, 1].set_title('1-1 vs 1-2 : Ch. V vs Ch. I')
# axs[0, 1].set_xlabel('Voltage [V]')
# axs[0, 1].set_ylabel('Current [mA]')
# axs[1, 1].set_title('1-1 vs 1-2 : Ch. V vs -PD V')
# axs[1, 1].set_xlabel('Samples')
# axs[1, 1].set_ylabel('Voltage [mV]')
# axs[2, 1].set_title('1-1 vs 1-2 : P heater vs - PD V')
# axs[2, 1].set_xlabel('Power [mW]')
# axs[2, 1].set_ylabel('Voltage [mV]')
# 
# for i in range(data['channels']):
#     #print("\nPLOTS FOR DRIVING CHANNEL {:} \n" .format(channels[i]))
#     if F_overlapping_plots == 0:
#         axs[0, 1].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['measured current'][i][i])
#         axs[1, 1].plot(range(i*len(data['measured current'][i][i]),(i+1)*len(data['measured current'][i][i])), data['PD voltage'][i])
#     else:
#         axs[0, 1].plot(data['measured voltage'][i][i], data['measured current'][i][i])
#         axs[1, 1].plot(range(len(data['measured current'][i][i])), data['PD voltage'][i])
#         #axs[2, 1].plot(range(len(measured_current[i][i])), P_heater[i][i])
#         axs[2, 1].plot(data['P heater'][i][i], data['PD voltage'][i])
#         #plt.xticks(range(len(measured_current[i][i])), [x/10 for x in range(len(measured_current[i][i]))] )
#     #plt.xticks(np.arange(min(PD_current[i]), max(PD_current[i])+1))
# 
# plt.tight_layout()
# plt.savefig('../Figures/' + data_filename.strip(".txt") + '.png')

# #change to the target directory  
# os.chdir('./Log') 
# 
# # sequentially open each file and perform information extraction and data visualization
# for j in os.listdir(): 
# 
#     # Variable re-initialization
#     lines = []
#     voltage_start = [] 
#     voltage_stop = []  
#     voltage_step = []  
#     
#     file1 = open(j,"r") 
#     filename = file1.name.strip(".txt")
# 
#     # extract the voltage_start, voltage_stop, voltage_step and triangular from the file
#     for i in range(9):
#         line = file1.readline()
#         if i == 5:
#             # split into individual values and stripping the % and the \n
#             voltage_start = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')] 
#         elif i == 6:
#             voltage_stop = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')]
#         elif i == 7:
#             voltage_step = [float(s.strip('%')) for s in line.rstrip('\n').split('\t')]
#         elif i == 8:
#             F_triangular = int(line.rstrip('\n').strip('%')) # FLAG : 0 for ramp sweep, 1 for triangular sweep
#         else:
#             pass        
# 
#     # save each line as a list in the 'lines' list 
#     for line in file1:
#         if line[0] != '%':
#             lines.append(line.rstrip('\n').split('\t'))
# 
#     # compute the number of channels/tries
#     channels = int(len(lines[0])/2-1) # /2 because they are grouped in couples (current-voltages), 
#                                       # -1 because first two columns are for PD
#     
#     # compute the total steps for each channel/try        
#     channel_steps = [int((F_triangular+1)*(voltage_stop[j]-voltage_start[j])/voltage_step[j]) for j in range(channels)]
# 
#     # re-build the original measured_voltage, measured_current, PD_voltage and PD_current
#     # measured_voltage[channels][channel_under_sweep][measurement]
#     measured_voltage = [[[] for i in range(channels)] for j in range(channels)] 
#     measured_current = [[[] for i in range(channels)] for j in range(channels)]
#     PD_voltage = [[] for i in range(channels)]
#     PD_current = [[] for i in range(channels)]
#     P_heater = [[[] for i in range(channels)] for j in range(channels)]
# 
#     # populate each list
#     for i in range(len(lines)):
#         for channel in range(0,len(lines[0]),2):
#             if channel == 0: # first two columns of the file are for the PD voltage and current
#                 PD_voltage[from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel]))
#                 PD_current[from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel+1]))
#             else: # remaining columns are for the actual channels
#                 measured_voltage[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel]))
#                 measured_current[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel+1]))  
#                 # computing the heater dissipated power (in mW)
#                 #P_heater[int((channel/2)-1)][from_linenumb_to_active_channel(i, channel_steps)].append(float(lines[i][channel])*float(lines[i][channel+1]))
#     # Close the log file
#     file1.close()
# 
#     # Plot results
#     fig, axs = plt.subplots(2,1)
#     fig.suptitle(filename)
#     
#     axs[0].set_title('Channel Voltage vs  Channel Current ')
#     axs[0].set_xlabel('Voltage [V]')
#     axs[0].set_ylabel('Current [mA]')
#     axs[1].set_title('Channel Voltage vs  -PD Voltage ')
#     axs[1].set_xlabel('Samples')
#     axs[1].set_ylabel('Voltage [mV]')
# 
#     for i in range(channels):
#         #print("\nPLOTS FOR DRIVING CHANNEL {:} \n" .format(channels[i]))
#         if F_overlapping_plots == 0:
#             axs[0].plot(range(i*len(measured_current[i][i]),(i+1)*len(measured_current[i][i])), measured_current[i][i])
#             axs[1].plot(range(i*len(measured_current[i][i]),(i+1)*len(measured_current[i][i])), PD_voltage[i])
#         else:
#             axs[0].plot(measured_voltage[i][i], measured_current[i][i])
#             axs[1].plot(range(len(measured_current[i][i])), PD_voltage[i])
#         #plt.xticks(np.arange(min(measured_current[i][i]), max(measured_current[i][i])))
#         #plt.xticks(np.arange(min(PD_current[i]), max(PD_current[i])+1))
# 
#     plt.tight_layout()
#     plt.savefig('../Figures/' + filename + '.png')

# In[ ]:




