# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 10:46:19 2020
@author: Rhapsody
Utility: Pi Pulse Calibration
"""

import sys
sys.path.append('D:\\Rhapsody\\Programs\\Zurich Instrument Qubit Characterization 2')
from PSG_E8257D import PSG_E8257D
from UHFQA import zurich_qa
from HDAWG import zurich_awg
from MongoDB import mongodb
from DP800 import DP800
import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time


mw_generator_ip_1 = 'TCPIP0::192.168.10.106::inst0::INSTR'
mw_generator_ip_2 = 'TCPIP0::192.168.10.219::inst0::INSTR'
#dc_ip_1 = 'USB0::0x1AB1::0x0E11::DP8C204504949::INSTR'


MW_GENERATOR_1 = PSG_E8257D(mw_generator_ip_1)
MW_GENERATOR_2 = PSG_E8257D(mw_generator_ip_2)
#DC_1 = DP800(dc_ip_1)

#%%  #---------------Pi Pulse校准参数设置-----------------------------
"""基本参数设置"""
uhfqa_id = 'dev2534'
hdawg_id = 'dev8252'
base_freq_probe = 6.5 #Probe基频

#osc_freq_probe = 279.5e6 #Q2
#osc_freq_probe = 219.4e6 #Q4
#osc_freq_probe = 219.4e6 #Q4
#osc_freq_probe = 105.8e6 #Q8
#osc_freq_probe = 165.9e6 #C2
#osc_freq_probe = 222.1e6 #C3
#osc_freq_probe = 223.0e6 #C3
#osc_freq_probe = 223.127e6 #C3 V_Dc-Q4 0.42V
#osc_freq_probe = 449.7e6 #C3
#osc_freq_probe = 113.3e6 #C1
#osc_freq_probe = 275.660e6 #
#osc_freq_probe = 275.581e6 #C4   #Flux = 0.42V
#osc_freq_probe = 275.518e6 #C4
#osc_freq_probe = 275.037e6 #C4 flux = 0.6V
#osc_freq_probe = 275.624e6 #C4
#osc_freq_probe = 275.60e6 #C4
#osc_freq_probe = 334.80e6 #C5
#osc_freq_probe = 570.8e6 #C9
#osc_freq_probe = 450.26e6 #C7
#osc_freq_probe = 387.2e6 #C6
osc_freq_probe = 509.001e6 #C8

#base_freq_drive = 5.06335 #Q2
#base_freq_drive = 4.89800 #Q4
#base_freq_drive = 4.91582 #Q8
#base_freq_drive = 4.91590 #Q8 #2021/0513 重校
#base_freq_drive = 4.7104 #C2
#base_freq_drive = 6.4230 #C2
#base_freq_drive = 4.0330#C1
#base_freq_drive = 4.696#C4
#base_freq_drive = 4.320#C4
#base_freq_drive = 4.6865#C4 0610重校
#base_freq_drive = 4.680#C4
#base_freq_drive = 4.443#c4
#base_freq_drive = 4.335 #c3
#base_freq_drive = 4.4269 #c3
#base_freq_drive = 4.5389 #c3
#base_freq_drive = 4.4560 #c3
#base_freq_drive = 4.377 #c3
#base_freq_drive = 4.253 #Q4  AWG_OFFSET=0.5V
#base_freq_drive = 4.69852#C4 重校
#base_freq_drive = 4.604#C4 重校
#base_freq_drive = 3.782#C4 重校
#base_freq_drive = 4.380#C5
#base_freq_drive = 4.6250#C5
#base_freq_drive = 4.7630#C9
#base_freq_drive = 4.7408#C9
#base_freq_drive = 4.5609#C7
#base_freq_drive = 4.533 #C7
#base_freq_drive = 4.7595#C6
base_freq_drive = 4.70897#C8
#base_freq_drive = 4.717#C8 QS_peak_2

osc_freq_drive = 300.0e6 #加上基频为比特频率

#base_power_probe = -11 #Q2
#base_power_probe = -6 #Q4
#base_power_probe = -5 #C2
#base_power_probe = -12 #C1
#base_power_probe = -12 #C4
#base_power_probe = -12 #C5
#base_power_probe = -3 #C5
#base_power_probe = -7 #C7
#base_power_probe = -6 #C6
#base_power_probe = -3 #C9
#base_power_probe = -12 #C4
base_power_probe = -6 #C8

#base_power_drive = 0 #Q2
#base_power_drive = -5 #Q4
#base_power_drive = 5#C2
#base_power_drive = 16#C3
#base_power_drive = -10#C1
#base_power_drive = 14#C4
#base_power_drive = 11#C5
#base_power_drive = 15#C9
#base_power_drive = 10#C7
#base_power_drive = 10#C6
base_power_drive = 16#C6

result_length_pulse = 80
result_length_power = 5
result_length = result_length_pulse*result_length_power

time_origin_sec = 6000.0e-9 #UHFQA和HDAWG 此处相同

num_averages_uhfqa = 1024 # 2^N
num_averages_hdawg = 1   # 2^N


amplitude_probe = 1.0 #probe 波形前乘以的系数，与amplitude_probe_1同样起到调节probe power的作用，实际probe power应为amplitude_probe_1*amplitude_probe_2*base_power
amplitude_drive = 0.8
amplitude_dc = 1.0

period_wait_sec = 600e-6
square_wave_sec_dc = 4e-6
#drive_wave_width_sec = 9.0e-9 #step length of gauss pulse  单位：s
#drive_pulse_width_sec = 3.0e-9 #step standard deviation of gauss pulse  单位：s
drive_wave_width_sec = 3.0e-9 #step length of gauss pulse  单位：s
drive_pulse_width_sec = 1.0e-9 #step standard deviation of gauss pulse  单位：s

data_ch_1 = []
data_ch_2 = []
samp_rate = 1.8e9 # 采样率1.8GHz  
t_sec = 2e-6  #对probe结果采取的积分长度，单位：s
read_length = np.floor(t_sec*samp_rate/8)*8  #积分长度，按点数计，取整数

#dc_voltage = 0.42 #直流电压偏置 /V
dc_voltage = 0.1 #直流电压偏置 /V

data_ch_1 = []
data_ch_2 = []
samp_rate = 1.8e9 # 采样率1.8GHz  
t_sec = 2e-6  #对probe结果采取的积分长度，单位：s
read_length = np.floor(t_sec*samp_rate/8)*8  #积分长度，按点数计，取整数

print('DC Voltage: ', dc_voltage, 'V \n')
print('Local Power Probe:  ', base_power_probe, 'dBm', '\n')
print('Local Power Drive:  ', base_power_drive, 'dBm', '\n')
print('Probe Frequency:  ', base_freq_probe+osc_freq_probe/1e9, 'GHZ \n')
print('Drive Frequency:  ', base_freq_drive+osc_freq_drive/1e9, 'GHz \n')

#%%------------Pi Pulse 校准 时序1-------------------

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive)
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)

hdawg.result_length = result_length
hdawg.result_length_pulse = result_length_pulse
hdawg.result_length_power = result_length_power

hdawg.num_averages = num_averages_hdawg
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=dc_voltage)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc
hdawg.amplitude_drive = amplitude_drive

#设置drive pulse长度
hdawg.wave_width_sec = drive_wave_width_sec
hdawg.pulse_width_sec = drive_pulse_width_sec
#设置dc pulse长度
hdawg.square_wave_sec_dc = square_wave_sec_dc

hdawg.set_osc(osc_path=0, freq=osc_freq_drive) #根据能谱得到的比特频率
#hdawg.set_osc(osc_path=0, freq=osc_freq_drive) #Ramsey 校正后的比特频率

#设置drive通道和偏置通道的输出量程
hdawg.set_output_range(channel=0, range=0.40)
hdawg.set_output_range(channel=1, range=0.40)
hdawg.set_output_range(channel=2, range=1.0)
hdawg.set_output_range(channel=3, range=1.0)

#打开HDAWG要用的通道
hdawg.channel_close(channel='*')
hdawg.channel_open(channel='0') 
hdawg.channel_open(channel='1')
hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#设置HDAWG OFFSET， 即直流偏置
hdawg.set_offset(channel=2, offset=0.1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译HDAWG awg sequence
hdawg.awg_builder_picali() #变gauss pulse长度

#Run HDAWG awg Drive/DC sequence,等待触发
hdawg.awg_open(awgcore=0)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.num_averages = num_averages_uhfqa
uhfqa.period_wait_sec = period_wait_sec

#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)


uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1 )
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0 )
uhfqa.set_result_path(source = 2) # 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置震荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_picali()

#Run UHFQA awg sequence
uhfqa.daq.sync()
uhfqa.awg_open()

#采集数据
data_temp = uhfqa.get_result(do_plot=0)
data_ch_1 = data_temp[uhfqa.paths[0]] #实部
data_ch_2 = data_temp[uhfqa.paths[1]] #虚部  
data = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
data_2D = data.reshape(result_length_power, result_length_pulse)


"""UHFQA/HDAWG Channel Off/Sequence Stop """
hdawg.awg_close(awgcore=0)
hdawg.awg_close(awgcore=1)
hdawg.channel_close(channel='*')

uhfqa.awg_close()
uhfqa.channel_close()


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off()  


"""画图初步""" 
fig, ax = plt.subplots(figsize=(16, 12))
ax.set_ylabel('DC Voltage /V', fontsize=16)
ax.set_xlabel('time step', fontsize=16)
ax.set_title('Pi Pulse Calibration', fontsize=16)
ax.imshow(data_2D)
 

"""MongoDB存储数据"""
power_array = np.linspace(1, result_length_power, result_length_power)/result_length_power #纵向，amplitude 0->1
pulse_array = np.linspace(1, result_length_pulse, result_length_pulse)*drive_wave_width_sec*1e6  #横向，单位：us
result = [{'pulse_list':(pulse_array).tolist()}, {'power_list':(power_array).tolist()}, {'picali':data_2D.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_picali(result)

#%%  Pi Pulse Calibration Old

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive)
MW_GENERATOR_2.turn_on()


"""设置直流源"""
DC_1.set_value(ch=2, offset=0.3)
DC_1.turn_on(ch=2)
DC_1.get_state(ch=2)
time.sleep(0.2)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.num_averages = num_averages_uhfqa
uhfqa.period_wait_sec = period_wait_sec
uhfqa.amplitude_probe_1 = amplitude_probe_1
uhfqa.amplitude_probe_2 = amplitude_probe_2
uhfqa.result_length_pulse = result_length_pulse
uhfqa.result_length_power = result_length_power


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.result_length_pulse = result_length_pulse
hdawg.result_length_power = result_length_power
hdawg.num_averages = num_averages_hdawg # 2^N
hdawg.time_origin_sec = time_origin_sec
hdawg.wave_width_sec = drive_wave_width_sec
hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.amplitude_drive_1 = amplitude_drive_1
hdawg.set_relative_amplitude()
hdawg.set_osc(osc_freq_drive)  #加上Drive基频等于比特频率

hdawg.awg_builder_picali()
hdawg.daq.sync()
hdawg.awg_open()


"""UHFQA初始化,Sequence编译"""
uhfqa.set_demodulation_default()
uhfqa.spectroscopy(mode_on = 1)
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length)

uhfqa.awg_builder_picali()








"""Sequence执行,开始触发hdawg,采集数据 """
uhfqa.set_osc(osc_freq_probe)
uhfqa.daq.sync()
uhfqa.awg_open()
data_temp = uhfqa.get_result(do_plot=0)
data_ch_1 = data_temp[uhfqa.paths[0]] #实部
data_ch_2 = data_temp[uhfqa.paths[1]] #虚部
print(len(data_ch_1))
print(len(data_ch_2))
data = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
print(len(data))
data_2D = data.reshape(result_length_power, result_length_pulse)


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off()  


"""关闭直流源"""
time.sleep(0.2)
DC_1.turn_off(ch=1)


"""画图初步""" 
plt.figure('Pi Pulse Calibration')
plt.imshow(data_2D)
plt.title('Pi Pulse Calibration') # 图像题目

plt.figure('qubit spectroscpy')
plt.plot(np.array(data))

 
"""MongoDB存储数据"""
power_array = np.linspace(1, result_length_power, result_length_power)/result_length_power #纵向，amplitude 0->1
pulse_array = np.linspace(1, result_length_pulse, result_length_pulse)*drive_wave_width_sec*1e6  #横向，单位：us
result = [{'pulse_list':(pulse_array).tolist()}, {'power_list':(power_array).tolist()}, {'picali':data_2D.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_picali(result)


"""test"""
print(len(data_2D))
for i in range(len(data_2D)):
    print(len(data_2D[i]))
    print(type(data_2D[i]))


