#!/usr/bin/env python
# coding: utf-8

# # My Custom Module

# In[ ]:


# Required imports
import sys
username = 'admin' # 'admin' for BO1 lab
sys.path.append('c:/users/'+ username +'/miniconda3/lib/site-packages')
import picosdk
import logging
import ctypes
from picosdk.ps4000 import ps4000 as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
from statistics import mean
import math
import matplotlib.pyplot as plt
import qontrol
import time
import numpy as np
import datetime
import os
import wx # needed to take a screenshot

get_ipython().run_line_magic('matplotlib', 'inline')

# Set the right path and file
lines = [] # list of lines of the .txt file
file_name = "Qontrol_and_Picoscope_IF_2021_03_26_11_35_16.txt"

# Variable declarations
F_overlapping_plots = 1 # 0 for non overlapping plots, not 0 otherwise
voltage_start = [] # list of voltage starting values for each channel/try
voltage_stop = []  # list of voltage stopping values for each channel/try
voltage_step = []  # list of voltage steps for each channel/try

#Configure the logging
logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
chandle = ctypes.c_int16()


# In[ ]:


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


# In[ ]:


def take_screenshot(xdest = 0, ydest= 0, xsrc = 0, ysrc = 0, image_name=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), save_path=os.getcwd(), screen_resolution=[1920,1080]):
    """
    Take a screenshot of the entire screen and save it in the save_path directory with
    the timestamp as its name
    """
    #take a bitmap
    
    # CAUTION! : if you get the error "The wx.App object must be created first!" 
    #            comment the following line
    
    #wx.App()
    
    #            and in the main code, in the first cell (the import section), 
    #            separated from the rest of the code, insert the line: app = wx.App(False)
    
    screen = wx.ScreenDC()
    bmp = wx.Bitmap(screen_resolution[0], screen_resolution[1]) 
    mem = wx.MemoryDC(bmp)
    mem.Blit(xdest, ydest, screen_resolution[0], screen_resolution[1], screen, xsrc, ysrc) 
    del mem  # Release bitmap
    
    #save the screenshot in a png file 
    bmp.SaveFile(save_path + '/' + image_name + '.png', wx.BITMAP_TYPE_PNG) # it is saved where the ipynb is


# ## Picoscope functions

# In[ ]:


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
    global nextSample, autoStopOuter, wasCalledBack
    wasCalledBack = True
    destEnd = nextSample + noOfSamples
    sourceEnd = startIndex + noOfSamples
    bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
    bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
    nextSample += noOfSamples
    if autoStop:
        autoStopOuter = True

def pico_start(channel_range, sampleInterval = ctypes.c_int32(250), sampleUnits = ps.PS4000_TIME_UNITS['PS4000_US'], sizeOfOneBuffer = 500, numBuffersToCapture = 10, maxPreTriggerSamples = 0, autoStopOn = 1, downsampleRatio = 1):
    """
    channel range : ps.PS4000_RANGE['PS4000_2V']
    sampleInterval : ctypes.c_int32(250) in sample units specified by sampleUnits
    sampleUnits = ps.PS4000_TIME_UNITS['PS4000_US']
    sizeOfOneBuffer = 500 size of a single buffer
    numBuffersToCapture = 10 --> totalSamples = sizeOfOneBuffer * numBuffersToCapture
    
    Note:   actualSampleInterval = sampleInterval.value
            actualSampleIntervalNs = actualSampleInterval * 1000
            totalSamplingTime = totalSamples * actualSampleIntervalNs
            # If we are not triggering:
            maxPreTriggerSamples = 0
            autoStopOn = 1
            # If we do not want downsampling:
            downsampleRatio = 1
    """
    
    # Size of capture
    totalSamples = sizeOfOneBuffer * numBuffersToCapture
    
    # Create status ready for use
    global status 
    status = {}

    # Open PicoScope 2000 Series device
    # Returns handle to chandle for use in future API functions
    status["openunit"] = ps.ps4000OpenUnit(ctypes.byref(chandle))
    assert_pico_ok(status["openunit"])


    enabled = 1
    disabled = 0
    analogue_offset = 0.0
    nextSample = 0
    autoStopOuter = False
    wasCalledBack = False

    # Set up channel A
    # handle = chandle
    # channel = PS4000_CHANNEL_A = 0
    # enabled = 1
    # coupling type = PS4000_DC = 1
    # range = PS4000_2V = 7
    #global channel_range = ps.PS4000_RANGE['PS4000_2V']
    status["setChA"] = ps.ps4000SetChannel(chandle,
                                            ps.PS4000_CHANNEL['PS4000_CHANNEL_A'],
                                            enabled,
                                            1,
                                            channel_range)
    assert_pico_ok(status["setChA"])

    # Set up channel B
    # handle = chandle
    # channel = PS4000_CHANNEL_B = 1
    # enabled = 1
    # coupling type = PS4000_DC = 1
    # range = PS4000_2V = 7
    status["setChB"] = ps.ps4000SetChannel(chandle,
                                            ps.PS4000_CHANNEL['PS4000_CHANNEL_B'],
                                            enabled,
                                            1,
                                            channel_range)
    assert_pico_ok(status["setChB"])



    # Create buffers ready for assigning pointers for data collection
    global bufferAMax
    bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    global bufferBMax
    bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    # We need a big buffer, not registered with the driver, to keep our complete capture in.
    global bufferCompleteA
    bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
    global bufferCompleteB
    bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)

    memory_segment = 0



    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = PS4000_CHANNEL_A = 0
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS4000_RATIO_MODE_NONE = 0
    status["setDataBuffersA"] = ps.ps4000SetDataBuffers(chandle,
                                                         ps.PS4000_CHANNEL['PS4000_CHANNEL_A'],
                                                         bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                         None,
                                                         sizeOfOneBuffer)
    assert_pico_ok(status["setDataBuffersA"])

    # Set data buffer location for data collection from channel B
    # handle = chandle
    # source = PS4000_CHANNEL_B = 1
    # pointer to buffer max = ctypes.byref(bufferBMax)
    # pointer to buffer min = ctypes.byref(bufferBMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS4000_RATIO_MODE_NONE = 0
    status["setDataBuffersB"] = ps.ps4000SetDataBuffers(chandle,
                                                         ps.PS4000_CHANNEL['PS4000_CHANNEL_B'],
                                                         bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                         None,
                                                         sizeOfOneBuffer)
    assert_pico_ok(status["setDataBuffersB"])

    # Begin streaming mode:
    
    
    # We are not triggering:
    maxPreTriggerSamples = 0
    autoStopOn = 1
    # No downsampling:
    downsampleRatio = 1

    actualSampleInterval = sampleInterval.value
    actualSampleIntervalNs = actualSampleInterval * 1000
    totalSamplingTime = totalSamples * actualSampleIntervalNs
    logging.info("Capturing at sample interval %10.3E ns, with total sampling time of %10.3E ns" % (actualSampleIntervalNs, totalSamplingTime))

