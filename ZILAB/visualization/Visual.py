# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:24:08 2020

@author: Rhapsody
"""

import numpy as np
import re
import matplotlib.pyplot as plt

class visual(object):
    def __init__(self):
        pass
    def plot_cavity_spectroscopy(self, data):
        """
        cavity_spectroscopy_result = data
        for key,value in cavity_spectroscopy_result.items():
            if not re.match('cavity spectroscopy result list', key, re.I)==None:
                cavity_spectroscopy_result_list = value
                #print(rabi_result_list)
        
        x_amplitudes = cavity_spectroscopy_result_list[0]['freq_x']
        spectroscopy_result_real = cavity_spectroscopy_result_list[1]['spectroscopy_result_real']
        spectroscopy_result_imag = cavity_spectroscopy_result_list[2]['spectroscopy_result_imag']
        spectroscopy_result_complex = np.array(spectroscopy_result_real)+1j*np.array(spectroscopy_result_imag)
        #print(rabi_complex)
        """
        x_freq, spectroscopy_result_complex = data
        fig, ax = plt.subplots()
        #plt.figure()
        #plt.plot(x_amplitudes,np.abs(spectroscopy_result_complex))
        ax.plot(x_freq, np.abs(spectroscopy_result_complex))
        ax.legend(loc='best')
        ax.set_xlabel('Frequency/Hz', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('Cavity_Spectroscopy', fontsize=20)
        #plt.show()
        
    def plot_cavity_spectroscopy_dbm(self, data):
        """
        cavity_spectroscopy_result = data
        for key,value in cavity_spectroscopy_result.items():
            if not re.match('cavity spectroscopy result list', key, re.I)==None:
                cavity_spectroscopy_result_list = value
                
                
        x_amplitudes = cavity_spectroscopy_result_list[0]['freq_x']
        spectroscopy_result_real = cavity_spectroscopy_result_list[1]['spectroscopy_result_real']
        spectroscopy_result_imag = cavity_spectroscopy_result_list[2]['spectroscopy_result_imag']
        spectroscopy_result_complex = np.array(spectroscopy_result_real)+1j*np.array(spectroscopy_result_imag)
        spectroscopy_result_complex_dbm = 10+20*np.log10(np.abs(spectroscopy_result_complex))
        #print(rabi_complex)
        """
        x_freq, spectroscopy_result_complex = data
        spectroscopy_result_complex_dbm = 10+20*np.log10(np.abs(spectroscopy_result_complex))
        fig, ax = plt.subplots()
        ax.plot(x_freq, spectroscopy_result_complex_dbm)
        ax.legend(loc='best')
        ax.set_xlabel('Frequency/Hz', fontsize=20)
        ax.set_ylabel('Gain/dBm', fontsize=20)
        ax.set_title('Cavity_Spectroscopy', fontsize=20)
        
        
    def plot_cavity_spectroscopy_vs_power(self, data):
        """
        cavity_spectroscopy_vs_power_result = data
        for key,value in cavity_spectroscopy_vs_power_result.items():
            if not re.match('cavity spectroscopy result list vs power', key, re.I)==None:
                cavity_spectroscopy_vs_power_result_list = value
                #print(rabi_result_list)
        
        x_freq = np.array(cavity_spectroscopy_vs_power_result_list[0]['x_freq'])
        y_power = cavity_spectroscopy_vs_power_result_list[1]['power_list']
        spectroscopy_result_real = np.array(cavity_spectroscopy_vs_power_result_list[2]['spectroscopy_result_real'])
        spectroscopy_result_imag = np.array(cavity_spectroscopy_vs_power_result_list[3]['spectroscopy_result_imag'])
        spectroscopy_result_complex = sp.l  ectroscopy_result_real+1j*spectroscopy_result_imag
        """
        
        x_freq, y_power, spectroscopy_result_complex = data
        fig, ax = plt.subplots()
        ax.set_ylabel('Power (dbm)')
        ax.set_xlabel('Frequency (Hz)')
        xmin = min(6.68e9+x_freq)
        xmax = max(6.68e9+x_freq)
        ymin = min(y_power)
        ymax = max(y_power)
        extent = [xmin,xmax,ymin,ymax]
        print(xmin)
        print(xmax)
        print(ymin)
        print(ymax)
        #label_x = 6.68e9+experiment['oscillator_freq_list']
        #label_y=experiment['power_list'] # 填写自己的标签
        #ax.set_xticklabels(label_x)
        #ax.set_yticklabels(label_y)
        #ax.set_xlim(label_x)
        #ax.set_ylim(label_y)
        ax.imshow(np.abs(spectroscopy_result_complex), aspect='auto', extent = extent, origin='lower', interpolation='nearest')

    def plot_cavity_spectroscopy_vs_flux(self, data):
        """Cavity Freq modulation by dc voltage"""
        x_freq, y_voltage, spectroscopy_result_complex = data
        fig, ax = plt.subplots()
        ax.set_ylabel('DC Voltage (V)', fontsize=20)
        ax.set_xlabel('Frequency (GHz)', fontsize=20)
        ax.set_title('Cavity Frequency vs Flux', fontsize=20)
        xmin = min(x_freq)
        xmax = max(x_freq)
        ymin = min(y_voltage)
        ymax = max(y_voltage)
        extent = [xmin,xmax,ymin,ymax]
        # print(xmin)
        # print(xmax)
        # print(ymin)
        # print(ymax)
        #label_x = 6.68e9+experiment['oscillator_freq_list']
        #label_y=experiment['power_list'] # 填写自己的标签
        #ax.set_xticklabels(label_x)
        #ax.set_yticklabels(label_y)
        #ax.set_xlim(label_x)
        #ax.set_ylim(label_y)
        ax.imshow(np.abs(spectroscopy_result_complex), aspect='auto', extent = extent, origin='lower', interpolation='nearest')


    def plot_cavity_spectroscopy_vs_power_regularization(self, data):
        """
        cavity_spectroscopy_vs_power_result = data
        for key,value in cavity_spectroscopy_vs_power_result.items():
            if not re.match('cavity spectroscopy result list vs power', key, re.I)==None:
                cavity_spectroscopy_vs_power_result_list = value
        
        freq_x = cavity_spectroscopy_vs_power_result_list[0]['freq_x']
        amplitude_y = cavity_spectroscopy_vs_power_result_list[1]['amplitude_y']
        data_power = np.array(cavity_spectroscopy_vs_power_result_list[2]['data_power'])
        """
        
        freq_x, amplitude_y, data_power = data
        data_power_dbm = 10+20*np.log10(np.abs(data_power))
        for i in range(len(amplitude_y)):
            dbm_max = np.max(data_power[i])
            dbm_min = np.min(data_power[i])
            dbm_delta = dbm_max-dbm_min
            data_power[i] = (data_power[i]-dbm_min)/dbm_delta
        fig, ax = plt.subplots()
        #fig, ax = plt.subplots(figsize=(12,12)) #加了figsize后jupyter notebook调用画图比例不对
        ax.set_ylabel('Power (dbm)')
        ax.set_xlabel('Frequency (Hz)')
        xmin = min(freq_x)
        xmax = max(freq_x)
        ymin = min(amplitude_y)
        ymax = max(amplitude_y)
        extent = [xmin,xmax,ymin,ymax]
        ax.legend(loc='best')
        ax.imshow(data_power, aspect='auto', extent = extent, origin='lower', interpolation='nearest')
        
    def plot_qubit_spectroscopy(self, data):
        """
        qubit_spectroscopy_result = data
        for key,value in qubit_spectroscopy_result.items():
            if not re.match('qubit spectroscopy result list ', key, re.I)==None:
                qubit_spectroscopy_result_list = value
        
        freq_x = qubit_spectroscopy_result_list[0]['freq_x']
        spectroscopy_real = qubit_spectroscopy_result_list[1]['spectroscopy_real']
        spectroscopy_imag = qubit_spectroscopy_result_list[2]['spectroscopy_imag']
        data = np.abs(np.array(spectroscopy_real)+1j*np.array(spectroscopy_imag))
        """
        
        freq_x, spectroscopy_complex = data
        fig, ax = plt.subplots()
        ax.plot(freq_x, spectroscopy_complex)
        ax.legend(loc='best')
        ax.set_xlabel('Frequency/Hz', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('Qubit_Spectroscopy', fontsize=20)
        
    def plot_rabi(self, data):
        """
        rabi_result = data
        for key,value in rabi_result.items():
            if not re.match('rabi result list ', key, re.I)==None:
                rabi_result_list = value
                
        step_x = np.array(rabi_result_list[0]['time_x'])
        rabi_real = rabi_result_list[1]['rabi_real']
        rabi_imag = rabi_result_list[2]['rabi_imag']
        rabi_complex = np.abs(np.array(rabi_real)+1j*np.array(rabi_imag))
        """
        
        step_x, rabi_complex = data
        fig, ax = plt.subplots()
        ax.plot(step_x, rabi_complex)
        ax.legend(loc='best')
        ax.set_xlabel('Time/us', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('Rabi', fontsize=20)
        
    def plot_T1(self, data):
        """
        T1_result = data
        for key, value in T1_result.items():
            if not re.match('T1 result list ', key, re.I)==None:
                T1_result_list = value
        
        time_increment = T1_result_list[3]['time_increment']
        rate = time_increment*8*(1e6)/(1.8e9) 
        time_x = np.array(T1_result_list[0]['time_x'])*rate #单位是微秒
        T1_real = T1_result_list[1]['T1_real']
        T1_imag = T1_result_list[2]['T1_imag']
        T1_complex = np.abs(np.array(T1_real)+1j*np.array(T1_imag))
        """
        
        time_x, T1_complex = data
        fig, ax = plt.subplots()
        ax.plot(time_x, T1_complex)
        ax.legend(loc='best')
        ax.set_xlabel('Time/us', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('T1', fontsize=20)
        
    def plot_T2(self, data):
        """
        T2_result = data
        for key, value in T2_result.items():
            if not re.match('T2 result list ', key, re.I)==None:
                T2_result_list = value
                
        time_increment = T2_result_list[3]['time_increment']
        rate = time_increment*8*(1e6)/(1.8e9) 
        time_x = np.array(T2_result_list[0]['time_x'])*rate #单位是微秒
        T2_real = T2_result_list[1]['T2_real']
        T2_imag = T2_result_list[2]['T2_imag']
        detuning = T2_result_list[4]['detuning'] #失谐
        T2_complex = np.abs(np.array(T2_real)+1j*np.array(T2_imag))
        """
        
        time_x, T2_complex = data
        fig, ax = plt.subplots()
        ax.plot(time_x, T2_complex)
        ax.legend(loc='best')
        ax.set_xlabel('Time/us', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('Ramsey', fontsize=20)
        
    def plot_spinecho(self, data):
        """
        T2_result = data
        for key, value in T2_result.items():
            if not re.match('T2 result list ', key, re.I)==None:
                T2_result_list = value
                
        time_increment = T2_result_list[3]['time_increment']
        rate = time_increment*8*(1e6)/(1.8e9) 
        time_x = np.array(T2_result_list[0]['time_x'])*rate #单位是微秒
        T2_real = T2_result_list[1]['T2_real']
        T2_imag = T2_result_list[2]['T2_imag']
        detuning = T2_result_list[4]['detuning'] #失谐
        T2_complex = np.abs(np.array(T2_real)+1j*np.array(T2_imag))
        """
    
        time_x, spinecho_complex = data
        fig, ax = plt.subplots()
        ax.plot(time_x, spinecho_complex)
        ax.legend(loc='best')
        ax.set_xlabel('Time/us', fontsize=20)
        ax.set_ylabel('Vpp/V', fontsize=20)
        ax.set_title('Spin Echo', fontsize=20)
        
    def plot_picali(self, data):
        """
        Pi Pulse Calibration
        """
        pulse_list, power_list, data_2D = data
        fig, ax = plt.subplots()
        xmin = min(pulse_list)
        xmax = max(pulse_list)
        ymin = min(power_list)
        ymax = max(power_list)
        extent = [xmin,xmax,ymin,ymax]
        ax.legend(loc='best')
        ax.imshow(data_2D, aspect='auto', extent = extent, origin='lower', interpolation='nearest')
        ax.set_ylabel('Power', fontsize=20)
        ax.set_xlabel('Pulse Length / us', fontsize=20)
        ax.set_title('Pi Pulse Calibration', fontsize=20)
        
    def plot_singleshot(self, data):
        """
        Single Shot Plot
        """
        data_ch_1, data_ch_2, data_ch_11, data_ch_22 = data        
        data_ch_1_center = np.mean(data_ch_1)
        data_ch_2_center = np.mean(data_ch_2)
        data_ch_11_center = np.mean(data_ch_11)
        data_ch_22_center = np.mean(data_ch_22)
        cx = np.mean([data_ch_1_center, data_ch_11_center])
        cy = np.mean([data_ch_2_center, data_ch_22_center])
        x_first = np.min([np.min(data_ch_1),np.min(data_ch_11)])
        x_last = np.max([np.max(data_ch_1),np.max(data_ch_11)])
        slope = -1/((data_ch_22_center-data_ch_2_center)/(data_ch_11_center-data_ch_1_center))
        x = np.linspace(x_first, x_last, 66)
        
        fig, ax = plt.subplots()
        ax.scatter(np.array(data_ch_1), np.array(data_ch_2), s=5)
        ax.scatter(np.array(data_ch_11), np.array(data_ch_22), s=5)
        ax.scatter(data_ch_1_center, data_ch_2_center, c='r')
        ax.scatter(data_ch_11_center, data_ch_22_center, c='r')
        ax.plot([data_ch_1_center, data_ch_11_center], [data_ch_2_center, data_ch_22_center], c='b')
        ax.plot(x, slope*(x-cx)+cy, c='k')
        ax.set_xlabel('Real', fontsize=20)
        ax.set_ylabel('Imag', fontsize=20)
        ax.set_title('Single Shot', fontsize=20)
        plt.axis('equal') #使横轴和纵轴步长一致
        
    def plot_rbm(self, data):
        "Randomized Benchmarking Plot"
        m_x, num_per_m, data_ch_1, data_ch_2, data, data_mean = data
        num_m = len(m_x)
        print(m_x)
        num_per_m = int(num_per_m)
        data_ch_1 = np.array(data_ch_1)
        data_ch_2 = np.array(data_ch_2)
        data = np.array(data)
        #data_ch_1 = data_ch_1.reshape((num_m, num_per_m))
        #data_ch_2 = data_ch_2.reshape((num_m, num_per_m))
        #data = data.reshape((num_m, num_per_m))
        
        fig, ax = plt.subplots()
        for i in range(num_m):
            x_list =[m_x[i]]*num_per_m
            ax.scatter(x_list, data[i], s=10)
        ax.scatter(m_x, data_mean, s=33, c='k')
        ax.plot(m_x, data_mean)
        ax.set_xlabel('Number of clifford gates', fontsize=20)
        ax.set_ylabel('Voltage/V', fontsize=20)
        ax.set_title('Clifford based Randomized Benchmarking', fontsize=20)
        
    def plot_rbm_puri(self, data):
        "Purity Benchmarking Plot"
        m_x, num_per_m, data_ch_1, data_ch_2, data, data_mean = data
        num_m = len(m_x)
        print(m_x)
        num_per_m = int(num_per_m)
        data_ch_1 = np.array(data_ch_1)
        data_ch_2 = np.array(data_ch_2)
        data = np.array(data)
        #data_ch_1 = data_ch_1.reshape((num_m, num_per_m))
        #data_ch_2 = data_ch_2.reshape((num_m, num_per_m))
        #data = data.reshape((num_m, num_per_m))
        
        fig, ax = plt.subplots()
        for i in range(num_m):
            x_list =[m_x[i]]*num_per_m
            ax.scatter(x_list, data[i], s=10)
        ax.scatter(m_x, data_mean, s=33, c='k')
        ax.plot(m_x, data_mean)
        ax.set_xlabel('Number of clifford gates', fontsize=20)
        ax.set_ylabel('Purity', fontsize=20)
        ax.set_title('Purity Benchmarking', fontsize=20)
    
    def plot_rbm_2(self, data, voltage_0 = 11, voltage_1 = 35):
        "Randomized Benchmarking Plot"
        m_x, num_per_m, data_ch_1, data_ch_2, data, data_mean = data
        num_m = len(m_x)
        num_per_m = int(num_per_m)
        data_ch_1 = np.array(data_ch_1)
        data_ch_2 = np.array(data_ch_2)
        data = np.array(data)
        data_ch_1 = data_ch_1.reshape((num_m, num_per_m))
        data_ch_2 = data_ch_2.reshape((num_m, num_per_m))
        data = data.reshape((num_m, num_per_m))
        
        voltage_0 = voltage_0
        voltage_1 = voltage_1
        for i in range(num_m):
            for j in range(num_per_m):
                data[i][j] = (voltage_1-data[i][j])/(voltage_1-voltage_0)
        data_mean = np.mean(data,1)
        fig, ax = plt.subplots()
        for k in range(num_m):
            x_list = [m_x[k]]*num_per_m
            ax.scatter(x_list, data[k])
        ax.scatter(m_x, data_mean, s=100, c='k')
        ax.plot(m_x, data_mean,c='k')
        ax.set_xlabel('Number of clifford gates', fontsize=20)
        ax.set_ylabel('Population', fontsize=20)
        ax.set_title('Clifford based Randomized Benchmarking', fontsize=20)
        
               
    def plot_cavityvsflux(self, data):
        """Cavity frequency vs dc voltage"""
        freq_x, dc_voltage, data = data
        fig, ax = plt.subplots()
        xmin = min(freq_x)
        xmax = max(freq_x)
        ymin = min(dc_voltage)
        ymax = max(dc_voltage)
        extent = [xmin,xmax,ymin,ymax]
        ax.legend(loc='best')
        ax.imshow(data, aspect='auto', extent = extent, origin='lower', interpolation='nearest')
        ax.set_ylabel('Voltage / V', fontsize=20)
        ax.set_xlabel('Cavity Freq / GHz', fontsize=20)
        ax.set_title('Cavity Freq vs Flux', fontsize=20) # 图像题目
        
    def plot_drag_cali(self, data1, data2, data3):
        """drag amplitude calibration"""
        drag_amplitude_list_1, data_complex_1 = data1
        drag_amplitude_list_2, data_complex_2 = data2
        drag_amplitude_list_3, data_complex_3 = data3
        fig, ax = plt.subplots()
        ax.plot(drag_amplitude_list_1, data_complex_1, label = 'Rx(Pi/2)')
        ax.plot(drag_amplitude_list_1, data_complex_2, label = 'Rx(Pi),Ry(Pi/2)') 
        ax.plot(drag_amplitude_list_1, data_complex_3, label = 'Rx(Pi),Ry(-Pi/2)')
        ax.legend()
        ax.set_ylabel('Voltage / V', fontsize=20)
        ax.set_xlabel('Drag Amplitude', fontsize=20)
        ax.set_title('Drag Amplitude Calibration', fontsize=20) # 图像题目
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        