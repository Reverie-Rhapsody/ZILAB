# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:03:42 2020

@author: Rhapsody
"""
import pyvisa

class PSG_E8257D(object):
    """MW GENERATOR"""
    def __init__(self, device_ip):
        """连接仪器，初始化"""
        try:
            rm = pyvisa.ResourceManager()
            self.MW_GENERATOR = rm.open_resource(str(device_ip))
            
        except:
            print("没有连接，检查微波源ip是否正确")
            
        self.power = 0
        self.freq = 5
        
    def turn_on(self):
        """打开微波源输出"""
        self.MW_GENERATOR.write('OUTP ON')
        if int(self.MW_GENERATOR.query('OUTP?'))==1:
            print("LF output is on.")
        else:
            print("Caution! LF output is still off.")
        
    def turn_off(self):
        """关闭微波源输出"""
        self.MW_GENERATOR.write('OUTP OFF')
        if not int(self.MW_GENERATOR.query('OUTP?'))==1:
            print("LF output is off.")
        else:
            print("Caution! LF output is still on.")
            
    def set_power(self, power=-11):
        """设置微波源输出功率"""
        self.power = power
        self.MW_GENERATOR.write('POW:AMPL '+str(self.power)+'dBm')
        
    def set_freq(self, freq=5.0):
        """设置微波源输出频率"""
        self.freq = freq
        self.MW_GENERATOR.write('freq '+str(self.freq)+'GHz')
        
    def query_mode(self):
        """读取微波源波模式"""
        print(self.MW_GENERATOR.query('FREQ:MODE?'))
        
    def query_freq(self):
        """读取微波源频率"""
        print(self.MW_GENERATOR.query('FREQ?'))
    
    def query_power(self):
        """读取微波源功率"""
        print(self.MW_GENERATOR.query('POW:AMPL?'))
        
        
class PSG_E8257D_2(object):
    """MW GENERATOR"""
    def __init__(self, device_ip):
        """连接仪器，初始化"""
        try:
            rm = pyvisa.ResourceManager()
            self.MW_GENERATOR = rm.open_resource(str(device_ip))
            
        except:
            print("没有连接，检查微波源ip是否正确")
            
        self.power = 0
        self.freq = 5
        
    def turn_on(self):
        """打开微波源输出"""
        self.MW_GENERATOR.write('OUTP ON')
        if int(self.MW_GENERATOR.query('OUTP?'))==1:
            print("LF output is on.")
        else:
            print("Caution! LF output is still off.")
        
    def turn_off(self):
        """关闭微波源输出"""
        self.MW_GENERATOR.write('OUTP OFF')
        if not int(self.MW_GENERATOR.query('OUTP?'))==1:
            print("LF output is off.")
        else:
            print("Caution! LF output is still on.")
            
    def set_power(self, power=-11):
        """设置微波源输出功率"""
        self.power = power
        self.MW_GENERATOR.write('POW:AMPL '+str(self.power)+'dBm')
        
    def set_freq(self, freq=5.0):
        """设置微波源输出频率"""
        self.freq = freq
        self.MW_GENERATOR.write('freq '+str(self.freq)+'GHz')
        
    def query_mode(self):
        """读取微波源波模式"""
        print(self.MW_GENERATOR.query('FREQ:MODE?'))
        
    def query_freq(self):
        """读取微波源频率"""
        print(self.MW_GENERATOR.query('FREQ?'))
    
    def query_power(self):
        """读取微波源功率"""
        print(self.MW_GENERATOR.query('POW:AMPL?'))
        
        