def pico_acquire_measurement(channel_range, sampleInterval = ctypes.c_int32(250), sampleUnits = ps.PS4000_TIME_UNITS['PS4000_US'], sizeOfOneBuffer = 500, numBuffersToCapture = 10, maxPreTriggerSamples = 0, autoStopOn = 1, downsampleRatio = 1, discarded_portion = 0.0, plot = False):    
    global status
    totalSamples = sizeOfOneBuffer * numBuffersToCapture
    actualSampleInterval = sampleInterval.value
    actualSampleIntervalNs = actualSampleInterval * 1000
    
    status["runStreaming"] = ps.ps4000RunStreaming(chandle,
                                                ctypes.byref(sampleInterval),
                                                sampleUnits,
                                                maxPreTriggerSamples,
                                                totalSamples,
                                                autoStopOn,
                                                downsampleRatio,
                                                sizeOfOneBuffer)
    assert_pico_ok(status["runStreaming"])
    
    # We need a big buffer, not registered with the driver, to keep our complete capture in.
    global bufferCompleteA 
    global bufferCompleteB 
    global nextSample 
    global autoStopOuter 
    global wasCalledBack 
    global cFuncPtr 
    
    bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
    bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
    nextSample = 0
    autoStopOuter = False
    wasCalledBack = False
    cFuncPtr = ps.StreamingReadyType(streaming_callback)
    
    while nextSample < totalSamples and not autoStopOuter:
        wasCalledBack = False
        status["getStreamingLastestValues"] = ps.ps4000GetStreamingLatestValues(chandle, cFuncPtr, None)
        if not wasCalledBack:
            # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
            # again.
            time.sleep(0.01)
    
    #logging.info("Done grabbing values.")
    
    # Find maximum ADC count value
    # handle = chandle
    # pointer to value = ctypes.byref(maxADC)
    maxADC = ctypes.c_int16(32767)

    # Convert ADC counts data to mV
    adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
    #adc2mVChBMax = adc2mV(bufferCompleteB, channel_range, maxADC)
    
    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps4000Stop(chandle)
    assert_pico_ok(status["stop"])
    
    if plot:
        # Plot data from channel A
        # Create time data
        time_axis = np.linspace(0, (totalSamples) * actualSampleIntervalNs, totalSamples)
        plt.plot(time_axis, adc2mVChAMax[:])
        #plt.plot(time, adc2mVChBMax[:])
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    return round_half_up(mean(adc2mVChAMax[math.floor((len(adc2mVChAMax)-1)*discarded_portion):]),3); #round_half_up(mean(adc2mVChAMax),3);

def pico_stop():
    global status
    
    # Stop the scope
    # handle = chandle
    status["stop"] = ps.ps4000Stop(chandle)
    assert_pico_ok(status["stop"])    

    # Disconnect the scope
    # handle = chandle
    status["close"] = ps.ps4000CloseUnit(chandle)
    assert_pico_ok(status["close"])
    return;


# ## To Do

# In[ ]:


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

