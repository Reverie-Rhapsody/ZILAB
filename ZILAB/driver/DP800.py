# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 10:54:44 2021

@author: Rhapsody
"""

import numpy as np
import pyvisa

class DP800(object):
    """DP800series DC voltage resource"""
    def __init__(self, device_ip):
        """连接仪器，初始化"""
        self.device_ip = 'USB0::0x1AB1::0x0E11::DP8C204504949::INSTR'
        self.device_ip = device_ip
        try:
            rm = pyvisa.ResourceManager()
            self.DC = rm.open_resource(str(device_ip)) 
        except:
            print("没有连接，检查微波源ip是否正确")
        self.offset = 0
        self.ch = 1
        self.option = 'OFF'
        
    def set_value(self, ch=1, offset=0):
        self.ch = ch
        self.offset = offset
        self.DC.write(':SOUR{:d}:VOLT {:.2f}'.format(self.ch, self.offset))
        
    def get_value(self, ch=1):
        self.ch = ch
        print(self.DC.query(':SOUR{:d}:VOLT?'.format(self.ch)))
        
    def turn_on(self, ch=1, option='ON'):
        self.ch = ch
        self.option = option
        self.DC.write(':OUTP CH{:d},{:s}'.format(self.ch, self.option))
        
    def turn_off(self, ch=1, option='OFF'):
        self.ch = ch
        self.option = option
        self.DC.write(':OUTP CH{:d},{:s}'.format(self.ch, self.option))   
        
    def get_state(self, ch=1):
        self.ch = ch
        print('DC OUTPUT: '+self.DC.query(':OUTP? CH{:d}'.format(self.ch)))
        
        
        
        