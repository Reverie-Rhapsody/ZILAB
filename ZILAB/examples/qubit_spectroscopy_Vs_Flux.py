# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:29:39 2020

@author: Rhapsody

------测能谱调制------

------时序1如下------
       ________________
______| DC Pulse      |___________________
         ______________
________| Drive Pulse |___________________
                       ______________
______________________| Probe Pulse |_____ 


------时序2如下------
       ________________________________________
______|             DC Pulse                  |_______
         ______________
________| Drive Pulse |_______________________________
                       ______________
______________________| Probe Pulse |_________________



------时序3如下------
       ________________________________________
______|             DC OFFSET                 |_______
         ______________
________| Drive Pulse |_______________________________
                       ______________
______________________| Probe Pulse |_________________

"""

#%%   #头文件
import sys
sys.path.append('D:\\Rhapsody\\Programs\\Zurich Instrument Qubit Characterization 2')
from PSG_E8257D import PSG_E8257D,PSG_E8257D_2
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
MW_GENERATOR_2 = PSG_E8257D_2(mw_generator_ip_2)
#DC_1 = DP800(dc_ip_1)

#%%   #基本参数设置

"""基本参数设置"""

#仪器ID
uhfqa_id = 'dev2534'
hdawg_id = 'dev8252'

base_freq_probe = 6.5

#osc_freq_probe = 165.9e6 #C2 
#osc_freq_probe = 222.1e6 #C3 
#osc_freq_probe = 223.114e6 #C3 V_Dc-Q4 0.42V
#osc_freq_probe = 223.128e6 #C3 V_Dc-Q4 0.42V  Prime
#osc_freq_probe = 223.127e6 #C3 V_Dc-Q4 0.6V
#osc_freq_probe = 222.917e6 #C3 
#osc_freq_probe = 450.5e6 #C7
#osc_freq_probe = 113.3e6 #C1
#osc_freq_probe = 275.660e6 #C4  #不加磁通的固定点
#osc_freq_probe = 272.452e6 #C4  #不加磁通的固定点
#osc_freq_probe = 275.581e6 #C4   #Flux = 0.42V
#osc_freq_probe = 275.518e6 #C4   #Flux = 0V
#osc_freq_probe = 275.60e6 #C4   #Flux:0.25V 
#osc_freq_probe = 387.9e6 #C6
#osc_freq_probe = 334.0e6 #C5
#osc_freq_probe = 333.962e6 #C5 Flux = 0.42V
#osc_freq_probe = 570.8e6 #C9
osc_freq_probe = 509.001e6 #C8

#base_freq_drive = np.linspace(4.65, 4.72, 211, endpoint = True) #C2
#base_freq_drive = np.linspace(5.5, 6.5, 1001, endpoint = True) #C2
#base_freq_drive = np.linspace(4.9, 5.5, 601, endpoint = True) #C2
#base_freq_drive = np.linspace(4.2, 4.9, 701, endpoint = True) #C2
#base_freq_drive = np.linspace(3.7, 5.7, 2001, endpoint = True) #C3
#base_freq_drive = np.linspace(3.5, 5.0, 1501, endpoint = True) #C3
#base_freq_drive = np.linspace(4.1, 4.3, 201, endpoint = True) #C3

#base_freq_drive = np.linspace(4.5, 4.6, 401, endpoint = True) #C7
#base_freq_drive = np.linspace(4.7, 5.2,1001, endpoint = True) #C7
#base_freq_drive = np.linspace(6.4, 7.0,301, endpoint = True) #C7
#base_freq_drive = np.linspace(5.7, 6.4,351, endpoint = True) #C7
#base_freq_drive = np.linspace(4.6, 5.1,501, endpoint = True) #C7
#base_freq_drive = np.linspace(4.65, 4.85,401, endpoint = True) #C6
#base_freq_drive = np.linspace(4.5, 4.8,301, endpoint = True) #C5
#base_freq_drive = np.linspace(4.4, 4.52, 121, endpoint = True) #C4
#base_freq_drive = np.linspace(4.4, 5.0, 601, endpoint = True) #C4
#base_freq_drive = np.linspace(4.57, 4.87, 301, endpoint = True) #C4
#base_freq_drive = np.linspace(4.2, 5.2,1001, endpoint = True) #C9
#base_freq_drive = np.linspace(4.6, 4.8,401, endpoint = True) #C9
#base_freq_drive = np.linspace(4.65, 4.85,10, endpoint = True) #C6
#base_freq_drive = np.linspace(4.50, 4.80,301, endpoint = True) #C4
#base_freq_drive = np.linspace(3.7, 4.2, 1001, endpoint = True) #C8
base_freq_drive = np.linspace(4.6, 5.1, 1001, endpoint = True) #C8

#osc_freq_drive = 50e6
osc_freq_drive = 300e6

#base_power_probe = -5 #C2 
#base_power_probe = -5 # C3
#base_power_probe = -12 # C3
#base_power_probe = -5# C7
#base_power_probe = -3# C9
#base_power_probe = -12 # C1
#base_power_probe = -10# C4
#base_power_probe = -6# C6
#base_power_probe = -12# C5
base_power_probe = -6# C3

#base_power_drive = -10 # C4
base_power_drive = -10 # C4

time_origin_sec = 46e-6  #time_origin_sec HDAWG与UHFQA相同
period_wait_sec = 100e-6 #控制单个测量周期
result_length = 2000  #UHFQA和HDAWG 此处相同
num_averages = 1  #UHFQA和HDAWG此处相同,不用硬件平均

square_wave_sec_drive = 40e-6 #drive的方波长
square_wave_sec_dc = 42e-6 #直流偏置的方波长

#period_wait_sec = 100e-6
#drive_wave_width_sec = 300.0e-9 #step length of gauss pulse  单位：s
#drive_pulse_width_sec = 150.0e-9 #step standard deviation of gauss pulse  单位：s
#drive_pulse_width_sec = 50.0e-9

amplitude_probe = 1.0
amplitude_drive = 0.5
amplitude_dc = 1.0

range_probe = 1.5

samp_rate = 1.8e9 # 采样率1.8GHz  
t_sec = 2e-6  #对probe结果采取的积分长度，单位：s
read_length = np.floor(t_sec*samp_rate/8)*8  #积分长度，按点数计，取整数

dc_voltage = 0.1
#dc_voltage_list = np.linspace(0.4, 0.7, 3) #直流电压输出列表
#dc_voltage_list = np.linspace(0.40, 0.55, 16) #直流电压输出列表
#dc_voltage_list = np.linspace(0.30, 0.50, 21) #直流电压输出列表
dc_voltage_list = np.linspace(0.00, 0.60, 19) #直流电压输出列表

#0.3-0.5V 21points
#osc_freq_probe_list = [275800000.0, 275800000.0, 275800000.0, 275733333.3333333, 275733333.3333333, 275733333.3333333, 275666666.6666667, 275666666.6666667, 275666666.6666667, 275666666.6666667, 275600000.0, 275600000.0, 275600000.0, 275533333.3333333, 275466666.6666667, 275466666.6666667, 275466666.6666667, 275400000.0, 275400000.0, 275333333.3333333, 275333333.3333333]
#print(len(osc_freq_probe_list))

#0.37-0.47V 21points
#osc_freq_probe_list = [275360000.0, 275480000.0, 275600000.0, 275660000.0, 275660000.0, 275780000.0, 275840000.0, 275840000.0, 275840000.0, 275840000.0, 275780000.0, 275780000.0, 275720000.0, 275660000.0, 275540000.0, 275480000.0, 275360000.0, 275300000.0, 275240000.0, 275120000.0, 275060000.0, 274700000.0, 274880000.0, 274760000.0, 274700000.0, 274640000.0, 274580000.0, 274520000.0, 274460000.0, 274400000.0, 274340000.0]
#print(len(osc_freq_probe_list))
#osc_freq_probe_list = [275660000.0, 275660000.0, 275660000.0, 275660000.0, 275660000.0, 275600000.0, 275600000.0, 275540000.0, 275600000.0, 275600000.0, 275540000.0, 275540000.0, 275540000.0, 275480000.0, 275480000.0, 275480000.0, 275480000.0, 275420000.0, 275420000.0, 275420000.0, 275420000.0]
#print(len(osc_freq_probe_list))
#osc_freq_probe_list = [275540000.0, 275540000.0, 275600000.0, 275600000.0, 275540000.0, 275540000.0] #0.41-0.43V 6points
osc_freq_probe_list = [223100000.0, 223100000.0, 223100000.0, 223100000.0, 223100000.0, 223100000.0, 223000000.0, 223000000.0, 223100000.0, 223100000.0, 223100000.0, 223100000.0, 223100000.0, 223200000.0, 223200000.0, 223200000.0, 223200000.0, 223200000.0, 223200000.0]

print('DC Voltage List:\n', dc_voltage, '\n')
print('Drive Frequency Range [GHz]:\n', [np.min(base_freq_drive*1e9+osc_freq_drive)/1e9,np.max(base_freq_drive*1e9+osc_freq_drive)/1e9], '\n')
print('Drive Frequency Points:  ', len(base_freq_drive), '\n')
print('Local Power Probe:  ', base_power_probe, 'dBm', '\n')
print('Local Power Drive:  ', base_power_drive, 'dBm', '\n')

#%%   #——————Qubit Spectroscopy———时序1———腔固定不动“_“———————————————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=dc_voltage)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc
hdawg.amplitude_drive = amplitude_drive

#设置drive pulse和dc pulse长度
hdawg.square_wave_sec_drive = square_wave_sec_drive
hdawg.square_wave_sec_dc = square_wave_sec_dc

#hdawg.wave_width_sec = drive_wave_width_sec
#hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.set_osc(osc_path=0, freq=osc_freq_drive)

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
#hdawg.channel_open(channel='3')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译AWG sequence
hdawg.awg_builder_spec()
hdawg.awg_builder_flux()


"""新建实例uhfqa,初始化,将设置从Data Server同步到仪器"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置振荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_general()


