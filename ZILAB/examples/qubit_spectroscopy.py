# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:29:39 2020

@author: Rhapsody

------测能谱------

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


"""
from ZILAB.driver.UHFQA import zurich_qa
from ZILAB.driver.HDAWG import zurich_awg
from ZILAB.driver.PSG_E8257D import PSG_E8257D,PSG_E8257D_2
from ZILAB.driver.DP800 import DP800
from ZILAB.db.MongoDB import mongodb

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

#%%  #基本参数设置

"""基本参数设置"""
#仪器ID
uhfqa_id = 'dev2534'
hdawg_id = 'dev8252'

base_freq_probe = 6.5

#osc_freq_probe = 165.9e6 #C2 
#osc_freq_probe = 222.1e6 #C3 
osc_freq_probe = 450.26e6 #C7
#osc_freq_probe = 113.3e6 #C1
#osc_freq_probe = 275.39e6 #C4 不加偏置
#osc_freq_probe = 275.73e6 #C4 flux:0.25V
#osc_freq_probe = 387.20e6 #C6 flux:0.80V
#osc_freq_probe = 334.80e6 #C5 flux:0.73V
#osc_freq_probe = 570.8e6 #C9

#base_freq_drive = np.linspace(4.65, 4.72, 211, endpoint = True) #C2
#base_freq_drive = np.linspace(5.5, 6.5, 1001, endpoint = True) #C2
#base_freq_drive = np.linspace(4.9, 5.5, 601, endpoint = True) #C2
#base_freq_drive = np.linspace(4.2, 4.9, 701, endpoint = True) #C2
#base_freq_drive = np.linspace(4.9, 5.5, 601, endpoint = True) #C3
#base_freq_drive = np.linspace(6.3, 6.5, 201, endpoint = True) #C3
#base_freq_drive = np.linspace(4.2, 4.9, 701, endpoint = True) #C3
#base_freq_drive = np.linspace(4.5, 4.6, 401, endpoint = True) #C7
#base_freq_drive = np.linspace(4.7, 5.2,1001, endpoint = True) #C7
#base_freq_drive = np.linspace(6.4, 7.0,301, endpoint = True) #C7
#base_freq_drive = np.linspace(5.7, 6.4,351, endpoint = True) #C7
#base_freq_drive = np.linspace(4.6, 5.1,501, endpoint = True) #C7
#base_freq_drive = np.linspace(4.72, 4.78,601, endpoint = True) #C6
#base_freq_drive = np.linspace(4.8, 4.85, 51, endpoint = True) #C5
#base_freq_drive = np.linspace(4.7, 4.8,101, endpoint = True) #C9
#base_freq_drive = np.linspace(4.6, 4.8,401, endpoint = True) #C9
#base_freq_drive = np.linspace(4.85, 5.15, 301, endpoint = True) #C6 part1
base_freq_drive = np.linspace(4.70, 4.90, 201, endpoint = True) #C6 part2
osc_freq_drive = 50e6
#osc_freq_drive = 50e6
#base_power_probe = -5 #C2 
#base_power_probe = -5 # C3
#base_power_probe = -5# C7
#base_power_probe = -3# C9
#base_power_probe = -12 # C1
base_power_probe = -7
# C4
#base_power_probe = -6# C6 
#base_power_probe = -12# C5

base_power_drive = -5#C4

time_origin_sec = 42e-6
#time_origin_sec = 500e-9
period_wait_sec = 100e-6
drive_wave_width_sec = 300.0e-9 #step length of gauss pulse  单位：s
#drive_pulse_width_sec = 150.0e-9 #step standard deviation of gauss pulse  单位：s
drive_pulse_width_sec = 50.0e-9
square_wave_sec = 40e-6
result_length = 2000  #UHFQA和HDAWG 此处相同
num_averages = 1  #UHFQA和HDAWG此处相同,不用硬件平均
amplitude_probe_1 = 0.133 #uhfqa的awg输出波形的振幅系数，值为`1.0`则表示`1.0*range`应设为变功率测量得到合适的dispersive范围amplitude
amplitude_probe_2 = 1.0 #probe 波形前乘以的系数，与amplitude_probe_1同样起到调节probe power的作用，实际probe power应为amplitude_probe_1*amplitude_probe_2*base_power 
amplitude_drive_1 = 1.0
amplitude_drive_2 = 0.5
data_ch_1 = [] #存储实部
data_ch_2 = [] #存储虚部
samp_rate = 1.8e9 # 采样率1.8GHz  
t_sec = 2e-6  #对probe结果采取的积分长度，单位：s
read_length = np.floor(t_sec*samp_rate/8)*8  #积分长度，按点数计，取整数

#%%   #————————————时序1————————————

"""设置微波源"""
MW_GENERATOR_1.set_power(base_power_probe)
MW_GENERATOR_1.set_freq(base_freq_probe)
MW_GENERATOR_1.turn_on()

MW_GENERATOR_2.set_power(base_power_drive)
MW_GENERATOR_2.set_freq(base_freq_drive[0])
MW_GENERATOR_2.turn_on()


#"""设置直流源"""
# DC_1.set_value(ch=1, offset=0.90)
# DC_1.turn_on(ch=1)
# DC_1.get_state(ch=1)
# time.sleep(0.2)


"""初始化实例uhfqa,传递参数"""
uhfqa = zurich_qa(uhfqa_id)
uhfqa.result_length = result_length
uhfqa.time_origin_sec = time_origin_sec
uhfqa.period_wait_sec = period_wait_sec
uhfqa.num_averages = num_averages
uhfqa.amplitude_probe_1 = amplitude_probe_1
uhfqa.set_relative_amplitude()
uhfqa.amplitude_probe_2 = amplitude_probe_2
uhfqa.daq.sync()


"""初始化实例hdawg,传递参数,sequence编译执行,等待触发"""
hdawg = zurich_awg(hdawg_id)
hdawg.result_length = result_length
hdawg.num_averages = num_averages
hdawg.time_origin_sec = time_origin_sec
hdawg.amplitude_drive_1 = amplitude_drive_1
hdawg.set_relative_amplitude()
hdawg.amplitude_drive_2 = amplitude_drive_2
hdawg.square_wave_sec = square_wave_sec
hdawg.wave_width_sec = drive_wave_width_sec
hdawg.pulse_width_sec = drive_pulse_width_sec
hdawg.set_osc(osc_freq_drive)
hdawg.awg_builder_spec()
hdawg.daq.sync()
time.sleep(0.6666)
hdawg.awg_open()


"""UHFQA初始化,Sequence编译"""
uhfqa.set_demodulation_default() #初始化UHFQA
uhfqa.spectroscopy(mode_on = 1) #选择Spectroscopy模式
uhfqa.update_qubit_frequency([0, 0])
uhfqa.set_rotation(0, rotation = 1-1j, input_mapping= 1 )
uhfqa.set_rotation(1, rotation = 1+1j, input_mapping= 0 )
uhfqa.set_result_path(source = 2)# 7=读取integration, 2 = rotation后的数值
uhfqa.set_pulse_length(read_length) #设置积分长度
uhfqa.set_osc(osc_freq_probe)
uhfqa.daq.sync()
time.sleep(0.6666)
uhfqa.awg_builder_general()


"""变微波源频率,扫频"""

for freq in base_freq_drive:
    MW_GENERATOR_2.set_freq(freq)
    uhfqa.daq.sync()
    uhfqa.awg_open()
    tmp = uhfqa.get_result(do_plot=0)
    data_ch_1.append(np.mean(tmp[uhfqa.paths[0]])) #实部
    data_ch_2.append(np.mean(tmp[uhfqa.paths[1]])) #虚部 
    print('------------')
    print(len(data_ch_1))
    print('------------')
data = np.abs(np.array(data_ch_1)+1j*np.array(data_ch_2))
    

"""关闭微波源输出"""
MW_GENERATOR_1.turn_off()
MW_GENERATOR_2.turn_off()  


"""关闭直流源"""
# time.sleep(0.2)
# DC_1.turn_off(ch=1)


"""画图初步"""    
fig, ax = plt.subplots()
ax.set_ylabel('DC Voltage /V', fontsize=20)
ax.set_xlabel('Frequency (GHz)', fontsize=20)
ax.set_title('Qubit spectroscopy', fontsize=20)
freq_x = np.array(base_freq_drive)*1e9+osc_freq_drive
ax.plot(freq_x, np.array(data))

 
"""MongoDB存储数据"""
result = [{'freq_x':freq_x.tolist()},{'spectroscopy_real':data_ch_1},{'spectroscopy_imag':data_ch_2}]
database_host = 'mongodb://localhost:27017/'
database = mongodb(database_host)
database.save_qubit_spectroscopy(result)
    
