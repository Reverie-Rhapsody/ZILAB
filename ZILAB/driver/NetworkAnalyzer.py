# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 11:49:29 2021

@author: Rhapsody
"""

import numpy as np
import pyvisa
import time                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         

class NA(object):
    """ROHDE&SCHWARZ NETWORK ANALYZER"""
    def __init__(self, device_ip):
        """连接仪器，初始化"""
        self.device_ip = 'TCPIP0::192.168.10.227::inst0::INSTR'
        self.device_ip = device_ip
        try:
            rm = pyvisa.ResourceManager()
            self.NA = rm.open_resource(str(self.device_ip))
        except:
            print("没有连接，检查微波源ip是否正确")
        
    def get_S(self, ch=1, formated=False):
        """Get the complex value of S parameter or formated data"""
        #turn off sweep
        self.NA.write('INIT:CONT OFF')
        #begin a measurement
        
        
        self.NA.write('INIT:IMM')
        #prevent the controller from sending other commands to the analyzer
        self.NA.write('*WAI')
        #wait until the sweep is finished; bigger bandwidth corresponding to shorter time
        time.sleep(5)
        #set the trace format
        #self.NA.write('FORMAT:BORD NORM')
        #read the data of last trace
        #data = self.NA.write('CALC1:FORM MLIN')
        
        #Displays |z| in a Cartesian diagram
        # self.NA.write('CALC1:FORM MLIN')
        # data1 = self.NA.query('CALC1:DATA? FDATa')
        
        #Calculates |z| in dB (= 20 log|z|) and displays it in a Cartesian diagram
        self.NA.write('CALC1:FORM MLOG')
        data2 = self.NA.query('CALC1:DATA? FDATa')
                   
        #Calculates Re(z) = x and displays it in a Cartesian diagram                                                                                                                                                                                                               
        # self.NA.write('CALC1:FORM REAL')
        # data3 = self.NA.query('CALC1:DATA? FDATa')
        
        # #Calculates Im(z) = y and displays it in a Cartesian diagram
        # self.NA.write('CALC1:FORM IMAG')
        # data4 = self.NA.query('CALC1:DATA? FDATa')
        
        
        #data1 = self.NA.query('CALA1:DATA? FDATa')
        #data1 = self.NA.query('CALC1:DATA? SDATa')
        #return data1, data2, data3, data4
        return data2
        
        #data = self.NA.write(':FREQ:STAR?')
        #data = self.NA.ask_for_values('CALCulate1:DATA? FDATa')
        #self.NA.query('CALC:DATA:STIM?')
        #data = np.asarray(self.NA.query('CALC:DATA? FDAT'))
     
        
"""     
ip = 'TCPIP0::192.168.10.227::inst0::INSTR'        
RS_NA = NA(ip)
data = RS_NA.get_S(ch=1)
#print(len(data))
#print(type(data),data.len)
#print(np.shape(data))
print(data)
data = data.replace('\n','')
print(type(data))
data_list = data.split(',')

print(data_list)
print(len(data_list))

data_list = list(map(float, data_list))
print(data_list)

import matplotlib.pyplot as plt
plt.figure('sweep')
plt.plot(np.array(data_list))
plt.title('image') # 图像题目
"""