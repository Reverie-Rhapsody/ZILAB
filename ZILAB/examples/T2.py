# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 11:14:36 2020

@author: Rhapsody
"""

from ZILAB.driver.UHFQA import zurich_qa
from ZILAB.driver.HDAWG import zurich_awg
from ZILAB.driver.PSG_E8257D import PSG_E8257D
from ZILAB.driver.DP800 import DP800
from ZILAB.db.MongoDB import mongodb

import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time


mw_generator_ip_1 = 'TCPIP0::192.168.10.106::inst0::INSTR'
mw_generator_ip_2 = 'TCPIP0::192.168.10.219::inst0::INSTR'
dc_ip_1 = 'USB0::0x1AB1::0x0E11::DP8C204504949::INSTR'


MW_GENERATOR_1 = PSG_E8257D(mw_generator_ip_1)
MW_GENERATOR_2 = PSG_E8257D(mw_generator_ip_2)
DC_1 = DP800(dc_ip_1)

#%%
"""基本参数设置"""
uhfqa_id = 'dev2534'
hdawg_id = 'dev8252'

base_freq_probe = 6.5 #Probe基频

#osc_freq_probe = 334.8e6 #C5 
#osc_freq_probe = 279.5e6 #Q2
#osc_freq_probe = 165.9e6 #C2 
#osc_freq_probe = 275.8e6 #C4 
#osc_freq_probe = 275.037e6 #C4 flux = 0.6V
#osc_freq_probe = 223.0e6 #C3
#osc_freq_probe = 223.127e6 #C3 V_Dc-Q4 0.42V
#osc_freq_probe = 570.8e6 #C9 
#osc_freq_probe = 450.5e6 #C7
#osc_freq_probe = 113.3e6 #C1
#osc_freq_probe = 165.9e6 #C2
#osc_freq_probe = 387.9e6 #C6
osc_freq_probe = 509.001e6 #C8  #V_DC-Q9= 0.1V

#base_freq_drive = 5.06335 #Q2
#base_freq_drive = 4.7104 #C2
#base_freq_drive = 4.69852#C4
#base_freq_drive = 3.7775#C4 重校
#base_freq_drive = 4.3345#C3
#base_freq_drive = 4.3775#C3
#base_freq_drive = 4.65662#C5
#base_freq_drive = 4.7408#C9
#base_freq_drive = 4.5619#C7
#base_freq_drive = 4.0330 #C1
#base_freq_drive = 4.7104 #C2
#base_freq_drive = 4.7627#C6
#base_freq_drive = 4.4269 #c3
#base_freq_drive = 4.4560 #c3
#base_freq_drive = 4.458645 #c3
#base_freq_drive = 4.453355 #c3
base_freq_drive = 4.70897#C8   #V_DC-Q9= 0.1V

osc_freq_drive = 300.0e6 #加上基频为比特频率

#base_power_probe = -11 #Q2
#base_power_probe = -10#Q8
#base_power_probe = -3#c9
#base_power_probe = -12#c3
#base_power_probe = -5 #C7
#base_power_probe = -12 #C1
#base_power_probe = -5 #C2
#base_power_probe = -6 #C6
base_power_probe = -6 #C6

#base_power_drive = 0 #Q2
#base_power_drive = 10 #Q8
#base_power_drive = 10#C7
#base_power_drive = 5#C1
#base_power_drive = 5#C2
#base_power_drive = 10#C6
base_power_drive = 16#C6

result_length =50 #UHFQA和HDAWG 此处相同
#time_origin_sec = 2000.0e-9 #UHFQA和HDAWG 此处相同
num_averages_uhfqa = 1024 # 2^N
num_averages_hdawg = 1   # 2^N
period_wait_sec = 1000e-6 
time_origin_sec = 100000.0e-9 #UHFQA和HDAWG 此处相同


#amplitude_probe_1 = 0.133 #uhfqa的awg输出波形的振幅系数，值为`1.0`则表示`1.0*range`应设为变功率测量得到合适的dispersive范围amplitude
#amplitude_probe_2 = 1.0 #probe 波形前乘以的系数，与amplitude_probe_1同样起到调节probe power的作用，实际probe power应为amplitude_probe_1*amplitude_probe_2*base_power
#amplitude_drive_1 = 1.0
#amplitude_drive_2 = 0.5 #Pi pulse前面乘的系数 

amplitude_probe = 1.0 #probe 波形前乘以的系数，与amplitude_probe_1同样起到调节probe power的作用，实际probe power应为amplitude_probe_1*amplitude_probe_2*base_power
amplitude_drive = 0.5
amplitude_dc = 1.0

#drive_wave_width_sec = 118.49e-9 #length of gauss pulse 单位：s
#drive_pulse_width_sec = 39.49e-9 #standard deviation of gauss pulse 单位：s
#drive_wave_width_sec = 36.97e-9 #length of gauss pulse 单位：s C4
#drive_pulse_width_sec = 12.323e-9 #standard deviation of gauss pulse 单位：s C4
#drive_wave_width_sec = 66.37e-9 #length of gauss pulse 单位：s C7
#drive_pulse_width_sec = 22.123e-9 #standard deviation of gauss pulse 单位：s C7
#drive_wave_width_sec = 114.03e-9 #length of gauss pulse 单位：s C1
#drive_pulse_width_sec = 38.01e-9 #standard deviation of gauss pulse 单位：s C1
#drive_wave_width_sec = 118.49e-9 #length of gauss pulse 单位：s C1
#drive_pulse_width_sec = 39.50e-9 #standard deviation of gauss pulse 单位：s C1
#drive_pulse_width_sec = 10.12e-9 #standard deviation of gauss pulse 单位：s C6
#drive_wave_width_sec = 36.97e-9 #length of gauss pulse 单位：s C6
#drive_pulse_width_sec = 12.32e-9 #standard deviation of gauss pulse 单位：s C6
#drive_wave_width_sec = 23.11e-9 #length of gauss pulse 单位：s C9
#drive_pulse_width_sec = 7.61e-9 #standard deviation of gauss pulse
#drive_wave_width_sec = 22.80e-9 #length of gauss pulse 单位：s C3
#drive_pulse_width_sec = 7.60e-9 #standard deviation of gauss pulse 单位：s C3
#drive_wave_width_sec = 36.00e-9 #length of gauss pulse 单位：s C3
#drive_pulse_width_sec = 12.0e-9 #standard deviation of gauss pulse 单位：s C3
#drive_wave_width_sec = 31.85e-9 #length of gauss pulse 单位：s C3
#drive_pulse_width_sec = 10.62e-9 #standard deviation of gauss pulse 单位：s C3
drive_wave_width_sec = 19.51e-9 #length of gauss pulse 单位：s C8
drive_pulse_width_sec = 6.50e-9 #standard deviation of gauss pulse 单位：s C8


square_wave_sec_dc = 4e-6
dc_voltage = 0.1 #直流电压偏置 /V

#time_increment = 2 #测T2每次增加的时间长度，为1.8GHz采样率下设置点数对应的时间长度
time_increment = 5#测T2每次增加的时间长度，为1.8GHz采样率下设置点数对应的时间长度 C1

detuning = 0e6 #失谐，单位Hz
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


#%% #—————测T2———————old————————————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive)
MW_GENERATOR_2.turn_on()


"""设置直流源"""
DC_1.set_value(ch=1, offset=0.25)
DC_1.turn_on(ch=1)
DC_1.get_state(ch=1)
time.sleep(0.2)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.num_averages = num_averages_uhfqa # 2^N
uhfqa.period_wait_sec = period_wait_sec
uhfqa.time_origin_sec = time_origin_sec
uhfqa.amplitude_probe_1 = amplitude_probe_1
uhfqa.amplitude_probe_2 = amplitude_probe_2
uhfqa.set_relative_amplitude()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.num_averages = num_averages_hdawg # 2^N
hdawg.wave_width_sec = drive_wave_width_sec
hdawg.pulse_width_sec = drive_pulse_width_sec
hdawg.time_origin_sec = time_origin_sec
hdawg.time_increment = time_increment
hdawg.amplitude_drive_1 = amplitude_drive_1
hdawg.amplitude_drive_2 = amplitude_drive_2
hdawg.set_relative_amplitude()
hdawg.set_osc((osc_freq_drive+detuning))
hdawg.awg_builder_T2()
hdawg.daq.sync()
hdawg.awg_open()


"""UHFQA初始化,Sequence编译"""
uhfqa.set_demodulation_default()
uhfqa.spectroscopy(mode_on = 1)
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1 )
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0 )
uhfqa.set_result_path(source = 2 )# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length)
uhfqa.awg_builder_general()


"""Sequence执行,开始触发hdawg,采集数据 """
uhfqa.set_osc(osc_freq_probe)
uhfqa.daq.sync()
uhfqa.awg_open()
data_temp = uhfqa.get_result(do_plot=0)
data_ch_1 = data_temp[uhfqa.paths[0]] #实部
data_ch_2 = data_temp[uhfqa.paths[1]] #虚部      
data = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off() 


"""关闭直流源"""
time.sleep(0.2)
DC_1.turn_off(ch=1)  


"""画图初步""" 
plt.figure('qubit spectroscpy')
plt.plot(np.array(data))
plt.title('image') # 图像题目

  
"""MongoDB存储数据"""
result = [{'time_x':np.linspace(0, hdawg.result_length-1, hdawg.result_length).tolist()},{'T2_real':data_ch_1.tolist()},{'T2_imag':data_ch_2.tolist()},{'time_increment':hdawg.time_increment},{'detuning':detuning*(1e6)}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_T2(result)


#%% #—————测T2———————时序2————————————
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
hdawg.num_averages = num_averages_hdawg
hdawg.time_origin_sec = time_origin_sec
hdawg.time_increment = time_increment

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
hdawg.set_output_range(channel=0, range=0.4)
hdawg.set_output_range(channel=1, range=0.4)
hdawg.set_output_range(channel=2, range=1.0)
hdawg.set_output_range(channel=3, range=1.0)

#打开HDAWG要用的通道
hdawg.channel_close(channel='*')
hdawg.channel_open(channel='0') 
hdawg.channel_open(channel='1')
#hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译HDAWG awg sequence
hdawg.awg_builder_T2() #变gauss pulse长度
#hdawg.awg_builder_rabi()  #变amplitude
hdawg.awg_builder_flux_2()

#Run HDAWG awg Drive/DC sequence,等待触发
hdawg.awg_open(awgcore=0)
hdawg.awg_open(awgcore=1)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.num_averages = num_averages_uhfqa
uhfqa.period_wait_sec = period_wait_sec

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

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
uhfqa.awg_builder_general()

#Run UHFQA awg sequence
uhfqa.awg_open()

#采集数据
data_temp = uhfqa.get_result(do_plot=0)
data_ch_1 = data_temp[uhfqa.paths[0]] #实部
data_ch_2 = data_temp[uhfqa.paths[1]] #虚部  
data = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))


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
fig, ax = plt.subplots(figsize=(16,12))
ax.set_ylabel('DC Voltage /V', fontsize=16)
ax.set_xlabel('time step', fontsize=16)
ax.set_title('T2', fontsize=16)
#plt.figure('qubit spectroscpy')
plt.plot(np.array(data))
 

"""MongoDB存储数据"""
result = [{'time_x':np.linspace(0, hdawg.result_length-1, hdawg.result_length).tolist()},{'T2_real':data_ch_1.tolist()},{'T2_imag':data_ch_2.tolist()},{'time_increment':hdawg.time_increment},{'detuning':detuning*(1e6)}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_T2(result)


    
