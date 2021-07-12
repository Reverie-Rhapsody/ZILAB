# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 20:49:57 2020

@author: rhapsody

------扫腔------固定直流偏置固定Power扫腔------变直流偏置固定Power扫腔------变Power固定直流偏置扫腔------


------时序1------固定直流偏置固定Local Power------
       ________________________________________
______|          DC Pulse  [Fixed]            |____________
                    ______________________
___________________| Probe Pulse [Fixed] |_________________



------时序2------变直流偏置固定Local Power------
       ________________________________________
______|          DC Pulse  [Change]           |____________
                    ______________________
___________________| Probe Pulse [Fixed] |_________________


------时序3------固定直流偏置变Local Power------
       ________________________________________
______|          DC Pulse  [Fixed]            |____________
                    ______________________
___________________| Probe Pulse [Change]|_________________

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


"""
rm = pyvisa.ResourceManager()
rm.list_resources()
my_instrument = rm.open_resource('TCPIP0::192.168.10.106::inst0::INSTR')
print(my_instrument)
"""

MW_GENERATOR_1 = PSG_E8257D(mw_generator_ip_1)
MW_GENERATOR_2 = PSG_E8257D(mw_generator_ip_2)
#DC_1 = DP800(dc_ip_1)

#%% #基本参数设置
print('---基本参数设置---')
"""基本参数设置"""

uhfqa_id = 'dev2534'
hdawg_id = 'dev8252'

base_freq_probe = 6.5

#base_power_probe = -7 #C7      #固定Local Power时使用
#base_power_probe = -5 #C4      #固定Local Power时使用
base_power_probe = -6 #C8     #固定Local Power时使用
base_power_probe_list = np.linspace(-6, 10, 17, endpoint=True)#C6     #变Local Power时使用

result_length = 1000
num_averages = 1
time_origin_sec = 500e-9

amplitude_probe = 0.133
amplitude_dc = 1.0

DC_Voltage = 0.1      #固定DC偏置扫腔时使用
DC_Voltage_list = np.linspace(-1.0, 1.0, 21, endpoint=True)       #变DC偏置扫腔时使用

#freq_scan = np.linspace(276e6, 281e6, 51, endpoint=True) #Q2
#freq_scan = np.linspace(212e6, 222e6, 101, endpoint=True) #Q4
#freq_scan = np.linspace(157.0e6, 167.0e6, 101, endpoint=True) #Q6
#freq_scan = np.linspace(162.0e6, 168e6, 501, endpoint=True) #C2 6.6658GHz
#freq_scan = np.linspace(502e6, 512.0e6, 501, endpoint=True) #C8 7.006GHz
#freq_scan = np.linspace(100e6, 500e6, 401, endpoint=True)#Total 6 cavities
#freq_scan = np.linspace(222.0e6, 225.0e6, 31, endpoint=True) #C3 6.7230GHz
#freq_scan = np.linspace(272.0e6, 278.0e6, 101, endpoint=True) #C4 6.7748GHz
#freq_scan = np.linspace(330.0e6, 340.0e6, 101, endpoint=True) #C5 6.8336GHz
#freq_scan = np.linspace(382.0e6, 392.0e6, 151, endpoint=True) #C6 6.8864GHz
#freq_scan = np.linspace(445.0e6, 455.0e6, 151, endpoint=True) #C7 6.9490GHz
#freq_scan = np.linspace(1.0e6, 551.0e6, 2201, endpoint=True) #Total 10 cavities
#freq_scan = np.linspace(559.0e6, 579.0e6, 801, endpoint=True) #C9
#freq_scan = np.linspace(107.0e6, 117.0e6, 501, endpoint=True) #C1
#freq_scan = np.linspace(620.0e6, 630.0e6, 501, endpoint=True) #C10
freq_scan = np.linspace(506.0e6, 512.0e6, 61, endpoint=True) #C8

