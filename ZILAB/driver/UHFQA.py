# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 21:14:35 2019
Zurich Instruments
@author:  liufei@zhinst.com
"""
import zhinst.utils
import textwrap
import time
import math
import numpy as np
import matplotlib.pyplot as plt


class zurich_qa(object):
    """AWG """
    
    def __init__(self, device_id): 
        """Initialize the UHFQA"""
        required_devtype = 'UHFQA'
        required_options = ['']
        try:
            self.daq, self.device, info= zhinst.utils.create_api_session(device_id, 6, required_devtype=required_devtype, required_options=required_options)
            zhinst.utils.disable_everything(self.daq, self.device) 
            #self.daq = zhinst.ziPython.ziDAQServer('10.21.6.154', 8004, 6) #用ip的形式访问
            #self.daq = zhinst.ziPython.ziDAQServer('192.168.10.40', 8004, 6) #用ip的形式访问
            #self.device = device_id
            #initialize_device(self.daq, self.device)
        except:
            print('No connection is availabe, please check whether Labone can find the Instrument.')
        
        #self.average = 1024  # 'self.num_averages=1' means no hardware average.
        self.result_length = 100
        self.result_length_pulse = 100  #awg_builder_picali变pulse长度次数
 
        self.result_length_power = 6    #awg_builder_picali变pulse振幅次数
        self.channels = [] # channel from 0 to 9; 
        self.qubit_frequency = []
        self.paths = []
        
        self.pulse_length = 0
        self.integration_length = 0 
#        self.set_demodulation_default()
  
        self.sampling_rate = 1.8e9
        self.readout_length = 2e-6
        self.num_averages = 1 #2^N  'self.num_averages=1' means no hardware average.
        self.time_origin_sec = 1000e-9
        self.period_wait_sec = 1000e-9
        self.delay_align_sec = 70e-9
        self.amplitude_probe = 1.0 #probe 波形前乘以的系数，起到调节probe power的作用，实际probe power应为total_amplitude*amplitude_probe*base_power 
        self.range_probe = 1.5
        self.osc_path = '/' + self.device +'/oscs/0/freq'
  
       
        #set output range / V
        self.daq.setDouble('/{:s}/sigouts/*/range'.format(self.device), self.range_probe) # output1.5vpeak
        #set input range / V
        self.daq.setDouble('/{:s}/sigins/*/range'.format(self.device), 1) # 输入量程1v
        self.daq.setInt('/{:s}/sigins/*/imp50'.format(self.device), 1) # 50Ω输入阻抗
        self.daq.setInt('/{:s}/sigins/*/ac'.format(self.device), 1) # ac coupling on
        
        self.daq.setInt('/{:s}/triggers/out/0/source'.format(self.device), 32)# 32= awg trigger 1
        self.daq.setInt('/{:s}/triggers/out/*/drive'.format(self.device), 1)
        # Set DIO output to qubit result
        self.daq.setInt('/{:s}/dios/0/drive'.format(self.device), 15)
        self.daq.setInt('/{:s}/dios/0/mode'.format(self.device),2)
        # Sample DIO data at 50 MHz
        self.daq.setInt('/{:s}/dios/0/extclk'.format(self.device), 2)
        self.daq.setInt('/{:s}/system/extclk'.format(self.device), 1)
        
    def set_demodulation_default(self):
        """Make the default setting of demodulation"""
        
        self.set_deskew_matrix()
        self.set_delay()
        for i in range(10):
            self.set_rotation( i, rotation = 1, input_mapping = 0)
        self.set_integration_length()
        self.spectroscopy(mode_on = 0)
        self.set_result_path(source = 7)
         # 跳过crosstalk 操作，节约时间
        self.daq.setInt('/{:s}/qas/0/crosstalk/bypass'.format(self.device), 1)
  
    """
    def set_relative_amplitude(self):
        self.daq.setDouble('/{:s}/awgs/0/outputs/*/amplitude'.format(self.device), self.amplitude_probe_1)   
    """
    
    def set_total_amplitude(self, awgcore=0, amplitude=0.133):
        #set the amplitude factor of the pulse, this setting takes effect for all the outputs under this awg core. 
        self.daq.setDouble('/{:s}/awgs/{:s}/outputs/*/amplitude'.format(self.device, str(awgcore)), amplitude)   

    def set_pulse_length(self, pulse_length):
        self.pulse_length =  pulse_length
        self.set_integration_length(int(self.pulse_length))

    
    def awg_builder(self, sampling_rate = 1.8e9, waveform = [[0.111,0.222], [0.333,0.444]], trigger = 0):     
        """Make an awg sequence, then play the waveform. It can work on the "trigger=1" triggered mode.
        Check the value of each point and should not exceed 1. The waveform has no unit and should not exceed 1."""
        
        assert np.max(waveform) <= 1, '\n waveform value is dimensionless, less than 1. Check waveform values before proceed.\n'     
        #Build the waveform
        define_str = 'wave wave0 = vect(_w_);\n'
        str0 = ''
        play_str = ''
        for i in range(len(waveform)):
            # wave wave1 = vect(_w1); wave wave2 = vect(_w2_);...
            str0 = str0 + define_str.replace('0', str(i+1)).replace('_w_', ','.join([str(x) for x in waveform[i]]))
            # 1, w1, 2, w2, ....
            play_str = play_str + (  ','+ str(i+1) + ', wave'+str(i+1) )
        
        play_str = play_str[1:]
        
        awg_program = textwrap.dedent("""\
 