"""变电压偏置，变微波源频率"""
data = []
data_ch_1 = []
data_ch_2 = []
    
for freq in base_freq_drive:
    MW_GENERATOR_2.set_freq(freq)
    
    hdawg.daq.sync()
    hdawg.awg_open(awgcore=0)
    hdawg.awg_open(awgcore=1)
    uhfqa.daq.sync()
    uhfqa.awg_open()
    
    tmp = uhfqa.get_result(do_plot=0)
    data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
    data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
    print('------------')
    print(len(data_ch_1))
    print('------------')
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
#plt.figure('qubit spectroscpy ')
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
data = np.array(data)

fig, ax = plt.subplots()
ax.set_ylabel('Voltage /V', fontsize=16)
ax.set_xlabel('Frequency (GHz)', fontsize=16)
ax.set_title('Qubit spectroscopy Vs Flux 2D', fontsize=16)
ax.plot(freq_x, data)
# print(type(data))
# print(data)

 
"""MongoDB存储数据"""
result = [{'freq_x':freq_x.tolist()},{'spectroscopy_real':data_ch_1},{'spectroscopy_imag':data_ch_2}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_qubit_spectroscopy(result)


#%%   #——————Qubit Spectroscopy———时序2———注意要考虑腔的移动———————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
#hdawg.set_total_amplitude(awgcore=1, amplitude=dc_voltage)

#hdawg.set_total_amplitude(awgcore=1, amplitude=-0.08)
#hdawg.set_offset(channel=2, offset=0.5)

hdawg.set_total_amplitude(awgcore=1, amplitude=0.0)
hdawg.set_offset(channel=2, offset=0.5)

#hdawg.set_total_amplitude(awgcore=1, amplitude=-0.18)
#hdawg.set_offset(channel=2, offset=0.6)

#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc
hdawg.amplitude_drive = amplitude_drive

#设置drive pulse和dc pulse长度
hdawg.square_wave_sec_drive = square_wave_sec_drive
hdawg.square_wave_sec_dc = square_wave_sec_dc

#hdawg.wave_width_sec = drive_wave_width_sec
#hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.set_osc(osc_path=0, freq=osc_freq_drive)

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

#编译AWG sequence
hdawg.awg_builder_spec()
hdawg.awg_builder_flux_2()


"""新建实例uhfqa,初始化,将设置从Data Server同步到仪器"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置振荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_general()


"""变电压偏置，变微波源频率"""
data = []
data_ch_1 = []
data_ch_2 = []
    
for freq in base_freq_drive:
    MW_GENERATOR_2.set_freq(freq)
    
    hdawg.daq.sync()
    hdawg.awg_open(awgcore=0)
    hdawg.awg_open(awgcore=1)
    uhfqa.daq.sync()
    uhfqa.awg_open()
    
    tmp = uhfqa.get_result(do_plot=0)
    data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
    data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
    print('------------')
    print(len(data_ch_1))
    print('------------')
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
#plt.figure('qubit spectroscpy ')
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
data = np.array(data)

fig, ax = plt.subplots()
ax.set_ylabel('Voltage /V', fontsize=16)
ax.set_xlabel('Frequency (GHz)', fontsize=16)
ax.set_title('Qubit spectroscopy Vs Flux 2D', fontsize=16)
ax.plot(freq_x, data)
# print(type(data))
# print(data)

 
# """MongoDB存储数据"""
# result = [{'freq_x':freq_x.tolist()},{'voltage_y':dc_voltage_list.tolist()},{'qubit_spectroscopy_vs_flux':data.tolist()}]
# database_host = 'mongodb://localhost:27017/'
# database = mongodb(database_host)
# database.save_qubit_spectroscopy(result)

"""MongoDB存储数据"""
result = [{'freq_x':freq_x.tolist()},{'spectroscopy_real':data_ch_1},{'spectroscopy_imag':data_ch_2}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_qubit_spectroscopy(result)



#%%   #——————Qubit Spectroscopy Vs Flux———时序1———腔固定不动“_“———————————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=1.0)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc
hdawg.amplitude_drive = amplitude_drive

#设置drive pulse和dc pulse长度
hdawg.square_wave_sec_drive = square_wave_sec_drive
hdawg.square_wave_sec_dc = square_wave_sec_dc

#hdawg.wave_width_sec = drive_wave_width_sec
#hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.set_osc(osc_path=0, freq=osc_freq_drive)

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

#编译AWG sequence
hdawg.awg_builder_spec()
hdawg.awg_builder_flux()


"""新建实例uhfqa,初始化,将设置从Data Server同步到仪器"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置振荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_general()


"""变电压偏置，变微波源频率"""
data = []
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy', fontsize=20)
for voltage in dc_voltage_list: 
    data_ch_1 = []
    data_ch_2 = []
    
    hdawg.set_total_amplitude(awgcore=1, amplitude=voltage)
    
    for freq in base_freq_drive:
        MW_GENERATOR_2.set_freq(freq)
        
        hdawg.daq.sync()
        hdawg.awg_open(awgcore=0)
        hdawg.awg_open(awgcore=1)
        uhfqa.daq.sync()
        uhfqa.awg_open()
        
        tmp = uhfqa.get_result(do_plot=0)
        data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
        data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
        print('------------')
        print(len(data_ch_1))
        print('------------')
    data_1= np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
    ax.plot(base_freq_drive*1e9+osc_freq_drive,data_1)
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
#plt.figure('qubit spectroscpy ')
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
data = np.array(data)
#plt.plot(freq_x, np.array(data))
#plt.title('image') # 图像题目
#data = np.array(data)
freqx_max = np.max(freq_x)
freqx_min = np.min(freq_x)
print(freqx_max,freqx_min)

dc_Vmax = np.max(dc_voltage) 
dc_Vmin = np.min(dc_voltage) 
print(dc_Vmax,dc_Vmin)

fig, ax = plt.subplots(figsize=(12,12))
extent = [freqx_min, freqx_max, dc_Vmin, dc_Vmax]
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy Vs Flux 2D', fontsize=20)
ax.imshow(data, aspect='auto', origin='lower', extent = extent, interpolation='nearest')
# print(type(data))
# print(data)

 
"""MongoDB存储数据"""
#result = [{'freq_x':freq_x.tolist()},{'voltage_y':dc_voltage.tolist()},{'qubit_spectroscopy_vs_flux':data.tolist()}]
#database_host = 'mongodb://localhost:27017/'
#database = mongodb(database_host)
#database.save_qubit_spectroscopy(result)

#%%   #——————Qubit Spectroscopy Vs Flux———时序2———注意要考虑腔的移动———————


"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=1.0)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc
hdawg.amplitude_drive = amplitude_drive

#设置drive pulse和dc pulse长度
hdawg.square_wave_sec_drive = square_wave_sec_drive
hdawg.square_wave_sec_dc = square_wave_sec_dc

#hdawg.wave_width_sec = drive_wave_width_sec
#hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.set_osc(osc_path=0, freq=osc_freq_drive)

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

#编译AWG sequence
hdawg.awg_builder_spec()
hdawg.awg_builder_flux_2() #awg_builder_flux_2不同于awg_builder_flux,在Probe的时间段也有直流偏置


"""新建实例uhfqa,初始化,将设置从Data Server同步到仪器"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置振荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_general()


"""变电压偏置，变微波源频率"""
data = []
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy', fontsize=20)
for index, voltage in enumerate(dc_voltage_list): 
    data_ch_1 = []
    data_ch_2 = []
    
    hdawg.set_total_amplitude(awgcore=1, amplitude=voltage)
    uhfqa.set_osc(osc_freq_probe_list[index]) #设置振荡器频率
    
    for freq in base_freq_drive:
        MW_GENERATOR_2.set_freq(freq)
        
        hdawg.daq.sync()
        hdawg.awg_open(awgcore=0)
        hdawg.awg_open(awgcore=1)
        uhfqa.daq.sync()
        uhfqa.awg_open()
        
        tmp = uhfqa.get_result(do_plot=0)
        data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
        data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
        print('------------')
        print(len(data_ch_1))
        print('------------')
    data_1= np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
    ax.plot(base_freq_drive*1e9+osc_freq_drive,data_1)
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
#plt.figure('qubit spectroscpy ')
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
data = np.array(data)
#plt.plot(freq_x, np.array(data))
#plt.title('image') # 图像题目
#data = np.array(data)
freqx_max = np.max(freq_x)
freqx_min = np.min(freq_x)
print(freqx_max,freqx_min)

dc_Vmax = np.max(dc_voltage_list) 
dc_Vmin = np.min(dc_voltage_list) 
print(dc_Vmax,dc_Vmin)

fig, ax = plt.subplots(figsize=(16,12))
extent = [freqx_min, freqx_max, dc_Vmin, dc_Vmax]
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy Vs Flux 2D', fontsize=20)
ax.imshow(data, aspect='auto', origin='lower', extent = extent, interpolation='nearest')
# print(type(data))
# print(data)

 
"""MongoDB存储数据"""
#result = [{'freq_x':freq_x.tolist()},{'voltage_y':dc_voltage.tolist()},{'qubit_spectroscopy_vs_flux':data.tolist()}]
#database_host = 'mongodb://localhost:27017/'
#database = mongodb(database_host)
#database.save_qubit_spectroscopy(result)


#%%   #——————Qubit Spectroscopy Vs Flux———时序3———注意要考虑腔的移动———————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
#hdawg.set_total_amplitude(awgcore=1, amplitude=1.0)
#设置单个pulse的amplitde
hdawg.amplitude_drive = amplitude_drive
#hdawg.amplitude_dc = amplitude_dc


#设置drive pulse和dc pulse长度
hdawg.square_wave_sec_drive = square_wave_sec_drive
#hdawg.square_wave_sec_dc = square_wave_sec_dc

#hdawg.wave_width_sec = drive_wave_width_sec
#hdawg.pulse_width_sec = drive_pulse_width_sec

hdawg.set_osc(osc_path=0, freq=osc_freq_drive)

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

#打开Direct，用于OFFSET输出
hdawg.direct_open(channel=2)

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译AWG sequence
hdawg.awg_builder_spec()
#hdawg.awg_builder_flux()


"""新建实例uhfqa,初始化,将设置从Data Server同步到仪器"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.set_demodulation_default() #初始化UHFQA

uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages

#设置awg core对应的所有通道的amplitude
uhfqa.set_total_amplitude(awgcore=0, amplitude=0.133)
#设置单个pulse的amplitde
uhfqa.amplitude_probe = amplitude_probe

uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1)
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0)
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe) #设置振荡器频率