print('Frequency Scan: GHz\n', [np.min(base_freq_probe+freq_scan/1e9),np.max(base_freq_probe+freq_scan/1e9)], 'Points: ', len(freq_scan), '\n')
print('Probe Power: dBm \n', base_power_probe, '\n')
print('Probe Power List: dBm \n', base_power_probe_list, '\n')
print('DC Voltage:  ', DC_Voltage, 'V \n')
print('DC Voltage List:  ', DC_Voltage_list, 'V \n')

#%%  #固定直流偏置固定Power扫腔  时序1
print('---开始固定直流偏置固定Power扫腔---')

"""设置微波源"""
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.turn_on()


"""设置直流源"""
#DC_1.set_value(ch=2, offset=0.0) #C1Q2
#DC_1.set_value(ch=1, offset=0.85) #C6Q4
#DC_1.set_value(ch=1, offset=0.0) #C4Q4
#DC_1.set_value(ch=1, offset=0.73) #C5
#DC_1.set_value(ch=1, offset=0.80) #C6
#DC_1.set_value(ch=1, offset=0.73) #C5
# DC_1.set_value(ch=1, offset=0.90) #C7
# DC_1.turn_off(ch=1)
# DC_1.get_state(ch=1)
# time.sleep(0.2)


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=DC_Voltage)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc

#设置drive通道和偏置通道的输出量程
hdawg.set_output_range(channel=0, range=0.4)
hdawg.set_output_range(channel=1, range=0.4)
hdawg.set_output_range(channel=2, range=1.0)
hdawg.set_output_range(channel=3, range=1.0)

#打开HDAWG要用的通道
hdawg.channel_close(channel='*')
#hdawg.channel_open(channel='0') 
#hdawg.channel_open(channel='1')
hdawg.channel_open(channel='2')
#hdawg.channel_open(channel='3')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译AWG sequence
#hdawg.awg_builder_flux_3()  #awg_builder_flux_3专用于扫腔时加方波偏置！
hdawg.awg_builder_flux_3()  #awg_builder_flux_3专用于扫腔时加方波偏置！
#Run HDAWG awg sequence
hdawg.awg_open(awgcore=1)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.num_averages = num_averages
uhfqa.time_origin_sec = time_origin_sec
uhfqa.set_total_amplitude(amplitude=amplitude_probe)
#uhfqa.set_relative_amplitude(amplitude_probe) #重置amplitude为1，防止变amplitde测量后停留在别的值


"""Probe start in spectroscopy mode"""
data = []
data_real = []
data_1,data_2 = uhfqa.spectroscopy_scan_frequency(2e-6,freq_scan)     
data.append(np.abs(np.array(data_1)+1j*np.array(data_2)))
data_real.append(data_1)


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()


"""UHFQA/HDAWG Channel Off/Sequence Stop"""
hdawg.awg_close(awgcore=1)
hdawg.channel_close(channel='*')

uhfqa.awg_close()
uhfqa.channel_close()


"""画图初步"""
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=16)
ax.set_xlabel('Frequency (GHz)', fontsize=16)
ax.set_title('Cavity Spectroscopy', fontsize=16)
freq_x = np.array(freq_scan)+base_freq_probe*1e9  
ax.plot(freq_x, np.array(data[0]))


"""MongoDB存储数据"""
result = [{'freq_x':freq_x.tolist()},{'spectroscopy_result_real':data_1},{'spectroscopy_result_imag':data_2}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_cavity_spectroscopy(result)
#print(data)

#%%  #变直流偏置固定Power扫腔
print('---开始变直流偏置固定Local Power扫腔---\n')

"""设置微波源"""
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=DC_Voltage)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc

#设置drive通道和偏置通道的输出量程
hdawg.set_output_range(channel=0, range=0.4)
hdawg.set_output_range(channel=1, range=0.4)
hdawg.set_output_range(channel=2, range=3.0)
hdawg.set_output_range(channel=3, range=1.0)

