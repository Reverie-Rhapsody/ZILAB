# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 23:10:51 2020

@author: Rhapsody

------测Vacuum Rabi震荡------

------时序1如下------
       ________________
______|    Pi Pulse   |___________________________________________________________________

                        _______________________________________________
_______________________| [Q4] AWG DC Pulse [change length/amplitude］ |___________________
                                            
   _____________________________________________________________________________________           
__|                          [Q4] AWG OFFSET fixed at Idle Frequency                   |__
                                       
     _______________________________________________________________________________
____|                    [Q3] AWG OFFSET [freq fixed]                                |______                           
                                                                  ______________
_________________________________________________________________| Probe Pulse |__________


------时序2如下------
   ____________________________________________
__|                 DC Pulse                  |__________
         ______________
________| Drive Pulse |_________________________________
                       ______________
______________________| Probe Pulse |___________________ 


------时序3如下------
   ____________________________________________
__|                DC OFFSET                  |__________
         ______________
________| Drive Pulse |_________________________________
                       ______________
______________________| Probe Pulse |___________________ 

"""

#%%   #头文件

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

#%%   #—————————测Rabi———参数设置————————————

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
#osc_freq_probe = 449.7e6 #C3
#osc_freq_probe = 113.3e6 #C1
#osc_freq_probe = 275.660e6 #C4
#osc_freq_probe = 275.037e6 #C4 flux = 0.
#osc_freq_probe = 275.396e6 #C4 flux = 0.6V
osc_freq_probe = 275.581e6 #C4   #Flux = 0.42V
#osc_freq_probe = 275.60e6 #C4
#osc_freq_probe = 334.80e6 #C5
#osc_freq_probe = 570.8e6 #C9
#osc_freq_probe = 450.26e6 #C7
#osc_freq_probe = 387.2e6 #C6

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
#base_freq_drive = 4.377 #c3
#base_freq_drive = 3.782#C4 flux=0.6V
base_freq_drive = 4.253 #Q4  AWG_OFFSET=0.5V
#base_freq_drive = 4.69852#C4 重校
#base_freq_drive = 4.380#C5
#base_freq_drive = 4.6250#C5
#base_freq_drive = 4.7630#C9
#base_freq_drive = 4.7408#C9
#base_freq_drive = 4.5609#C7
#base_freq_drive = 4.533 #C7
#base_freq_drive = 4.7595#C6

osc_freq_drive = 300.0e6 #加上基频为比特频率

#base_power_probe = -11 #Q2
#base_power_probe = -6 #Q4
#base_power_probe = -5 #C2
#base_power_probe = -12 #C1
base_power_probe = -12 #C4
#base_power_probe = -12 #C5
#base_power_probe = -3 #C5
#base_power_probe = -7 #C7
#base_power_probe = -6 #C6
#base_power_probe = -3 #C9

#base_power_drive = 0 #Q2
#base_power_drive = -5 #Q4
#base_power_drive = 5#C2
#base_power_drive = 0#C3
#base_power_drive = -10#C1
base_power_drive = 16#C4
#base_power_drive = 11#C5
#base_power_drive = 15#C9
#base_power_drive = 10#C7
#base_power_drive = 10#C6

result_length = 40 #UHFQA和HDAWG 此处相同
time_origin_sec = 6000.0e-9 #UHFQA和HDAWG 此处相同
num_averages_uhfqa = 2048 # 2^N
num_averages_hdawg = 1   # 2^N


amplitude_probe = 1.0 #probe 波形前乘以的系数，与amplitude_probe_1同样起到调节probe power的作用，实际probe power应为amplitude_probe_1*amplitude_probe_2*base_power
amplitude_drive = 0.6
amplitude_dc = 1.0

period_wait_sec = 600e-6
square_wave_sec_dc = 2e-9
#drive_wave_width_sec = 9.0e-9 #step length of gauss pulse  单位：s
#drive_pulse_width_sec = 3.0e-9 #step standard deviation of gauss pulse  单位：s
drive_wave_width_sec = 32.28e-9 #step length of gauss pulse  单位：s
drive_pulse_width_sec = 10.76e-9 #step standard deviation of gauss pulse  单位：s

samp_rate = 1.8e9 # 采样率1.8GHz  
t_sec = 2e-6  #对probe结果采取的积分长度，单位：s
read_length = np.floor(t_sec*samp_rate/8)*8  #积分长度，按点数计，取整数

dc_voltage_1 = 0.00 #直流电压偏置 /V
dc_voltage_2 = 0.00 #直流电压偏置 /V
#dc_voltage_list = np.linspace(0.41, 0.43, 6) #直流电压输出列表
#dc_voltage_list = np.linspace(-0.06, -0.10, 5) #直流电压输出列表
#dc_voltage_list = np.linspace(-0.02, -0.09, 29) #直流电压输出列表
dc_voltage_list = np.linspace(-0.07, -0.11, 13) #直流电压输出列表

print('DC Voltage 1: ', dc_voltage_1, 'V \n')
print('DC Voltage 2: ', dc_voltage_2, 'V \n')
print('Local Power Probe:  ', base_power_probe, 'dBm', '\n')
print('Local Power Drive:  ', base_power_drive, 'dBm', '\n')
print('Probe Frequency:  ', base_freq_probe+osc_freq_probe/1e9, 'GHZ \n')
print('Drive Frequency:  ', base_freq_drive+osc_freq_drive/1e9, 'GHz \n')

#%%   #—————测真空Rabi———————时序1————————————

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

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude_single(awgcore=1, channel=0, amplitude=dc_voltage_1)
hdawg.set_total_amplitude_single(awgcore=1, channel=1, amplitude=dc_voltage_2)

hdawg.set_offset(channel=2, offset=0.5)
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
hdawg.channel_open(channel='2')
hdawg.channel_open(channel='3')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译HDAWG awg sequence
hdawg.awg_builder_vacuum_rabi_drive() #变gauss pulse长度
#hdawg.awg_builder_rabi()  #变amplitude
hdawg.awg_builder_vacuum_rabi_flux()

#Run HDAWG awg Drive/DC sequence,等待触发

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


data = []
fig, ax = plt.subplots(figsize=(16,12))
ax.set_ylabel('Voltage /V', fontsize=16)
ax.set_xlabel('Time/ns', fontsize=16)
ax.set_title('Vacuum Rabi', fontsize=16)
time_x = (np.arange(hdawg.result_length))*hdawg.square_wave_sec_dc*1e9
for voltage in dc_voltage_list:
    data_ch_1 = []
    data_ch_2 = []
    
    hdawg.set_total_amplitude(awgcore=1, amplitude=voltage)
    
    hdawg.daq.sync()
    hdawg.awg_open(awgcore=0) #Run HDAWG awg core 1 sequence
    hdawg.awg_open(awgcore=1) #Run HDAWG awg core 2 sequence
    uhfqa.daq.sync()
    uhfqa.awg_open() #Run UHFQA awg sequence
    
    #采集数据
    data_temp = uhfqa.get_result(do_plot=0)
    data_ch_1 = data_temp[uhfqa.paths[0]] #实部
    data_ch_2 = data_temp[uhfqa.paths[1]] #虚部  
    print('------------')
    print(len(data_ch_1))
    print('------------')
    data_1 = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
    ax.plot(time_x, data_1)
    data.append(data_1)


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
print(len(data))
new_data=data[::-1]

time_x = (np.arange(hdawg.result_length))*hdawg.square_wave_sec_dc*1e9
fig, ax = plt.subplots(figsize=(16,12))
ax.set_ylabel('DC Voltage /V', fontsize=16)
ax.set_xlabel('Time/ns', fontsize=16)
ax.set_title('Vacuum Rabi', fontsize=16)
extent = [np.min(time_x), np.max(time_x), np.min(dc_voltage_list+0.5), np.max(dc_voltage_list+0.5)]
ax.imshow(new_data, aspect='auto', extent = extent, origin='lower', interpolation='nearest')
        
print(data)

"""MongoDB存储数据"""
# result = [{'time_x':np.linspace(0,(hdawg.result_length-1)*hdawg.wave_width_sec,hdawg.result_length).tolist()},{'rabi_real':data_ch_1.tolist()},{'rabi_imag':data_ch_2.tolist()}]
# database_host = 'mongodb://localhost:27017/'
# database = mongodb(database_host)
# database.save_rabi(result)    

#%%   #—————测Rabi———————时序2————————————

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
hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译HDAWG awg sequence
hdawg.awg_builder_rabi_t() #变gauss pulse长度
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
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('time step', fontsize=20)
ax.set_title('Rabi', fontsize=20)
#plt.figure('qubit spectroscpy')
plt.plot(np.array(data))
 

"""MongoDB存储数据"""
result = [{'time_x':np.linspace(0,(hdawg.result_length-1)*hdawg.wave_width_sec,hdawg.result_length).tolist()},{'rabi_real':data_ch_1.tolist()},{'rabi_imag':data_ch_2.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_rabi(result)

#%%   #—————测Rabi———————时序3————————————

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

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
#hdawg.set_total_amplitude(awgcore=1, amplitude=dc_voltage)
#设置单个pulse的amplitde
hdawg.amplitude_drive = amplitude_drive
#hdawg.amplitude_dc = amplitude_dc

#设置HDAWG偏置通道的offset
hdawg.set_offset(channel=2, offset=dc_voltage)

#设置drive pulse长度
hdawg.wave_width_sec = drive_wave_width_sec
hdawg.pulse_width_sec = drive_pulse_width_sec
#设置dc pulse长度
#hdawg.square_wave_sec_dc = square_wave_sec_dc

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
hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译HDAWG awg sequence
hdawg.awg_builder_rabi_t() #变gauss pulse长度
#hdawg.awg_builder_rabi()  #变amplitude
#hdawg.awg_builder_flux()

#Run HDAWG awg Drive/DC sequence,等待触发
hdawg.awg_open(awgcore=0)
#hdawg.awg_open(awgcore=1)


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


"""UHFQA/HDAWG Channel Off/Sequence Stop"""
hdawg.awg_close(awgcore=0)
#hdawg.awg_close(awgcore=1)
hdawg.channel_close(channel='*')

uhfqa.awg_close()
uhfqa.channel_close()


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off()  


"""画图初步""" 
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('time step', fontsize=20)
ax.set_title('Rabi', fontsize=20)
#plt.figure('qubit spectroscpy')
plt.plot(np.array(data))
 

"""MongoDB存储数据"""
result = [{'time_x':np.linspace(0,(hdawg.result_length-1)*hdawg.wave_width_sec,hdawg.result_length).tolist()},{'rabi_real':data_ch_1.tolist()},{'rabi_imag':data_ch_2.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_rabi(result)   