#将UHFQA设置从Data Server同步到仪器
uhfqa.daq.sync()
time.sleep(0.6666)

#编译UHFQA sequence
uhfqa.awg_builder_general()


"""变电压偏置，变微波源频率"""
data = []
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy', fontsize=20)
for voltage in dc_voltage_list:
    data_ch_1 = []
    data_ch_2 = []
    
    #hdawg.set_total_amplitude(awgcore=1, amplitude=voltage)
    
    #设置HDAWG偏置通道的offset
    hdawg.set_offset(channel=2, offset=voltage)
    
    for freq in base_freq_drive:
        MW_GENERATOR_2.set_freq(freq)
        
        hdawg.daq.sync()
        hdawg.awg_open(awgcore=0)
        #hdawg.awg_open(awgcore=1)
        uhfqa.daq.sync()
        uhfqa.awg_open()
        
        tmp = uhfqa.get_result(do_plot=0)
        data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
        data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
        print('------------')
        print(len(data_ch_1))
        print('------------')
    data_1= np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
    ax.plot(base_freq_drive*1e9+osc_freq_drive,data_1)
    data.append(data_1)
    

"""UHFQA/HDAWG Channel Off/Sequence Stop"""
hdawg.awg_close(awgcore=0)
hdawg.awg_close(awgcore=1)
hdawg.channel_close(channel='*')
hdawg.direct_close(channel=2)

uhfqa.awg_close()
uhfqa.channel_close()


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off()  


"""画图初步"""    
#plt.figure('qubit spectroscpy ')
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
data = np.array(data)
#plt.plot(freq_x, np.array(data))
#plt.title('image') # 图像题目
#data = np.array(data)
freqx_max = np.max(freq_x)
freqx_min = np.min(freq_x)
print(freqx_max,freqx_min)

dc_Vmax = np.max(dc_voltage) 
dc_Vmin = np.min(dc_voltage) 
print(dc_Vmax,dc_Vmin)

fig, ax = plt.subplots(figsize=(12,12))
extent = [freqx_min, freqx_max, dc_Vmin, dc_Vmax]
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy Vs Flux 2D', fontsize=20)
ax.imshow(data, aspect='auto', origin='lower', extent = extent, interpolation='nearest')
# print(type(data))
# print(data)

 
"""MongoDB存储数据"""
#result = [{'freq_x':freq_x.tolist()},{'voltage_y':dc_voltage.tolist()},{'qubit_spectroscopy_vs_flux':data.tolist()}]
#database_host = 'mongodb://localhost:27017/'
#database = mongodb(database_host)
#database.save_qubit_spectroscopy(result)