#打开HDAWG要用的通道
hdawg.channel_close(channel='*')
#hdawg.channel_open(channel='0') 
#hdawg.channel_open(channel='1')
hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译AWG sequence
hdawg.awg_builder_flux_3()  #awg_builder_flux_3专用于扫腔时加方波偏置！

#Run HDAWG awg sequence
hdawg.awg_open(awgcore=1)

"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.num_averages = num_averages
uhfqa.time_origin_sec = time_origin_sec
uhfqa.set_total_amplitude(amplitude=amplitude_probe) #设置awg core 1 的两个通道的输出amplitude
#uhfqa.set_relative_amplitude(amplitude_probe) #重置amplitude为1，防止变amplitde测量后停留在别的值

data_DC = [] #变DC采集的数据
data_DC_real = [] #变DC采集的数据的实部
for voltage in DC_Voltage_list:
    #设置DC偏置电压
    hdawg.set_total_amplitude(awgcore=1, amplitude=voltage)

    """Probe start in spectroscopy mode"""
    data_1,data_2 = uhfqa.spectroscopy_scan_frequency(2e-6,freq_scan)     
    data_DC.append(np.abs(np.array(data_1)+1j*np.array(data_2)))
    data_DC_real.append(data_1)

data_DC = np.array(data_DC).reshape(len(DC_Voltage_list), len(freq_scan))

"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()


"""UHFQA/HDAWG Channel Off/Sequence Stop"""
hdawg.awg_close(awgcore=1)
hdawg.channel_close(channel='*')

uhfqa.awg_close()
uhfqa.channel_close()


"""数据处理，返回所有电压偏置下腔频电压最低点"""
fixed_point = []
for data_list in data_DC:
    data_list = data_list.tolist()
    #fixed_point.append(freq_scan[data_list.index(np.min(data_list))]+base_freq_probe*1e9)
    fixed_point.append(freq_scan[data_list.index(np.min(data_list))])
print('Fixed Points:\n', fixed_point)


"""画图初步"""
fig, ax = plt.subplots()
ax.set_title('Cavity Spectroscopy Vs DC Voltage', fontsize=16)
ax.set_xlabel('Frequency (GHz)', fontsize=16)
ax.set_ylabel('DC Voltage /V', fontsize=16)
extent = [np.min(freq_scan/1e9+base_freq_probe), np.max(freq_scan/1e9+base_freq_probe), np.min(DC_Voltage_list), np.max(DC_Voltage_list)]
ax.imshow(data_DC, aspect='auto', origin='lower', extent = extent, interpolation='nearest')


"""MongoDB存储数据"""
# result = [{'freq_x':freq_x.tolist()},{'spectroscopy_result_real':data_1},{'spectroscopy_result_imag':data_2}]
# database_host = 'mongodb://localhost:27017/'
# database = mongodb(database_host)
# database.save_cavity_spectroscopy(result) 
# #print(data)

#%% #固定直流偏置变Local功率扫腔

print('---开始固定直流偏置变Local功率扫腔---')

"""变功率测量"""

