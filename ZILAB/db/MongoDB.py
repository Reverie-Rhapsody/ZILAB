# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 14:53:18 2020

@author: Rhapsody
"""

import numpy as np
import re
import pymongo
import datetime
from bson.objectid import ObjectId

class mongodb(object):
    """用MongoDB数据库存储数据"""
    def __init__(self, database_host = 'mongodb://localhost:27017/'):
        """连接数据库"""
        try:
            self.client = pymongo.MongoClient(str(database_host))
        
        except:
            print("MongoDB数据库没有连接，检查MongoDB服务是否开启及host是否正确！")
        
        self.db = self.client.qulab106_characterization  #将名为`qulab106_characterization`的database赋给db,如果数据库不存在，会创建
        self.collection_cavity_spectroscopy = self.db.cavity_spectroscopy  #将名为`cavity_spectroscopy`的collection赋给collection_cavity_spectroscopy,如果collection不存在，会创建
        self.collection_qubit_spectroscopy = self.db.qubit_spectroscopy #将名为`qubit_spectroscopy`的collection赋给collection_qubit_spectroscopy,如果collection不存在，会创建
        self.collection_rabi = self.db.rabi  #将名为`rabi`的collection赋给collection_rabi,如果collection不存在，会创建
        self.collection_T1 = self.db.T1 #将名为`T1`的collection赋给collection_T1,如果collection不存在，会创建
        self.collection_T2 = self.db.T2 #将名为`T2`的collection赋给collection_T2,如果collection不存在，会创建
        self.collection_spinecho = self.db.spinecho #将名为`spinecho`的collection赋给collection_spinecho,如果collection不存在，会创建
        self.collection_picali = self.db.picali #将名为`picali`的collection赋给collection_picali,如果collection不存在，会创建
        self.collection_singleshot = self.db.singleshot #将名为`singleshot`的collection赋给collection_singleshot,如果collection不存在，会创建
        self.collection_rbm = self.db.rbm #将名为`rbm`的collection赋给collection_rbm,如果collection不存在，会创建
        self.collection_cavityvsflux = self.db.cavityvsflux #将名为`cavityvsflux`的collection赋给collection_cavityvsflux,如果collection不存在，会创建
        self.collection_jpa = self.db.jpa #将名为`jpa`的collection赋给collection_jpa,如果collection不存在，会创建
        self.collection_drag_cali = self.db.drag_cali #将名为`drag_cali`的collection赋给collection_drag_cali,如果collection不存在，会创建
        self.collection_cavity_vs_flux = self.db.cavity_vs_flux #将名为`cavity_vs_flux`的collection赋给collection_cavity_vs_flux,如果collection不存在，会创建
        
    def save_cavity_spectroscopy(self, result):
        document = {}
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        document['cavity spectroscopy result list'+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_cavity_spectroscopy.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved cavity spectroscopy result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_cavity_vs_flux(self, result):
        document = {}
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        document['cavity vs flux result list'+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_cavity_vs_flux.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved cavity vs flux result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_cavity_spectroscopy_vs_power(self, result):
        document = {}
        print(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        document['cavity spectroscopy result list vs power'+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_cavity_spectroscopy.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved cavity spectroscopy vs power result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_qubit_spectroscopy(self, result):
        document = {}
        document['qubit spectroscopy result list '+str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_qubit_spectroscopy.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved qubit spectroscopy result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_rabi(self, result):
        document = {}
        document['rabi result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_rabi.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved rabi result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_T1(self, result):
        document = {}
        document['T1 result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_T1.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved T1 result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_T2(self, result):
        document = {}
        document['T2 result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_T2.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved T2 result: " + str(post_id))
        print('-----------------------------------------------------')
    
    def save_spinecho(self, result):
        document = {}
        document['spin echo result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_spinecho.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved spin echo result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_picali(self, result):
        document = {}
        document['picali result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_picali.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved picali result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_singleshot(self, result):
        document = {}
        document['single shot result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_singleshot.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved single shot result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_cavity_vs_flux(self, result):
        document = {}
        document['cavity vs flux result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_cavity_vs_flux.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved cavity vs flux result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_rbm(self, result):
        document = {}
        document['randomized benchmarking result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_rbm.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved randomized benchmarking result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_jpa(self, result):
        document = {}
        document['jpa result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_jpa.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved drag cali result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def save_drag_cali(self, result):
        document = {}
        document['drag cali result list ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = result
        post = self.collection_drag_cali.insert_one(document)
        post_id = post.inserted_id
        print('-----------------------------------------------------')
        print("ID of the saved jpa result: " + str(post_id))
        print('-----------------------------------------------------')
        
    def read_data_cavity(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_cavity_spectroscopy.find_one({"_id": post_id})
        
        cavity_spectroscopy_result = data
        for key,value in cavity_spectroscopy_result.items():
            if not re.match('cavity spectroscopy result list', key, re.I)==None:
                cavity_spectroscopy_result_list = value
                #print(rabi_result_list)
        
        x_freq = cavity_spectroscopy_result_list[0]['freq_x']
        spectroscopy_result_real = cavity_spectroscopy_result_list[1]['spectroscopy_result_real']
        spectroscopy_result_imag = cavity_spectroscopy_result_list[2]['spectroscopy_result_imag']
        spectroscopy_result_complex = np.array(spectroscopy_result_real)+1j*np.array(spectroscopy_result_imag)
        
        result = [x_freq, spectroscopy_result_complex]
        return result
    
    def read_data_cavity_vs_power(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_cavity_spectroscopy.find_one({"_id": post_id})
        
        cavity_spectroscopy_vs_power_result = data
        for key,value in cavity_spectroscopy_vs_power_result.items():
            if not re.match('cavity spectroscopy result list vs power', key, re.I)==None:
                cavity_spectroscopy_vs_power_result_list = value
        
        freq_x = cavity_spectroscopy_vs_power_result_list[0]['freq_x']
        amplitude_y = cavity_spectroscopy_vs_power_result_list[1]['amplitude_y']
        data_power = np.array(cavity_spectroscopy_vs_power_result_list[2]['data_power'])
        
        result = [freq_x, amplitude_y, data_power]
        return result
    
    def read_data_cavity_vs_flux(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_cavity_vs_flux.find_one({"_id": post_id})
        
        cavity_vs_flux_result = data
        for key,value in cavity_vs_flux_result.items():
            if not re.match('cavity vs flux result list', key, re.I)==None:
                cavity_vs_flux_result_list = value
        
        freq_x = cavity_vs_flux_result_list[0]['freq_x']
        voltage_y = cavity_vs_flux_result_list[1]['voltage_y']
        data_2d = np.array(cavity_vs_flux_result_list[2]['data_flux'])
        
        result = [freq_x, voltage_y, data_2d]
        return result
    
    def read_data_qubit(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_qubit_spectroscopy.find_one({"_id": post_id})
        
        qubit_spectroscopy_result = data
        for key,value in qubit_spectroscopy_result.items():
            if not re.match('qubit spectroscopy result list ', key, re.I)==None:
                qubit_spectroscopy_result_list = value
        
        freq_x = qubit_spectroscopy_result_list[0]['freq_x']
        spectroscopy_real = qubit_spectroscopy_result_list[1]['spectroscopy_real']
        spectroscopy_imag = qubit_spectroscopy_result_list[2]['spectroscopy_imag']
        spectroscopy_complex = np.abs(np.array(spectroscopy_real)+1j*np.array(spectroscopy_imag))
        result = [freq_x, spectroscopy_complex]
        return result
    
    def read_data_rabi(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_rabi.find_one({"_id": post_id})
        
        rabi_result = data
        for key,value in rabi_result.items():
            if not re.match('rabi result list ', key, re.I)==None:
                rabi_result_list = value
                
        time_x = np.array(rabi_result_list[0]['time_x'])*1e6
        rabi_real = rabi_result_list[1]['rabi_real']
        rabi_imag = rabi_result_list[2]['rabi_imag']
        rabi_complex = np.abs(np.array(rabi_real)+1j*np.array(rabi_imag))
        
        result = [time_x, rabi_complex]
        return result
    
    def read_data_T1(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_T1.find_one({"_id": post_id})
        
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
        
        result = [time_x, T1_complex]
        return result
    
    def read_data_T2(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_T2.find_one({"_id": post_id})
        
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
        
        result = [time_x, T2_complex]
        return result
    
    def read_data_spinecho(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_spinecho.find_one({"_id": post_id})
        
        spinecho_result = data
        for key, value in spinecho_result.items():
            if not re.match('spin echo result list ', key, re.I)==None:
                spinecho_result_list = value
                
        time_increment = spinecho_result_list[3]['time_increment']
        rate = time_increment*8*(1e6)/(1.8e9) 
        time_x = np.array(spinecho_result_list[0]['time_x'])*rate #单位是微秒
        spinecho_real = spinecho_result_list[1]['spinecho_real']
        spinecho_imag = spinecho_result_list[2]['spinecho_imag']
        detuning = spinecho_result_list[4]['detuning'] #失谐
        spinecho_complex = np.abs(np.array(spinecho_real)+1j*np.array(spinecho_imag))
        
        result = [time_x, spinecho_complex]
        return result
        
    def read_data_picali(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_picali.find_one({"_id": post_id})
        
        picali_result = data
        for key, value in picali_result.items():
            if not re.match('picali result list ', key, re.I)==None:
                picali_result_list = value
        
        pulse_list = picali_result_list[0]['pulse_list']
        power_list = picali_result_list[1]['power_list']
        data_2D = picali_result_list[2]['picali']
        result = [pulse_list, power_list, data_2D]
        return result
         
    def read_data_singleshot(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_singleshot.find_one({"_id": post_id})
        
        singleshot_result = data
        for key, value in singleshot_result.items():
            if not re.match('single shot result list ', key, re.I)==None:
                singleshot_result_list = value
        
        data_ch_1 = singleshot_result_list[0]['data_ch_1']
        data_ch_2 = singleshot_result_list[1]['data_ch_2']
        data_ch_11 = singleshot_result_list[2]['data_ch_11']
        data_ch_22 = singleshot_result_list[3]['data_ch_22']
        result = [data_ch_1, data_ch_2, data_ch_11, data_ch_22]
        return result
    
    def read_data_rbm(self, post_id):
        post_id = ObjectId(post_id)
        data = self.collection_rbm.find_one({"_id": post_id})
        
        rbm_result = data
        for key, value in rbm_result.items():
            if not re.match('randomized benchmarking result list ', key, re.I)==None:
                rbm_result_list = value
        
        data_ch_1 = rbm_result_list[0]['data_ch_1']
        data_ch_2 = rbm_result_list[1]['data_ch_2']
        data = rbm_result_list[2]['data']
        data_mean = rbm_result_list[3]['data_mean']
        m_x = rbm_result_list[4]['m_x']
        num_per_m = rbm_result_list[5]['num_per_m']
        result = [m_x, num_per_m, data_ch_1, data_ch_2, data, data_mean]
        return result
    
    def read_data_cavityvsflux(self, post_id):
        post_id = ObjectId(post_id)
        cavityvsflux_result = self.collection_cavityvsflux.find_one({"_id": post_id})
       
        for key, value in cavityvsflux_result.items():
            if not re.match('cavity vs flux result list ', key, re.I)==None:
                cavityvsflux_result_list = value
                
        freq_x = cavityvsflux_result_list[0]['freq_x']
        dc_voltage = cavityvsflux_result_list[1]['dc_voltage']
        data = cavityvsflux_result_list[2]['data']
        result = [freq_x, dc_voltage, data]
        return result
    
    
    def read_data_jpa(self, post_id):
        post_id = ObjectId(post_id)
        jpa_result = self.collection_jpa.find_one({"_id": post_id})
       
        for key, value in jpa_result.items():
            if not re.match('jpa result list ', key, re.I)==None:
                jpa_result_list = value
        
        freq_x = jpa_result_list[0]['freq_x']
        dc_voltage = jpa_result_list[1]['dc_voltage']
        data_real_2d = jpa_result_list[2]['data_real_2d']
        data_imag_2d = jpa_result_list[3]['data_imag_2d']
        result = [freq_x, dc_voltage, data_real_2d, data_imag_2d]
        return result
    
    def read_data_drag_cali(self, post_id):
        
        post_id = ObjectId(post_id)
        drag_cali_result = self.collection_drag_cali.find_one({"_id": post_id})
       
        for key, value in drag_cali_result.items():
            if not re.match('drag cali result list ', key, re.I)==None:
                drag_cali_result_list = value
                
        drag_amplitude_list = drag_cali_result_list[0]['drag_amplitude_list']
        data_complex = drag_cali_result_list[1]['data_complex']
        result = [drag_amplitude_list, data_complex]
        return result
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        