$str0       
const f_s = 1.8e9;
const delay_align_sec = 7e-8;
const time_origin_sec = 3e-6;

setTrigger(AWG_INTEGRATION_ARM); // Start the demodulator.

setTrigger(0b000);
repeat(getUserReg(0)){
repeat (getUserReg(1)) {

       //setTrigger(0b100); wait(21); setTrigger(0b000);
       setTrigger(0);wait(20);setTrigger(1);//
       wait((time_origin_sec + delay_align_sec)*(f_s/8));
       //waitDigTrigger(1, 1);
        setTrigger(AWG_INTEGRATION_ARM + AWG_INTEGRATION_TRIGGER + AWG_MONITOR_TRIGGER);// 开始抓取信号，进行integration
        setTrigger(AWG_INTEGRATION_ARM); // Reset
        playWave($play_str);
    
        waitWave();
        wait(1000e-9*225e6); //Wait ~1000ns before sending the next.
}
}        """)
        awg_program = awg_program.replace('$str0', str0)
        awg_program = awg_program.replace('$play_str', play_str)

        #If it is in trigger mode, add a trigger command, and the trigger is on the rising edge of trigger input 1.
        if trigger !=0:
            awg_program = awg_program.replace('//waitDigTrigger(1)；','waitDigTrigger(1);') # set trigger
            # trigger on the rise edge, the physical trigger port is trigger 1 at the front panel
            #impedance 50 at trigger input. trigger level 0.7 
            self.daq.setInt('/{:s}/awgs/0/auxtriggers/0/slope'.format(self.device), 1)
            self.daq.setInt('/{:s}/awgs/0/auxtriggers/0/channel'.format(self.device), 0)
            self.daq.setInt('/{:s}/triggers/in/0/imp50'.format(self.device), 0)            
            self.daq.setDouble('/{:s}/triggers/in/0/level'.format(self.device), 0.7)
            
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_general(self):
        """Make an awg sequence which can be used for spec, T1, T2"""
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;
        const f_seq = f_base/8;
    
        const result_length = _c0_;  // number of points
        const num_averages = _c4_;
        const time_origin_sec = _c2_;
        const period_wait_sec = _c5_;
    
        const delay_align_sec = _c6_; // adjust this number if necessary to align the control and readout pulse
        const pulse_width_sec = _c1_; // width of the readout pulse
        const waveform_length_sec = pulse_width_sec;
        const waveform_length = waveform_length_sec*f_base;
    
        wave w_I_qb1 = _c3_*ones(waveform_length);
        wave w_Q_qb1 = _c3_*ones(waveform_length);
    
        //setTrigger(AWG_INTEGRATION_ARM);
        repeat(num_averages){
        repeat(result_length) {
                //setTrigger(0b00);wait(20);setTrigger(0b01);//
                setTrigger(0);wait(20);setTrigger(1);//
                wait((time_origin_sec + delay_align_sec)*f_seq);
                //playZero((time_origin_sec + delay_align_sec)*f_base);
                setTrigger(AWG_INTEGRATION_ARM + AWG_INTEGRATION_TRIGGER + AWG_MONITOR_TRIGGER);
                playWave(w_I_qb1, w_Q_qb1);
                waitWave();
                setTrigger(AWG_INTEGRATION_ARM);
                wait(period_wait_sec*f_seq);
            }
        }
        """)
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c1_', str(self.readout_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.amplitude_probe))
        awg_program = awg_program.replace('_c4_', str(self.num_averages))
        awg_program = awg_program.replace('_c5_', str(self.period_wait_sec))
        awg_program = awg_program.replace('_c6_', str(self.delay_align_sec))
            
        self.awg_upload_string(awg_program)
        
    def awg_builder_picali(self):
        """Make an awg sequence, which can be used for Pi Pulse Calibration"""       
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;
        const f_seq = f_base/8;
    
        const result_length_pulse = _c0_;  // number of points
        const result_length_power = _c7_;
        const num_averages = _c4_;
        const time_origin_sec = _c2_;
        const period_wait_sec = _c5_;
    
        const delay_align_sec = _c6_; // adjust this number if necessary to align the control and readout pulse
        const pulse_width_sec = _c1_; // width of the readout pulse
        const waveform_length_sec = pulse_width_sec;
        const waveform_length = waveform_length_sec*f_base;
    
        wave w_I_qb1 = _c3_*ones(waveform_length);
        wave w_Q_qb1 = _c3_*ones(waveform_length);
    
        //setTrigger(AWG_INTEGRATION_ARM);
        repeat(num_averages){
            repeat(result_length_power){
                repeat(result_length_pulse){
                    setTrigger(0b00); wait(20); setTrigger(0b01);//
                    wait((time_origin_sec + delay_align_sec)*f_seq);
                    setTrigger(AWG_INTEGRATION_ARM + AWG_INTEGRATION_TRIGGER + AWG_MONITOR_TRIGGER);
                    playWave(w_I_qb1, w_Q_qb1);
                    waitWave();
                    setTrigger(AWG_INTEGRATION_ARM);
                    wait(period_wait_sec*f_seq);
                }
            }
        }
        """)
        awg_program = awg_program.replace('_c0_', str(self.result_length_pulse))
        awg_program = awg_program.replace('_c1_', str(self.readout_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.amplitude_probe))
        awg_program = awg_program.replace('_c4_', str(self.num_averages))
        awg_program = awg_program.replace('_c5_', str(self.period_wait_sec))
        awg_program = awg_program.replace('_c6_', str(self.delay_align_sec))
        awg_program = awg_program.replace('_c7_', str(self.result_length_power))
            
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_rbm(self):
        """Clifford Based Randomized Benchmarking, AWG of UHFQA Trigger&Probe Sequence"""
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;
        const f_seq = f_base/8;
    
        const result_length_ave = _c0_;  // number of points
        const result_length_sizeleng = _c7_;
        const num_averages = _c4_;
        const time_origin_sec = _c2_;
        const period_wait_sec = _c5_;
    
        const delay_align_sec = _c6_; // adjust this number if necessary to align the control and readout pulse
        const pulse_width_sec = _c1_; // width of the readout pulse
        const waveform_length_sec = pulse_width_sec;
        const waveform_length = waveform_length_sec*f_base;
    
        wave w_I_qb1 = _c3_*ones(waveform_length);
        wave w_Q_qb1 = _c3_*ones(waveform_length);
    
        //setTrigger(AWG_INTEGRATION_ARM);
        repeat(num_averages){
            repeat(result_length){
                setTrigger(0b00); wait(20); setTrigger(0b01);//
                wait((time_origin_sec + delay_align_sec)*f_seq);
                setTrigger(AWG_INTEGRATION_ARM + AWG_INTEGRATION_TRIGGER + AWG_MONITOR_TRIGGER);
                playWave(w_I_qb1, w_Q_qb1);
                waitWave();
                setTrigger(AWG_INTEGRATION_ARM);
                wait(period_wait_sec*f_seq);
            }
        }
        """)
        awg_program = awg_program.replace('_c0_', str(self.result_length_ave))
        awg_program = awg_program.replace('_c1_', str(self.readout_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.amplitude_probe_2))
        awg_program = awg_program.replace('_c4_', str(self.num_averages))
        awg_program = awg_program.replace('_c5_', str(self.period_wait_sec))
        awg_program = awg_program.replace('_c6_', str(self.delay_align_sec))
        awg_program = awg_program.replace('_c7_', str(self.result_length_sizeleng))
            
        self.awg_upload_string(awg_program)
        
        
    def awg_upload_string(self,awg_program, awg_index = 0): 
        """Write the waveform and compile.
        'awg_program' is an AWG sequence of string type.
        'awg_index' is the serial number of the AWG. When the grouping is 4*2, there are 4 AWGs and 'awg_index=0' refer to the first AWG."""
        
        awgModule = self.daq.awgModule()
        awgModule.set('awgModule/device', self.device)
        awgModule.set('awgModule/index', awg_index)# AWG 0, 1, 2, 3
        awgModule.execute()
        awgModule.set('awgModule/compiler/sourcestring', awg_program)
        while awgModule.getInt('awgModule/compiler/status') == -1:
            time.sleep(0.1)
        # Ensure that compilation was successful
        if awgModule.getInt('awgModule/compiler/status') == 1:
            # compilation failed, raise an exception
            raise Exception(awgModule.getString('awgModule/compiler/statusstring'))
        else:
            if awgModule.getInt('awgModule/compiler/status') == 0:
                print("Compilation successful with no warnings, will upload the program to the instrument.")
            if awgModule.getInt('awgModule/compiler/status') == 2:
                print("Compilation successful with warnings, will upload the program to the instrument.")