#freq_scan = np.linspace(276e6, 281e6, 51, endpoint=True) #Q2
#freq_scan = np.linspace(103.0e6, 107.0e6, 101, endpoint=True) #Q8
#freq_scan = np.linspace(500e6, 510.0e6, 101, endpoint=True) #C8 7.0075GHz
#freq_scan = np.linspace(162.0e6, 168.0e6, 61, endpoint=True) #C2 6.6658GHz
#freq_scan = np.linspace(209.0e6, 229.0e6, 51, endpoint=True) #C2 6.7192GHz（又加10dB衰减）
#freq_scan = np.linspace(217.0e6, 227.0e6, 41, endpoint=True) #C3 6.7221GHz
#freq_scan = np.linspace(270.0e6, 278.0e6, 61, endpoint=True) #C4 6.7748GHz
#freq_scan = np.linspace(329.0e6, 337.0e6, 81, endpoint=True) #C5 6.8336GHz
#freq_scan = np.linspace(150.0e6, 280.0e6, 521, endpoint=True) #C1-C3 6.7766GHz
#freq_scan = np.linspace(1.0e6, 551.0e6, 2041, endpoint=True) #Total 10 cavities
#freq_scan = np.linspace(384.0e6, 392.0e6, 81, endpoint=True) #C6 6.8864GHz
#freq_scan = np.linspace(447.0e6, 453.0e6, 61, endpoint=True) #C7 6.9490GHz
#freq_scan = np.linspace(566.0e6, 574.0e6, 81, endpoint=True) #C9 7.0697GHz
#freq_scan = np.linspace(107.0e6, 117.0e6, 101, endpoint=True) #C1

#amplitude_scan = np.logspace(-10, 0, 40, base=2)
#amplitude_scan = np.linspace(-15, 10, 10, endpoint=True)#C2
#amplitude_scan = np.linspace(-12, 6, 13, endpoint=True)#C3
#amplitude_scan = np.linspace(-8, 8, 10, endpoint=True)#C4
#amplitude_scan = np.linspace(-20, -10, 3, endpoint=True)#C5
#amplitude_scan = np.linspace(-10, 10,3, endpoint=True)#C1-C3
#amplitude_scan = np.linspace(-10, 10,10, endpoint=True)#Total 10 cavities
#amplitude_scan = np.linspace(-10, 10, 10, endpoint=True)#C6
#amplitude_scan = np.linspace(-8, 8, 3, endpoint=True)#C7
#amplitude_scan = np.linspace(-20, 18, 10, endpoint=True)#C8
#amplitude_scan = np.linspace(-5, 14,11, endpoint=True)#C9
#amplitude_scan = np.linspace(-20, 5,10, endpoint=True)#C1

#print('Frequency Scan: GHz\n', [np.min(base_freq_probe+freq_scan/1e9),np.max(base_freq_probe+freq_scan/1e9)], 'Points: ', len(freq_scan))
#print('Amplitude Scan: dBm\n', [np.min(amplitude_scan), np.max(amplitude_scan)], ' Points: ', len(amplitude_scan))

"""设置微波源"""
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.set_power(-10)
MW_GENERATOR_1.turn_on()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.time_origin_sec = time_origin_sec

#设置awg core对应的所有通道的amplitude
hdawg.set_total_amplitude(awgcore=0, amplitude=1.0)
hdawg.set_total_amplitude(awgcore=1, amplitude=DC_Voltage)
#设置单个pulse的amplitde
hdawg.amplitude_dc = amplitude_dc

#设置drive通道和偏置通道的输出量程
hdawg.set_output_range(channel=0, range=0.4)
hdawg.set_output_range(channel=1, range=0.4)
hdawg.set_output_range(channel=2, range=1.0)
hdawg.set_output_range(channel=3, range=1.0)

#打开HDAWG要用的通道
hdawg.channel_close(channel='*')
#hdawg.channel_open(channel='0') 
#hdawg.channel_open(channel='1')
hdawg.channel_open(channel='2')

#关闭偏置通道的调制
hdawg.modulation_close(awgcore=1)

#将AWG设置从Data Server同步到仪器
hdawg.daq.sync()
time.sleep(0.6666)

#编译AWG sequence
hdawg.awg_builder_flux_3()  #awg_builder_flux_3专用于扫腔时加方波偏置！

#Run HDAWG awg sequence
hdawg.awg_open(awgcore=1)

"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.num_averages = num_averages
uhfqa.time_origin_sec = time_origin_sec
uhfqa.set_total_amplitude(amplitude=amplitude_probe) #设置awg core 1 的两个通道的输出amplitude
#uhfqa.set_relative_amplitude(amplitude_probe) #重置amplitude为1，防止变amplitde测量后停留在别的值


"""变微波源(Local)功率"""
data_power = []
for amp in base_power_probe_list:
    MW_GENERATOR_1.set_power(amp)
    data_3,data_4 = uhfqa.spectroscopy_scan_frequency(2e-6,freq_scan)
    data_power.append(np.abs(np.array(data_3)+1j*np.array(data_4)))


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()


"""画图初步"""
# freq_x = np.array(freq_scan)+base_freq_probe*1e9
# data_power = np.array(data_power)
# plt.figure('spectroscopy vs power')
# plt.contourf(freq_x, base_power_probe_list, np.array(data_power))
# plt.imshow(data_power, aspect='auto', origin='lower', interpolation='nearest')
# plt.title('Cavity Spectroscopy Vs Local Power')
# for i in range(len(base_power_probe_list)):
#     dbm_max = np.max(data_power[i])
#     dbm_min = np.min(data_power[i])
#     dbm_delta = dbm_max-dbm_min
#     data_power[i] = (data_power[i]-dbm_min)/dbm_delta
# plt.figure('spectroscopy vs power')
# plt.imshow(data_power, aspect='auto', origin='lower', interpolation='nearest')



fig, ax = plt.subplots()
ax.set_title('Cavity Spectroscopy Vs Local Power', fontsize=16)
ax.set_xlabel('Frequency (GHz)', fontsize=16)
ax.set_ylabel('Local Power /dBm', fontsize=16)
extent = [np.min(freq_scan/1e9+base_freq_probe), np.max(freq_scan/1e9+base_freq_probe), np.min(base_power_probe_list), np.max(base_power_probe_list)]
ax.imshow(data_power, aspect='auto', origin='lower', extent = extent, interpolation='nearest')




"""MongoDB存储数据"""
data_power = np.array(data_power)
freq_x = np.array(freq_scan)+base_freq_probe*1e9 
result = [{'freq_x':freq_x.tolist()},{'amplitude_y':base_power_probe_list.tolist()},{'data_power':data_power.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_cavity_spectroscopy_vs_power(result)


#%%  #变Probe Pulse awgcore 对应系数 等效变Probe 功率 未修改，暂时不用
"""基本参数设置"""
data_power = []
freq_scan = np.linspace(125.0e6, 150.0e6, 31, endpoint=True)
#amplitude_scan = np.logspace(-10, 0, 40, base=2)
amplitude_scan = np.logspace(-5, 0, 2, base=2)


"""设置微波源"""
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.set_power(20)
MW_GENERATOR_1.turn_on()


"""变amplitude probe,等效于变功率"""
for amp in amplitude_scan:
    uhfqa.set_relative_amplitude(amp)
    data_3,data_4 = uhfqa.spectroscopy_scan_frequency(2e-6,freq_scan)
    data_power.append(np.abs(np.array(data_3)+1j*np.array(data_4)))


"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()


"""画图初步"""
freq_x = np.array(freq_scan)+base_freq_probe*1e9
data_power = np.array(data_power)
plt.figure('spectroscopy vs power')
plt.contourf(freq_x, amplitude_scan, np.array(data_power))
plt.imshow(data_power, aspect='auto', origin='lower', interpolation='nearest')
plt.title('image')
for i in range(len(amplitude_scan)):
    dbm_max = np.max(data_power[i])
    dbm_min = np.min(data_power[i])
    dbm_delta = dbm_max-dbm_min
    data_power[i] = (data_power[i]-dbm_min)/dbm_delta
plt.figure('spectroscopy vs power')
plt.imshow(data_power, aspect='auto', origin='lower', interpolation='nearest')


"""MongoDB存储数据"""
result = [{'freq_x':freq_x.tolist()},{'amplitude_y':amplitude_scan.tolist()},{'data_power':data_power.tolist()}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_cavity_spectroscopy_vs_power(result)