#                print("Compiler warning: ", awgModule.getString('awgModule/compiler/statusstring'))
            # wait for waveform upload to finish
            i = 0
            while awgModule.getDouble('awgModule/progress') < 1.0:
                #print("{} awgModule/progress: {}".format(i, awgModule.getDouble('awgModule/progress')))
                time.sleep(0.1)
                i += 1
            #print("{} awgModule/progress: {}".format(i, awgModule.getDouble('awgModule/progress')))
#        print(awg_program)
        print('\n AWG upload successful. Output enabled. AWG Standby. \n')

    def set_result(self):
        self.daq.setInt('/{:s}/qas/0/result/length'.format(self.device), self.result_length)#results length 
        self.daq.setInt('/{:s}/qas/0/result/averages'.format(self.device), self.num_averages)# average results
        #以下会设置读取脉冲的循环次数
        self.daq.setDouble('/{:s}/awgs/0/userregs/0'.format(self.device), self.num_averages)# average results
        self.daq.setDouble('/{:s}/awgs/0/userregs/1'.format(self.device), self.result_length)# average results   
 
    def awg_open(self, run = 1):
        self.daq.setInt('/{:s}/qas/0/result/reset'.format(self.device), 1)  #Reset the cache and clear the original data.
        self.daq.setInt('/{:s}/qas/0/result/enable'.format(self.device), 0) #Make the cache wait for writing.        
        self.daq.sync() 
        self.set_result()
        self.daq.setInt('/{:s}/qas/0/result/reset'.format(self.device), 1)  #Reset the cache and clear the original data. 
        self.daq.setInt('/{:s}/qas/0/result/enable'.format(self.device), 1) #Make the cache wait for writing. 
        #Turn on the AWG, turn on the output, set the output range.
        # run = 1 start AWG, run =0 close AWG
        self.daq.setInt('/{:s}/sigouts/*/on'.format(self.device), run)
        self.daq.setInt('/{:s}/awgs/0/single'.format(self.device), 1) #In order to prevent error, never use the rerun mode.
            # Arm the device
        self.daq.sync() 
        while not(self.daq.getInt('/{:s}/awgs/0/ready'.format(self.device))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/0/enable'.format(self.device), run)
    
    def channel_close(self):
        self.daq.setInt('/{:s}/sigouts/*/on'.format(self.device), 0)
        
    def awg_close(self):
        while not(self.daq.getInt('/{:s}/awgs/0/ready'.format(self.device))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/0/enable'.format(self.device), 0)

        
    def update_qubit_frequency(self, frequency_array):
        """Update demodulation weight, channels and paths."""
        
        self.channels = [] # channel from 0 to 9;  
        self.qubit_frequency = frequency_array
        print(self.pulse_length)
        print(type(self.pulse_length))
        time_axis = np.linspace(0, int(self.pulse_length-1), int(self.pulse_length))/1.8e9

        for i in range(len(self.qubit_frequency)):
#            print('frequency demodulation is :')
#            print(self.qubit_frequency[i])
            #Update demodulator/channel
            self.channels.append(i)          
            weights_real = np.cos(time_axis*self.qubit_frequency[i]*2*math.pi) 
            weights_imag = np.sin(time_axis*self.qubit_frequency[i]*2*math.pi)    
            # print('------------')
            # print(len(weights_real))
            # print(len(weights_imag))
            # print('------------')
            w_real = np.array(weights_real)
            w_imag = np.array(weights_imag)
            self.daq.setVector('/{:s}/qas/0/integration/weights/{}/real'.format(self.device, i), w_real)
            self.daq.setVector('/{:s}/qas/0/integration/weights/{}/imag'.format(self.device, i), w_imag)
          
        self.set_result_path()
                      

    
    def set_integration_length(self, length = 4096):
        """Set the integration length"""
        
        self.daq.setDouble('/{:s}/qas/0/integration/length'.format(self.device), length)
        self.integration_length = int(self.daq.getDouble('/{:s}/qas/0/integration/length'.format(self.device)))


    def set_rotation(self, channel, rotation = 1, input_mapping = 0):
        # Apply a rotation on half the channels to get the imaginary part instead
        self.daq.setComplex('/{:s}/qas/0/rotations/{:d}'.format(self.device, channel), rotation)  
        # Swap signal inputs for the second QA channel : input mapping->2 real, 1 imag
        self.daq.setInt('/{:s}/qas/0/integration/sources/{:d}'.format(self.device, channel), input_mapping)
          
    def set_result_path(self, source = 2): 
        # Now we're ready for readout. Enable monitor and start acquisition.
        self.daq.setInt('/{:s}/qas/0/result/reset'.format(self.device), 1)  #Reset the cache and clear the original data.
        self.daq.setInt('/{:s}/qas/0/result/enable'.format(self.device), 1) #Make the cache wait for writing. 
#        self.daq.unsubscribe('*')
        self.paths = []
        # source = 2 after rotation; 7 integration; 1 threshold
        self.daq.setInt('/{:s}/qas/0/result/source'.format(self.device), source) # 2,  result after rotation

        for ch in self.channels:
            path = '/{:s}/qas/0/result/data/{:d}/wave'.format(self.device, ch)
            self.paths.append(path)
            
#        print('\n', 'Subscribed paths: \n ', self.paths, '\n')
        self.daq.subscribe(self.paths)
   
    def set_monitor(self, run =1, average_on = 1 ):
        """Setup monitor"""
        
        if average_on:
            self.daq.setInt('/{:s}/qas/0/monitor/averages'.format(self.device), self.result_length)
        else:
            self.daq.setInt('/{:s}/qas/0/monitor/averages'.format(self.device), 1)
#        monitor_average = self.daq.getInt('/{:s}/qas/0/monitor/averages'.format(self.device))
        self.daq.setInt('/{:s}/qas/0/monitor/length'.format(self.device), 4096)
    
        # Now we're ready for readout. Enable monitor and start acquisition.
        self.daq.setInt('/{:s}/qas/0/monitor/reset'.format(self.device), 1)
        self.daq.setInt('/{:s}/qas/0/monitor/enable'.format(self.device), run)
                # Subscribe to monitor waves
        paths = []
        for channel in range(2):
            path = '/{:s}/qas/0/monitor/inputs/{:d}/wave'.format(self.device, channel)
            paths.append(path)
        self.daq.subscribe(paths)
      
    def stop_subscribe(self):     
        """Stop the result unit"""
        
        self.daq.unsubscribe(self.paths)
        self.daq.setInt('/{:s}/qas/0/result/enable'.format(self.device), 0)
        
    
    def set_threshold(self, threshold_array):
        # 设置某个解调器的 0/1判断阈值。 [ [解调器,阈值],[解调器,阈值],[解调器,阈值],[解调器,阈值]]
        for i in range(len(threshold_array)):
            self.daq.setDouble('/{:s}/qas/0/thresholds/{}/level'.format(self.device, threshold_array[i][0]), threshold_array[i][1])

        
    def set_delay(self,delay =224):
        #设置截取信号的起始点, 这个指令在spectroscopy 模式下，不影响结果
        self.daq.setDouble('/{:s}/qas/0/delay'.format(self.device), delay);
 
    def spectroscopy(self, uhf_frequency = 100e6, mode_on = 1):
        self.daq.setInt('/{:s}/qas/0/integration/mode'.format(self.device), mode_on)#sepctroscopy mode
        self.daq.setDouble('/{:s}/oscs/0/freq'.format(self.device), uhf_frequency )
        self.daq.setInt('/{:s}/awgs/0/outputs/*/mode'.format(self.device), mode_on)#modulation mode

        
    def get_result(self, do_plot = 0):
        #self.set_result_path(source = 2)  #此步如果省略，由于没有reset,会使采集的数据结果不正常
        # Perform acquisition
        #self.daq.setInt('/{:s}/qas/0/result/reset'.format(self.device), 1)  #重置缓存，清除原来的数据 
        #self.daq.setInt('/{:s}/qas/0/result/enable'.format(self.device), 1) #使缓存处于等待写入状态
        time_start = time.time()
        data = self.acquisition_poll(self.daq, self.paths, self.result_length, timeout=180.0)
        time_end=time.time()
        print('\n time cost',time_end-time_start,'s \n')
        
        if do_plot:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.set_title('Result unit')
            ax.set_ylabel('Amplitude (a.u.)')
            ax.set_xlabel('Measurement (#)')
            for path, samples in data.items():
                ax.plot(samples, label='{}'.format(path))
            plt.legend(loc='best')
            fig.set_tight_layout(True)
            plt.show()
        return data
    
    def set_deskew_matrix(self, theta = 0):
        # * exp(i*theta)
        #[1,                  np.sin(theta/180*pi)],
        #[-np.sin(theta/180*np.pi), np.cos(theta/180*pi)]
        if type(theta)== int:
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/0'.format(self.device),  np.cos(theta/180*np.pi))
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/1'.format(self.device),  np.sin(theta/180*np.pi))
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/0'.format(self.device), -np.sin(theta/180*np.pi))
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/1'.format(self.device), np.cos(theta/180*np.pi))
            
        if type(theta) == np.ndarray:
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/0'.format(self.device),  theta[0][0])
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/1'.format(self.device),  theta[0][1])
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/0'.format(self.device), theta[1][0])
            self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/1'.format(self.device), theta[1][1])
        
        self.daq.sync()
        return np.mat([[self.daq.getDouble('/{:s}/qas/0/deskew/rows/0/cols/0'.format(self.device)), 
                        self.daq.getDouble('/{:s}/qas/0/deskew/rows/0/cols/1'.format(self.device))], 
                       [self.daq.getDouble('/{:s}/qas/0/deskew/rows/1/cols/0'.format(self.device)),
                        self.daq.getDouble('/{:s}/qas/0/deskew/rows/1/cols/1'.format(self.device))] ])
    
    def set_deskew_matrix_2(self, list=[1,0,0,1]):
        """Set deskew matrix"""
        
        self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/0'.format(self.device),  list[0])
        self.daq.setDouble('/{:s}/qas/0/deskew/rows/0/cols/1'.format(self.device),  list[1])
        self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/0'.format(self.device),  list[2])
        self.daq.setDouble('/{:s}/qas/0/deskew/rows/1/cols/1'.format(self.device),  list[3])
    
    def spectroscopy_scan_frequency(self, ts, fre_array, do_plot = 0):
        self.set_demodulation_default()
        self.spectroscopy(mode_on = 1) #
        self.update_qubit_frequency([0, 0]) # Update the channel for fetching data.
        #two phase demodulation.
        self.set_rotation(0, rotation = 1-1j, input_mapping= 1 )
        self.set_rotation(1, rotation = 1+1j, input_mapping= 0 )
        self.set_result_path(source = 2 )# 7=读取integration, 2 = rotation后的数值
        fs = 1.8e9 # sampling rate    
        read_length = np.floor(ts*fs/8)*8
        self.set_pulse_length(read_length)
 
        #计算用于读取信号
        waveform_sine  = [1]* int(self.integration_length)
        self.awg_builder(waveform = [ waveform_sine, waveform_sine ], trigger = 0)
        osc_path = '/' + self.device +'/oscs/0/freq'
        data_ch_1 = []
        data_ch_2 = []
        for i in fre_array:
            self.daq.setDouble(osc_path, i)
            print('\n osc frequency:', self.daq.getDouble(osc_path),'\n')
            self.awg_open()
            tmp = self.get_result(do_plot = 0)
            data_ch_1.append(np.mean(tmp[self.paths[0]])) # Real part
            data_ch_2.append(np.mean(tmp[self.paths[1]])) # Imaginary part
        if do_plot:
                plt.figure('spectroscopy mode_two demodulator_frequency sweep')
                plt.plot(fre_array, np.abs(data_ch_1))  
        return data_ch_1,data_ch_2    

    def standard_scan_frequency(self, ts, fre_array, do_plot = 1):
        self.set_demodulation_default()
#        self.set_delay(504)

        #双相解调
        self.set_rotation(0, rotation = 1-1j, input_mapping= 1 )
        self.set_rotation(1, rotation = 1+1j, input_mapping= 0 )
        self.set_result_path(source = 2 )# 7=读取integration, 2 = rotation后的数值
        fs = 1.8e9 # sampling rate
        read_length = np.floor(ts*fs/8)*8
        self.set_pulse_length(read_length)
        self.set_integration_length(read_length)
        time_axis = np.linspace(0,  self.pulse_length -1, self.pulse_length)/1.8e9

        data_ch_1 = []
        for i in fre_array:
        #计算用于读取信号
            self.update_qubit_frequency([i, i]) # Update the channel for fetching data.
            waveform_sine  =  np.sin(2*np.pi*time_axis*i)
            waveform_cosine = np.cos(2*np.pi*time_axis*i)
            self.awg_builder(waveform = [ waveform_sine, waveform_cosine ], trigger = 0)
            print('\n readout pulse fre is :', self.qubit_frequency, '\n')
#            time.sleep(0.5)
            self.awg_open()
            tmp = self.get_result(do_plot = 0)
            data_ch_1.append(np.mean(tmp[self.paths[0]])  + 1j* np.mean(tmp[self.paths[1]]))
        
        if do_plot:
                plt.figure('standard mode_frequency sweep')
                plt.plot(fre_array, np.abs(data_ch_1)) 
        return data_ch_1        
   
    def power_frequency_sweep(self, amlitude_array, frequency_array):
        pass
    
    def rabi(self, freq):
        self.set_demodulation_default()
        
        
    def set_osc(self, freq=100e6):
        """Set the frequency of oscillator."""
        
        self.daq.setDouble(self.osc_path, freq)
        print('\n osc frequency:', self.daq.getDouble(self.osc_path),'\n')
    
    def set_output_range(self):
        #set output range / V
        self.daq.setDouble('/{:s}/sigouts/*/range'.format(self.device), self.range_probe) # output1.5vpeak

    def get_monitor(self, do_plot = 0):
        """Subscribe to monitor waves"""
        
        paths = []
        for channel in range(2):
            path = '/{:s}/qas/0/monitor/inputs/{:d}/wave'.format(self.device, channel)
            paths.append(path)
        self.daq.subscribe(paths)
 
        # Perform acquisition
        print('Acquiring data...')
        data = self.acquisition_poll(self.daq, paths, 4096)
        print('Done.')
        monitor_average = self.daq.getInt('/{:s}/qas/0/monitor/averages'.format(self.device))

        if do_plot:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.set_title('Input averager results after {:d} measurements'.format(monitor_average))
            ax.set_ylabel('Amplitude (a.u.)')
            ax.set_xlabel('Sample (#)')
            for path, samples in data.items():
                ax.plot(samples, label='Readout {}'.format(path))
            plt.legend(loc='best')
            fig.set_tight_layout(True)
            plt.show()
        return data
    
    def demonstrate_processing(self, do_plot = 1):
        self.set_demodulation_default()
        self.result_length = 100 #一共发送result_length个读取脉冲
        fs = 1.8e9 # sampling rate
        ts = 2e-6 #Probe pulse length / s
        read_length = np.floor(ts*fs/8)*8
        self.set_pulse_length(read_length)
        self.update_qubit_frequency([100e6, 100e6]) # set frequency of I, Q for probe
        time_axis = np.linspace(0,  read_length -1, read_length)/1.8e9
        #计算用于读取信号
        waveform_sine  = (np.sin(2*np.pi*time_axis*self.qubit_frequency[0])) 
        waveform_cosine =(np.cos(2*np.pi*time_axis*self.qubit_frequency[0]))

    
        self.awg_builder(waveform = [ waveform_cosine, waveform_sine], trigger = 0)
        self.set_deskew_matrix(0)
        self.set_monitor(average_on = 0) 
     
        self.awg_open()
        data_monitor = self.get_monitor(do_plot = 0) #monitor The displayed data is 
        
        input_1 = '/' + self.device + '/qas/0/monitor/inputs/0/wave'
        input_2 = '/' + self.device + '/qas/0/monitor/inputs/1/wave'
        data_raw = [[]]
        data_raw[0] = data_monitor[input_1]  
        data_raw.append( data_monitor[input_2])
        
        # 第一步测试deskew matrix
        deskew_matrix = self.set_deskew_matrix(30)  
        self.awg_open()
        data_monitor = self.get_monitor(do_plot = 0) #monitor 显示的数据是旋转后的
        data_deskew= [[]]
        data_deskew[0] = data_monitor[input_1]  
        data_deskew.append( data_monitor[input_2])
        
        # 第二步测试integration 的结果
        self.set_rotation(0, rotation = 1, input_mapping= 0 )
        self.set_result_path(source = 7 )# 7=读取integration, 2 = rotation后的数值
        self.awg_open()
        data_integration = self.get_result(do_plot = 0)
        data_integration_exp  = np.mean(data_integration['/' + self.device + '/qas/0/result/data/0/wave'])
        
        #第三步 测试rotation
        rotation = [1-0.3*1j,1+0.5*1j]
        self.set_rotation(0, rotation = rotation[0], input_mapping= 1 )
        self.set_rotation(1, rotation = rotation[1], input_mapping= 0 )
        self.set_result_path(source = 2 )# 7=读取integration, 2 = rotation后的数值
        self.awg_open()
        data_rotation = self.get_result(do_plot = 0)
        data_rotation_exp = [np.mean(data_rotation['/' + self.device + '/qas/0/result/data/0/wave']), np.mean(data_rotation['/' + self.device + '/qas/0/result/data/1/wave'])]

        #自己计算integration
        data_deskew_cal = np.dot( np.array(deskew_matrix), np.array(data_raw))
        data_deskew_array = np.array(data_deskew)
#        print(data_deskew_array.shape)
        data_integration_cal = (np.sum(   data_deskew_array[0][0:self.integration_length]*waveform_cosine)) + 1j*(np.sum(data_deskew_array[1][0:self.integration_length]*waveform_sine))
        
        #注意这是第二个解调器的结果
        chanel_2_rotation_cal =  np.real(data_integration_cal*rotation[1])
        
        data_integration_cal_1 = []
        # 注意这里有个input mapping 的切换 1->cos, 0->sine
        data_integration_cal_1.append(np.sum(   data_deskew_array[1][0:self.integration_length]*waveform_cosine))
        data_integration_cal_1.append(np.sum(data_deskew_array[0][0:self.integration_length]*waveform_sine))
        
        chanel_1_rotation_cal = np.real((data_integration_cal_1[0] + 1j*data_integration_cal_1[1])*rotation[0])
        data_rotation_cal = []
        data_rotation_cal.append(chanel_1_rotation_cal)
        data_rotation_cal.append(chanel_2_rotation_cal)


        
        if do_plot:
            plt.figure('deskew 线下与线上的对比')
            plt.plot(data_deskew[0],'.', data_deskew[1],'.')
            plt.plot(data_deskew_cal[0], 'r', data_deskew_cal[1],'g')
            result_path = '/' + self.device + '/qas/0/result/data/0/wave'

            plt.figure('I Q plot')
            plt.plot(np.real(data_integration[result_path]), np.imag(data_integration[result_path]),'.')

    
#        
#        
        return data_integration_exp, data_integration_cal, data_rotation_exp, data_rotation_cal
    
    def acquisition_poll(self, daq, paths, num_samples, timeout=10.0):
        """ Polls the UHFQA for data.
    
        Args:
            paths (list): list of subscribed paths
            num_samples (int): expected number of samples
            timeout (float): time in seconds before timeout Error is raised.
        """
        
        poll_length = 0.01  # s
        poll_timeout = 50  # ms
        poll_flags = 0
        poll_return_flat_dict = True
    
        # Keep list of recorded chunks of data for each subscribed path
        chunks = {p: [] for p in paths}
        gotem = {p: False for p in paths}
        print('polling results')

        # Poll data
        time = 0
        while time < timeout and not all(gotem.values()):
            dataset = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)
            for p in paths:
                if p not in dataset:
                    continue
                for v in dataset[p]:
                    chunks[p].append(v['vector'])
                    num_obtained = sum([len(x) for x in chunks[p]])
                    if num_obtained >= num_samples:
                        gotem[p] = True
            time += poll_length
    
        if not all(gotem.values()):
            for p in paths:
                num_obtained = sum([len(x) for x in chunks[p]])
                print('Path {}: Got {} of {} samples'.format(p, num_obtained, num_samples))
            raise Exception('Timeout Error: Did not get all results within {:.1f} s!'.format(timeout))
    
        # Return dict of flattened data
        return {p: np.concatenate(v) for p, v in chunks.items()}        
        
if __name__=='__main__':
     
#%%%%%%%%%%%%%%%%可以直接把波形给awg_builder, 它会构建一个sequence 程序 %%%%%%%%%%%%%%%%%
    device_id  = 'dev2534'
    qa=zurich_qa(device_id)

    qa.result_length = 100 #一共发送result_length个读取脉冲。10000为一组，
    
    fs = 1.8e9 # 采样率   
    ts = 0.5e-6 #读取脉冲时间长度/s
    read_length = (np.floor(ts*fs/8)*8).astype(np.int)  #.astype(np.int)将数据类型numpy.float64转为numpy.int32
    time_axis = np.linspace(0, read_length-1, read_length)/1.8e9
    qa.set_pulse_length(read_length)
    
    
     
    qa.update_qubit_frequency([10e6]) # 设置读取I_Q的频率
    #计算用于读取信号
    waveform_sine  = (np.sin(2*np.pi*time_axis*qa.qubit_frequency[0])) 
    waveform_cosine =(np.cos(2*np.pi*time_axis*qa.qubit_frequency[0]))
    qa.awg_builder(waveform = [ waveform_sine/3, waveform_cosine/3], trigger = 0)
    qa.set_result_path(source = 7 )# 7=读取integration, 2 = rotation后的数值
    qa.awg_open()
    test = qa.get_result(do_plot = 1)
    print(test)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#    data_integration_exp, data_integration_cal, data_rotation_exp, data_rotation_cal  = qa.demonstrate_processing(do_plot = 0)

 
#%%    
    qa.result_length = 1000 #一共发送result_length个读取脉冲。10000为一组，
    fre_scan = np.linspace(10e6, 600e6, 30, endpoint=True)
    amplitude_scan = np.logspace(0,-10,100,base=2)
    data_1 = []
    for amp in amplitude_scan:
        qa.set_relative_amplitude(amp)        
        data_1.append( np.abs(qa.spectroscopy_scan_frequency(2e-6,fre_scan )))
        
    plt.figure('spectroscpy_not standard')
 

    plt.contourf(fre_scan,amplitude_scan , np.array(data_1))
    plt.title('image') # 图像题目
 #    plt.show()


    


   
    