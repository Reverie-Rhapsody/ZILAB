# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:08:13 2020

@author: Rhapsody
"""

import zhinst.utils
import textwrap
import time
import math
import numpy as np
import matplotlib.pyplot as plt


class zurich_awg(object):
    """HDAWG"""
    def __init__(self, device_id, num_cores=1):
        #Initialize the HDAWG
        required_devtype = 'HDAWG'
        required_options = ['']
        try:
            self.daq, self.device, info = zhinst.utils.create_api_session(device_id, 6, required_devtype=required_devtype, required_options=required_options)
            zhinst.utils.disable_everything(self.daq, self.device) 
        
        except:
            print('没有连接，检查LabOne是否能发现仪器。')
            
        self.sampling_rate = 1.8e9  #采样率
        self.result_length = 100
        self.result_length_pulse = 100
        self.result_length_power = 6
        self.hdawg_sample_exponent = 0
        self.amplitude_drive_1 = 1.0
        self.amplitude_drive_2 = 1.0
        self.num_averages = 1 #2^N
        self.time_origin_sec = 1500e-9
        self.wave_width_sec = 500e-9  #Gauss波脉冲长度
        self.pulse_width_sec = 10e-9  #Gauss波标准差
        self.wave_width_poi = 96
        self.pulse_width_poi = 32
        self.range_drive = 0.4
        self.time_increment = 160
        self.osc_path = '/' + self.device +'/oscs/0/freq'
        self.osc_path_2 = '/' + self.device +'/oscs/1/freq'
        self.osc_path_5 = '/' + self.device +'/oscs/4/freq'
        self.awg_program = 'sequence'
        self.gate_size = 10
        self.gatesize_x = 10
        self.gatesize_y = 10
        self.gatesize_z = 10
        self.square_wave_sec_drive = 10e-6
        self.square_wave_sec_dc = 10e-6
        self.wave_sec = 160e-9
        self.d_increment = 0.05   #drag pulse amplitude increment step length
        self.num_cores = num_cores
        
        exp_setting = [
        ['/%s/sigouts/*/on'                % self.device, 1],
        ['/%s/sigouts/*/range'             % self.device, self.range_drive],
        ['/%s/awgs/0/time'                 % self.device, 0], # HDAWG sampling rate not reduced.
        ['/%s/awgs/0/userregs/0'           % self.device, 0],
        ['/%s/awgs/0/outputs/0/modulation/mode' % self.device, 1], # Output 1 modulated with Sine 1
        ['/%s/awgs/0/outputs/1/modulation/mode' % self.device, 2], # Output 2 modulated with Sine 2
        ['/%s/sines/0/phaseshift' % self.device, 0],  # Sine 1 phase
        ['/%s/sines/1/phaseshift' % self.device, 90], # Sine 2 phase
        ['/%s/sines/0/oscselect'  % self.device, 0],  # Select oscillator 1 for Sine 1
        ['/%s/sines/1/oscselect'  % self.device, 0],  # Select oscillator 1 for Sine 2
        ['/%s/sines/0/amplitudes/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/1/amplitudes/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/0/enables/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/1/enables/*' % self.device, 0], # Turn off CW signals
        ['/%s/awgs/*/single' % self.device, 0], #Set all the 4 awgs in rerun mode.
        ['/%s/awgs/0/auxtriggers/0/channel'% self.device, 0 ],#digtrigger 1； signal is trigger input 1
        ['/%s/awgs/0/auxtriggers/0/slope'% self.device, 1]# digtrigger 1： at rise edge
    ]
        
        exp_setting_2 = [
        ['/%s/sigouts/*/on'                % self.device, 1],
        ['/%s/sigouts/*/range'             % self.device, self.range_drive],
        ['/%s/awgs/1/time'                 % self.device, 0], # HDAWG sampling rate not reduced.
        ['/%s/awgs/1/userregs/0'           % self.device, 0],
        ['/%s/awgs/1/outputs/0/modulation/mode' % self.device, 1], # Output 1 modulated with Sine 1
        ['/%s/awgs/1/outputs/1/modulation/mode' % self.device, 2], # Output 2 modulated with Sine 2
        ['/%s/sines/2/phaseshift' % self.device, 0],  # Sine 1 phase
        ['/%s/sines/3/phaseshift' % self.device, 90], # Sine 2 phase
        ['/%s/sines/2/oscselect'  % self.device, 4],  # Select oscillator 1 for Sine 1
        ['/%s/sines/3/oscselect'  % self.device, 4],  # Select oscillator 1 for Sine 2
        ['/%s/sines/0/amplitudes/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/1/amplitudes/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/0/enables/*' % self.device, 0], # Turn off CW signals
        ['/%s/sines/1/enables/*' % self.device, 0], # Turn off CW signals
        ['/%s/awgs/*/single' % self.device, 0], #Set all the 4 awgs in rerun mode.
        ['/%s/awgs/0/auxtriggers/0/channel'% self.device, 0 ],#digtrigger 1； signal is trigger input 1
        ['/%s/awgs/0/auxtriggers/0/slope'% self.device, 1]# digtrigger 1： at rise edge
    ]
        
        self.daq.set(exp_setting)
        
        if self.num_cores==2:
            self.daq.set(exp_setting_2)
        
        self.daq.setInt('/{:s}/system/clocks/referenceclock/source'.format(self.device), 1)
        self.daq.setDouble('/{:s}/system/clocks/sampleclock/freq'.format(self.device), 1.8e+09)
        
    def awg_builder_flux(self):
        awg_program = textwrap.dedent("""\
        const f_base = _c0_;   // base sampling rate
        const f_s = f_base/pow(2,_c1_);
        const f_seq = f_base/8;
        const result_length = _c2_;
        const square_wave_sec_dc = _c3_;
        const time_origin_sec = _c4_;
        const amplitude_dc = _c5_;
        
        wave dc_pulse = ones(square_wave_sec_dc*f_s);
        
        repeat(result_length)
        {
            waitDigTrigger(1);
            //wait((time_origin_sec - square_wave_sec - 2e-6)*f_seq);
            wait((time_origin_sec - square_wave_sec_dc)*f_seq);
            playWave(1, amplitude_dc*dc_pulse);
            waitWave();
        }
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.sampling_rate))
        awg_program = awg_program.replace('_c1_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c2_', str(self.result_length))
        awg_program = awg_program.replace('_c3_', str(self.square_wave_sec_dc))
        awg_program = awg_program.replace('_c4_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c5_', str(self.amplitude_dc))
        
        self.awg_upload_string(awg_program, awg_index=1)
        
        
    def awg_builder_flux_2(self):
        awg_program = textwrap.dedent("""\
        const f_base = _c0_;   // base sampling rate
        const f_s = f_base/pow(2,_c1_);
        const f_seq = f_base/8;
        const result_length = _c2_;
        const square_wave_sec_dc = _c3_;
        const time_origin_sec = _c4_;
        const amplitude_dc = _c5_;
        
        wave dc_pulse = ones((square_wave_sec_dc+4e-6)*f_s);
        
        repeat(result_length)
        {
            waitDigTrigger(1);
            //wait((time_origin_sec - square_wave_sec - 2e-6)*f_seq);
            wait((time_origin_sec - square_wave_sec_dc)*f_seq);
            playWave(1, amplitude_dc*dc_pulse);
            waitWave();
        }
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.sampling_rate))
        awg_program = awg_program.replace('_c1_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c2_', str(self.result_length))
        awg_program = awg_program.replace('_c3_', str(self.square_wave_sec_dc))
        awg_program = awg_program.replace('_c4_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c5_', str(self.amplitude_dc))
        
        self.awg_upload_string(awg_program, awg_index=1)
    
    def awg_builder_flux_3(self):
        awg_program = textwrap.dedent("""\
        const f_base = _c0_;   // base sampling rate
        const f_s = f_base/pow(2,_c1_);
        const f_seq = f_base/8;
        const square_wave_sec_dc =2e-6;
        const time_origin_sec = 3e-6;
        const amplitude_dc = _c5_;
        
        wave dc_pulse = ones((square_wave_sec_dc+3e-6)*f_s);
        
        while(1)
        {
            waitDigTrigger(1);
            //wait((time_origin_sec - square_wave_sec - 2e-6)*f_seq);
            wait((time_origin_sec - square_wave_sec_dc)*f_seq);
            playWave(1, amplitude_dc*dc_pulse);
            waitWave();
        }
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.sampling_rate))
        awg_program = awg_program.replace('_c1_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c5_', str(self.amplitude_dc))
        
        self.awg_upload_string(awg_program, awg_index=1)
    
    def awg_builder_flux_4(self):
        awg_program = textwrap.dedent("""\
        const f_base = _c0_;   // base sampling rate
        const f_s = f_base/pow(2,_c1_);
        const f_seq = f_base/8;
        const square_wave_sec_dc =2e-6;
        const time_origin_sec = 3e-6;
        const amplitude_dc = _c5_;
        
        wave dc_pulse = ones((square_wave_sec_dc+3e-6)*f_s);
        
        while(1)
        {
            waitDigTrigger(1);
            //wait((time_origin_sec - square_wave_sec - 2e-6)*f_seq);
            wait((time_origin_sec - square_wave_sec_dc)*f_seq);
            playWave(2, amplitude_dc*dc_pulse);
            waitWave();
        }
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.sampling_rate))
        awg_program = awg_program.replace('_c1_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c5_', str(self.amplitude_dc))
        
        self.awg_upload_string(awg_program, awg_index=1)
    
    def awg_builder_rabi(self):
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c8_; // width of the Rabi pulse (sec)
    
        wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++) 
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - wave_width_sec)*f_seq);
            playWave(t/result_length*w_single_1, t/result_length*w_single_2);
            //playWave((0.01*t)*w_single_1, (0.01*t)*w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_rabi_t(self):
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        //const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const wave_width_sec_origin = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec_origin = _c9_; // width of the Rabi pulse (sec)
        //const pulse_width_sec = 300e-9;
        //cvar wave_width_sec = 5e-9;
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {   
            waitDigTrigger(1);
            const wave_width_sec = wave_width_sec_origin*(t+1);
            //const wave_width_sec = wave_width_sec_origin*(16/9)*(t+1);
            const pulse_width_sec = pulse_width_sec_origin*(t+1);
            wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
            wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
            wait((time_origin_sec - wave_width_sec)*f_seq-9);
            playWave(w_single_1, w_single_2);
            //playWave((0.01*t)*w_single_1, (0.01*t)*w_single_2);
            waitWave();
            //wait(0.225e8);
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
    
    
    def awg_builder_rabi_ttt(self):
        
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        //const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const wave_width_sec_origin = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec_origin = 1.0e-9; // width of the Rabi pulse (sec)
        //const pulse_width_sec = 300e-9;
        //cvar wave_width_sec = 5e-9;
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        repeat(result_length) 
        {  
            waitDigTrigger(1);
            const wave_width_sec = wave_width_sec_origin*(t+1);
            //const wave_width_sec = wave_width_sec_origin*(16/9)*(t+1);
            const pulse_width_sec = pulse_width_sec_origin*(t+1);
            wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
            wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
            wait((time_origin_sec - wave_width_sec)*f_seq);
            playWave(w_single_1, w_single_2);
            //playWave((0.01*t)*w_single_1, (0.01*t)*w_single_2);
            waitWave();
            t = t+1;
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_vacuum_rabi_drive(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c8_; //width of the Rabi Pulse (sec)
        wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);

        const square_width_step = _c9_; //step length of square wave (sec)
        
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        { 
            waitDigTrigger(1);
            const square_width_sec = square_width_step*(t+1);
            
            wait((time_origin_sec - wave_width_sec - square_width_sec - 30e-9)*f_seq);
            playWave(w_single_1, w_single_2);
            waitWave();
            //wait(0.225e8);
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pulse_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.square_wave_sec_dc))
        
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_vacuum_rabi_flux(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c8_; //width of the Rabi Pulse (sec)
        const square_width_step = _c9_; //step length of square wave (sec)
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {   
            waitDigTrigger(1);
            const square_width_sec = square_width_step*(t+1);
            wave w_square = 1.0*ones(square_width_sec*f_s);
            
            wait((time_origin_sec - square_width_sec)*f_seq);
            playWave(w_square);
            waitWave();
            //wait(0.225e8);
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pulse_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.square_wave_sec_dc))
        
        self.awg_upload_string(awg_program, awg_index=1)
    
    def awg_builder_spec(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
        const time_origin_sec = _c2_;
        const amplitude_drive = _c4_;
        
        //const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        //const pulse_width_sec = _c8_; // width of the Rabi pulse (sec)
        //wave w_single_1 = gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        //wave w_single_2 = gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        
        const square_wave_sec_drive = _c9_;
        wave w_single_1 = ones(square_wave_sec_drive*f_s);
        wave w_single_2 = ones(square_wave_sec_drive*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        repeat(result_length)
        {   
            waitDigTrigger(1);
            //wait((time_origin_sec - wave_width_sec)*f_seq);
            wait((time_origin_sec - square_wave_sec_drive)*f_seq);
            playWave(1,amplitude_drive*w_single_1, 2,amplitude_drive*w_single_2);     
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pulse_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.square_wave_sec_drive))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_spec_na(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        const square_wave_sec = _c9_;
        wave w_single_1 = ones(square_wave_sec*f_s);
        wave w_single_2 = ones(square_wave_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        playWave(1,drive_amplitude*w_single_1, 2,drive_amplitude*w_single_2);     
        waitWave();
        """)
    
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c9_', str(self.square_wave_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_T1(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c9_; // width of the Rabi pulse (sec)
    
        wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        const compensate_sec = 16e-9;
        //wave w_I = 'wave_I_test';
        //wave w_Q = 'wave_Q_test';
        //const wave_sec = 80e-9;
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - wave_width_sec - compensate_sec)*f_seq - t);
            //wait((time_origin_sec - wave_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);     
            //playWave(w_I, w_Q);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_drag_calibration(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const d_increment = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c9_; // width of the Rabi pulse (sec)
        const wave_width_poi = _c11_;
        const pulse_width_poi = _c12_;
        
    
        wave w_gauss = drive_amplitude*gauss(wave_width_poi, wave_width_poi/2, pulse_width_poi);
        wave w_drag = drag(wave_width_poi, wave_width_poi/2, pulse_width_poi)
        
        
        
        const compensate_sec = 16e-9;
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar d = 0;
        for(d = 0; d < result_length*d_increment; d=d+d_increment)
        {  
            assignWaveIndex(w_a, w_a, 0);
            waitDigTrigger(1);
            wait((time_origin_sec - wave_width_sec - compensate_sec)*f_seq);
            playWave(w_single_1, w_single_2);        
            //playWave(w_I, w_Q);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.d_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_test(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c8_; // width of the Rabi pulse (sec)
        //const gate_size = _c10_; // number of gates (not number of clifford gates)
        wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            
            waitDigTrigger(1);
            wait((time_origin_sec - 8.0*wave_width_sec)*f_seq-t-100-4-4+150);
            resetOscPhase();
            wait(100);
            setSinePhase(0,90);
            wait(2);
            setSinePhase(1,180);
            wait(2);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
            //incrementSinePhase(0,90);
            //wait(4);
            //incrementSinePhase(1,180);
            //wait(4);
            playWave(w_single_1, w_single_2);
            waitWave();
            //incrementSinePhase(0,270);
            //wait(4);
            //incrementSinePhase(0,180);
            wait(4);
            
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_test_CT(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,0);
        const f_seq = f_base/8; // sequencer clock rate
        
        const time_origin_sec = 2.88e-05;
        
        const drive_amplitude = 0.5;
        const wave_width_poi = 96;
        const pulse_width_poi = 32;
        const gate_size = 8; // number of gates (not number of clifford gates)
        wave w_a = drive_amplitude*gauss(wave_width_poi, wave_width_poi/2, pulse_width_poi);
        assignWaveIndex(w_a, w_a, 0);
        const time_increment = 1;
        const result_length = 100;
        
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {
        resetOscPhase();
        wait(100);
        waitDigTrigger(1);
        //wait((time_origin_sec - gate_size*wave_width_sec)*f_seq-gate_size*2-gate_size*4);
        wait(time_origin_sec*f_seq-gate_size*wave_width_poi/8-t-8*wave_width_poi/8);
        //playZero(time_origin_sec*f_s-gate_size*wave_width_poi-t*8);
        
        executeTableEntry(2);
        executeTableEntry(4);
        executeTableEntry(3);
        executeTableEntry(4);
        
        executeTableEntry(3);
        executeTableEntry(4);
        executeTableEntry(3);
        executeTableEntry(2);
        
        executeTableEntry(4);
        executeTableEntry(2);
        executeTableEntry(2);
        executeTableEntry(4);
        
        //executeTableEntry(4);
        //executeTableEntry(4);
        //executeTableEntry(4);
        //executeTableEntry(4);
        
        }
        """)
        self.awg_upload_string(awg_program)
        
    def awg_builder_T2(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // Width of the Rabi pulse (sec)
        const pulse_width_sec = _c9_; // Standard deviation of the Rabi Pi pulse (sec)
    
        wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - 2*wave_width_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);
            waitWave();
            wait(t);
            playWave(w_single_1, w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_spin_echo_1(self):
        """Spin Echo N=1"""
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const max_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // Width of the Pi Gauss pulse (sec)
        const pulse_width_sec = _c9_; // Standard deviation of Pi Gauss pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_3 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_4 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - 2*wave_width_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);
            waitWave();
            wait(t/2);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/2);
            playWave(w_single_1, w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_hdawg))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_spin_echo_2(self):
        """Spin Echo N=2"""
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const max_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // Width of the Pi Gauss pulse (sec)
        const pulse_width_sec = _c9_; // Standard deviation of Pi Gauss pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_3 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_4 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - 3*wave_width_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/2);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_1, w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_hdawg))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_spin_echo_4(self):
        """Spin Echo N=4"""
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const max_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // Width of the Pi Gauss pulse (sec)
        const pulse_width_sec = _c9_; // Standard deviation of Pi Gauss pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_3 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_4 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - 5*wave_width_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);
            waitWave();
            wait(t/8);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/8);
            playWave(w_single_1, w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_hdawg))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
    
    def awg_builder_spin_echo_8(self):
        """Spin Echo N=8"""
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const max_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // Width of the Pi Gauss pulse (sec)
        const pulse_width_sec = _c9_; // Standard deviation of Pi Gauss pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s/2, wave_width_sec*f_s/4, pulse_width_sec*f_s/2);
        wave w_single_3 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_4 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length*time_increment; t=t+time_increment)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - 5*wave_width_sec)*f_seq - t);
            playWave(w_single_1, w_single_2);
            waitWave();
            wait(t/8);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/4);
            playWave(w_single_3, w_single_4);
            waitWave();
            wait(t/8);
            playWave(w_single_1, w_single_2);
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_hdawg))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_picali(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length_pulse = _c0_;  // number of points
        const result_length_power = _c1_;
        const time_origin_sec = _c2_;
        const drive_amplitude = _c4_;
        const num_averages = _c6_;
        const wave_width_sec_origin = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec_origin = _c9_; // width of the Rabi pulse (sec)
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        cvar p = 1;
        for(p = 1; p<(result_length_power+1); p++)
        {
            for(t = 0; t < result_length_pulse; t++)
            {  
                waitDigTrigger(1);
                const wave_width_sec = wave_width_sec_origin*(t+1); 
                const pulse_width_sec = pulse_width_sec_origin*(t+1);
                wave w_single_1 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
                wave w_single_2 = drive_amplitude*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
                wait((time_origin_sec - wave_width_sec)*f_seq);
                playWave(p/result_length_power*w_single_1, p/result_length_power*w_single_2);
                //playWave((0.01*t)*w_single_1, (0.01*t)*w_single_2);
                waitWave();
                //wait(0.225e8);
            }
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length_pulse))
        awg_program = awg_program.replace('_c1_', str(self.result_length_power))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.num_averages))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_singleshot_zero(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const max_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c9_; // width of the Rabi pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec)*f_seq);
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_hdawg))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)    
    
    def awg_builder_singleshot_one(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
    
        const time_origin_sec = _c2_;
    
        const drive_amplitude = _c4_;
        const time_increment = _c6_;
        const wave_width_sec = _c7_; // width of the Rabi pulse (sec)
        const pulse_width_sec = _c9_; // width of the Rabi pulse (sec)
    
        wave w_single_1 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
        wave w_single_2 = _c8_*gauss(wave_width_sec*f_s, wave_width_sec*f_s/2, pulse_width_sec*f_s);
    
        // Beginning of the core sequencer program executed on the HDAWG at run time
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {  
            waitDigTrigger(1);
            wait((time_origin_sec - wave_width_sec)*f_seq);
            playWave(drive_amplitude*w_single_1, drive_amplitude*w_single_2);     
            waitWave();
        }
        """)
    
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c4_', str(self.amplitude_drive_2))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.time_increment))
        awg_program = awg_program.replace('_c7_', str(self.wave_width_sec))
        awg_program = awg_program.replace('_c8_', str(self.pi_amplitude))
        awg_program = awg_program.replace('_c9_', str(self.pulse_width_sec))
        
        self.awg_upload_string(awg_program)
        
    def awg_builder_rbm(self):
        awg_program = self.awg_program
        awg_program[0] = awg_program[0].replace('_c0_', str(self.result_length))
        awg_program[0] = awg_program[0].replace('_c2_', str(self.time_origin_sec))
        awg_program[0] = awg_program[0].replace('_c4_', str(self.amplitude_drive_2))
        awg_program[0] = awg_program[0].replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program[0] = awg_program[0].replace('_c6_', str(self.time_increment))
        awg_program[0] = awg_program[0].replace('_c7_', str(self.wave_width_sec))
        #awg_program[0] = awg_program[0].replace('_c8_', str(self.pi_amplitude))
        awg_program[0] = awg_program[0].replace('_c9_', str(self.pulse_width_sec))
        awg_program[0] = awg_program[0].replace('_c10_', str(self.gate_size))
        awg_program[0] = awg_program[0].replace('_c11_', str(self.wave_width_poi))
        awg_program[0] = awg_program[0].replace('_c12_', str(self.pulse_width_poi))
        
        awg_program = "\n".join([str(sequence) for sequence in awg_program])
        #print('----------')
        #print(awg_program)
        #print('----------')
        self.awg_upload_string(awg_program)
        
    def awg_builder_rbm_2(self):
        awg_program = self.awg_program
        awg_program[0] = awg_program[0].replace('_c0_', str(self.result_length))
        awg_program[0] = awg_program[0].replace('_c2_', str(self.time_origin_sec))
        awg_program[0] = awg_program[0].replace('_c4_', str(self.amplitude_drive_2))
        awg_program[0] = awg_program[0].replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program[0] = awg_program[0].replace('_c6_', str(self.time_increment))
        awg_program[0] = awg_program[0].replace('_c7_', str(self.wave_width_sec))
        #awg_program[0] = awg_program[0].replace('_c8_', str(self.pi_amplitude))
        awg_program[0] = awg_program[0].replace('_c9_', str(self.pulse_width_sec))
        awg_program[0] = awg_program[0].replace('_c10_', str(self.gate_size))
        awg_program[0] = awg_program[0].replace('_c11_', str(self.wave_width_poi))
        awg_program[0] = awg_program[0].replace('_c12_', str(self.pulse_width_poi))
        
        awg_program = "\n".join([str(sequence) for sequence in awg_program])
        #print('----------')
        #print(awg_program)
        #print('----------')
        self.awg_upload_string(awg_program, awg_index=1)
        
        
    def awg_builder_drag_cali(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        
        const result_length = _c0_;  // number of drag amplitude divisions
        const time_origin_sec = _c2_;
        
        const wave_width_poi = _c3_;
        const pulse_width_poi = _c4_;
        const drive_amplitude = _c6_;
        const gate_size = 2;
        
        wave w_gauss = drive_amplitude*gauss(wave_width_poi, wave_width_poi/2, pulse_width_poi);
        assignWaveIndex(w_gauss, w_gauss, 0);
            
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {
            resetOscPhase();
            wait(100);
            waitDigTrigger(1);
            wait(time_origin_sec*f_seq-gate_size*wave_width_poi/8);
            
            executeTableEntry(0);
            //executeTableEntry(1);
            //executeTableEntry(2);
        }                    
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.wave_width_poi))
        awg_program = awg_program.replace('_c4_', str(self.pulse_width_poi))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.amplitude_drive_2))
        
        self.awg_upload_string(awg_program)
        
        
    def awg_builder_drag_cali_2(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        
        const result_length = _c0_;  // number of drag amplitude divisions
        const time_origin_sec = _c2_;
        
        const wave_width_poi = _c3_;
        const pulse_width_poi = _c4_;
        const drive_amplitude = _c6_;
        const gate_size = 2;
        
        
        wave w_gauss = drive_amplitude*drag(wave_width_poi, wave_width_poi/2, pulse_width_poi);
        assignWaveIndex(w_gauss, w_gauss, 0);
        
        cvar t = 0;
        for(t = 0; t < result_length; t++)
        {
            resetOscPhase();
            wait(100);
            waitDigTrigger(1);
            wait(time_origin_sec*f_seq-gate_size*wave_width_poi/8);
            
            executeTableEntry(t);
            //executeTableEntry(t+result_length);
        }                    
        """)
        
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.wave_width_poi))
        awg_program = awg_program.replace('_c4_', str(self.pulse_width_poi))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        awg_program = awg_program.replace('_c6_', str(self.amplitude_drive_2))
        
        self.awg_upload_string(awg_program, awg_index=1)
    
        
    def awg_builder_playwave(self):
        awg_program = textwrap.dedent("""\
        const f_base = 1.8e9;   // base sampling rate
        const f_s = 1.8e9/pow(2,_c5_);
        const f_seq = f_base/8; // sequencer clock rate
        const result_length = _c0_;  // number of points
        const time_origin_sec = _c2_;
        const wave_sec = _c3_;
        const compensate_sec = 16e-9;
        
        wave w_I = 'wave_I_1';
        wave w_Q = 'wave_Q_1';
        
        //wave w_I = 'wave_I';
        //wave w_Q = 'wave_Q';
        
        while(1)
        {
            waitDigTrigger(1);
            wait((time_origin_sec - wave_sec-compensate_sec)*f_seq);
            playWave(w_I, w_Q);
            waitWave();
        }                    
        """)        
        awg_program = awg_program.replace('_c0_', str(self.result_length))
        awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
        awg_program = awg_program.replace('_c3_', str(self.wave_sec))
        awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
        
        self.awg_upload_string(awg_program)

    def awg_builder_playwave_total(self):
            awg_program = textwrap.dedent("""\
            const f_base = 1.8e9;   // base sampling rate
            const f_s = 1.8e9/pow(2,_c5_);
            const f_seq = f_base/8; // sequencer clock rate
            const result_length = _c0_;  // number of points
            const time_origin_sec = _c2_;
            const wave_sec = _c3_;
            const compensate_sec = 16e-9;
            
            wave w_I = 'wave_I_1';
            wave w_Q = 'wave_Q_1';
            
            //wave w_I = 'wave_I';
            //wave w_Q = 'wave_Q';
            
            while(1)
            {
                waitDigTrigger(1);
                wait((time_origin_sec - wave_sec-compensate_sec)*f_seq);
                playWave(w_I, w_Q);
                waitWave();
            }                    
            """)        
            awg_program = awg_program.replace('_c0_', str(self.result_length))
            awg_program = awg_program.replace('_c2_', str(self.time_origin_sec))
            awg_program = awg_program.replace('_c3_', str(self.wave_sec))
            awg_program = awg_program.replace('_c5_', str(self.hdawg_sample_exponent))
            
            self.awg_upload_string(awg_program)                      
    
    def awg_upload_string(self, awg_program, awg_index = 0):
        """写入波形并且编译"""
        awgModule = self.daq.awgModule()
        awgModule.set('awgModule/device', self.device)
        awgModule.set('awgModule/index', awg_index) #AWG 0, 1, 2, 3
        awgModule.execute()
        awgModule.set('awgModule/compiler/sourcestring', awg_program)
        while awgModule.getInt('awgModule/compiler/status')==-1:
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
       
    """    
    def awg_open(self, run=1):
        self.daq.setInt('/{:s}/sigouts/*/on'.format(self.device), run)
        self.daq.sync()
        while not(self.daq.getInt('/{:s}/awgs/0/ready'.format(self.device))):
            time.sleep(0.1)
        #self.daq.setInt('/{:s}/awgs/0/single'.format(self.device), 1) #temp
        self.daq.syncSetInt('/{:s}/awgs/0/enable'.format(self.device), run)#运行HDAWG, HDAWG 处于等待触发状态
        
    def awg_open_2(self, run=1):
        self.daq.setInt('/{:s}/sigouts/*/on'.format(self.device), run)
        self.daq.sync()
        while not(self.daq.getInt('/{:s}/awgs/1/ready'.format(self.device))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/1/enable'.format(self.device), run)#运行HDAWG, HDAWG 处于等待触发状态  
        
    def awg_open_12(self, run=1):
        self.daq.setInt('/{:s}/sigouts/*/on'.format(self.device), run)
        self.daq.sync()
        while not(self.daq.getInt('/{:s}/awgs/0/ready'.format(self.device))):
            time.sleep(0.1)
        while not(self.daq.getInt('/{:s}/awgs/1/ready'.format(self.device))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/0/enable'.format(self.device), run)#运行HDAWG, HDAWG 处于等待触发状态
        self.daq.syncSetInt('/{:s}/awgs/1/enable'.format(self.device), run)#运行HDAWG, HDAWG 处于等待触发状态
    """
    
    def channel_open(self, channel='*'):
        #choose the oriented channel to open, with channel='*' to open all the 8 channels
        self.daq.setInt('/{:s}/sigouts/{:s}/on'.format(self.device, str(channel)), 1)
        self.daq.sync()
        
    def channel_close(self, channel='*'):
         #choose the oriented channel to close, with channel='*' to close all the 8 channels
        self.daq.setInt('/{:s}/sigouts/{:s}/on'.format(self.device, str(channel)), 0)
        self.daq.sync()
        
    def awg_open(self, awgcore=0):
        #choose the oriented awg core to open
        #Make sure channels corresponding to the awg cores are opened at first
        while not(self.daq.getInt('/{:s}/awgs/{:s}/ready'.format(self.device, str(awgcore)))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/{:s}/enable'.format(self.device, str(awgcore)), 1)#运行HDAWG, HDAWG 处于等待触发状态
        
    def awg_close(self, awgcore=0):
        #choose the oriented awg core to close
        while not(self.daq.getInt('/{:s}/awgs/{:s}/ready'.format(self.device, str(awgcore)))):
            time.sleep(0.1)
        self.daq.syncSetInt('/{:s}/awgs/{:s}/enable'.format(self.device, str(awgcore)), 0)#运行HDAWG, HDAWG 处于等待触发状态
        
    """      
    def set_osc(self, freq=100e6):
        self.daq.setDouble(self.osc_path, freq)
        print('\n osc frequency:', self.daq.getDouble(self.osc_path),'\n')
      
    def set_osc_2(self, freq=100e6):
        self.daq.setDouble(self.osc_path_2, freq)
        print('\n osc frequency:', self.daq.getDouble(self.osc_path_2),'\n') 

    def set_osc_5(self, freq=100e6):
        self.daq.setDouble(self.osc_path_5, freq)
        print('\n osc frequency:', self.daq.getDouble(self.osc_path_5),'\n') 
    """
    
    def set_osc(self, osc_path=0, freq=100e6):
        #choose the oscillator path and set its frequency
        osc_path_full = '/{:s}/oscs/{:s}/freq'.format(self.device, str(osc_path))
        self.daq.setDouble(osc_path_full, freq)
        print('\n Oscillator frequency:  ', self.daq.getDouble(osc_path_full), 'Hz', '\n')
       
    def set_total_amplitude(self, awgcore=0, amplitude=1.0):
        #set the amplitude factor of the pulse, this setting takes effect for all the outputs under this awg core. 
        self.daq.setDouble('/{:s}/awgs/{:s}/outputs/*/amplitude'.format(self.device, str(awgcore)), amplitude)
        
    def set_total_amplitude_single(self, awgcore=0, channel=0, amplitude=1.0):
        #set the amplitude factor of the pulse, this setting takes effect for designated outputs under this awg core.
        self.daq.setDouble('/{:s}/awgs/{:s}/outputs/{:s}/amplitude'.format(self.device, str(awgcore), str(channel)), amplitude)
        
    """
    def set_relative_amplitude(self):
        #set the amplitude factor of the pulse
        self.daq.setDouble('/{:s}/awgs/0/outputs/*/amplitude'.format(self.device), self.amplitude_drive_1)
        
    def set_relative_amplitude_2(self):
        self.daq.setDouble('/{:s}/awgs/1/outputs/*/amplitude'.format(self.device), self.amplitude_drive_1)
    """
    
    def set_offset(self, channel=2, offset=0.0):
        self.daq.setDouble('/{:s}/sigouts/{:s}/offset'.format(self.device, str(channel)), offset)
    
    def direct_open(self, channel=2):
        self.daq.setDouble('/{:s}/sigouts/{:s}/direct'.format(self.device, str(channel)), 1)
        
    def direct_close(self, channel=2):
        self.daq.setDouble('/{:s}/sigouts/{:s}/direct'.format(self.device, str(channel)), 0)
    
    def set_output_range(self, channel=0, range=0.4):
        #set the output range (/V) of each output channel, with channel='*' to set all 8 output channels
        #range step is 200mV=0.2V, as example, if range=0.3, the actual effective setting is 0.4V
        self.daq.setDouble('/{:s}/sigouts/{:s}/range'.format(self.device, str(channel)), range)
        
    """
    def set_output_range(self):
        #set output range / V
        self.daq.setDouble('/{:s}/sigouts/*/range'.format(self.device), self.range_drive)
        
    def set_output_range_2(self):
        #set output range / V
        self.daq.setDouble('/{:s}/sigouts/2/range'.format(self.device), self.range_drive)
        self.daq.setDouble('/{:s}/sigouts/3/range'.format(self.device), self.range_drive)
    """
    
    def set_osc_control(self, state=0):
        """AWG Oscillator Control, rapid phase changes are available when the state is on--1"""
        self.daq.setInt('/{:s}/system/awg/oscillatorcontrol'.format(self.device), state)
    
    def modulation_open(self, awgcore=0):
        self.daq.setInt('/{:s}/awgs/{:s}/outputs/0/modulation/mode'.format(self.device, str(awgcore)), 1)
        self.daq.setInt('/{:s}/awgs/{:s}/outputs/1/modulation/mode'.format(self.device, str(awgcore)), 2)
        
    def modulation_close(self, awgcore=0):
        self.daq.setInt('/{:s}/awgs/{:s}/outputs/0/modulation/mode'.format(self.device, str(awgcore)), 0)
        self.daq.setInt('/{:s}/awgs/{:s}/outputs/1/modulation/mode'.format(self.device, str(awgcore)), 0)
    
    """
    def turnoff_modulation(self):
        self.daq.setInt('/{:s}/awgs/0/outputs/*/modulation/mode'.format(self.device), 0)
        
    def turnoff_modulation_2(self):
        self.daq.setInt('/{:s}/awgs/1/outputs/*/modulation/mode'.format(self.device), 0)
    
    def turnon_modulation(self):
        self.daq.setInt('/{:s}/awgs/0/outputs/0/modulation/mode'.format(self.device), 1)
        self.daq.setInt('/{:s}/awgs/0/outputs/1/modulation/mode'.format(self.device), 2)
    """
    
    def compile_status(self):
        """Read sequence compile status, set a time gap if compilation isn't finished."""
        awgModule = self.daq.awgModule()
        while awgModule.getInt("compiler/status") == -1:
            time.sleep(0.1)

        if awgModule.getInt("compiler/status") == 1:
            # compilation failed, raise an exception
            raise Exception(awgModule.getString("compiler/statusstring"))
    
        if awgModule.getInt("compiler/status") == 0:
            print(
                "Compilation successful with no warnings, will upload the program to the instrument."
            )
        if awgModule.getInt("compiler/status") == 2:
            print(
                "Compilation successful with warnings, will upload the program to the instrument."
            )
            print("Compiler warning: ", awgModule.getString("compiler/statusstring"))
        
        # Wait for the waveform upload to finish
        time.sleep(0.2)
        i = 0
        while (awgModule.getDouble("progress") < 1.0) and (
            awgModule.getInt("elf/status") != 1
        ):
            print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
            time.sleep(0.2)
            i += 1
        print(f"{i} progress: {awgModule.getDouble('progress'):.2f}")
        if awgModule.getInt("elf/status") == 0:
            print("Upload to the instrument successful.")
        if awgModule.getInt("elf/status") == 1:
            raise Exception("Upload to the instrument failed.")
    
    
    def upload_command_table(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 0,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value":90
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 1,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value": 180
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 2,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value": 90
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 3,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 180
                    }
                    "phase1"{
                        "value": 270
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 4,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value": 180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 5,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 270
                    }
                    "phase1"{
                        "value": 360
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/0/commandtable/data'.format(self.device), json_str)
          
        
    def upload_command_table_drag(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 0,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 1,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 180
                    }
                    "phase1"{
                        "value": 270
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 2,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value": 180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 3,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 270
                    }
                    "phase1"{
                        "value": 360
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 4,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 180
                    }
                    "phase1"{
                        "value": 270
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 5,
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 360
                    }
                    "phase1"{
                        "value": 450
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/1/commandtable/data'.format(self.device), json_str)
        
    def upload_command_table_2(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
            },
            "table": [
                {
                    "index": 0,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value": 90
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 1,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value": 180
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 2,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value": 90
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 3,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 180
                    }
                    "phase1"{
                        "value": 270
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 4,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value": 180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 5,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 270
                    }
                    "phase1"{
                        "value": 360
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/0/commandtable/data'.format(self.device), json_str)
        
    def upload_command_table_3(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 0,
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value":90
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 2
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.6
                    }
                    "amplitude1":{
                        "value": 0.6
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/0/commandtable/data'.format(self.device), json_str)
        
    def upload_command_table_4(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 2
                    "waveform": {
                        "index": 1
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.6
                    }
                    "amplitude1":{
                        "value": 0.6
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/1/commandtable/data'.format(self.device), json_str)
        
    def upload_command_table_drag_cali(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 0
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value":90
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 1
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 0
                    }
                    "phase1"{
                        "value":90
                    }
                    "amplitude0":{
                        "value": 1.0
                    }
                    "amplitude1":{
                        "value": 1.0
                    }
                },
                {
                    "index": 2
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 3
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 270
                    }
                    "phase1"{
                        "value":360
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/0/commandtable/data'.format(self.device), json_str)
        
    def upload_command_table_drag_cali_2(self):
        # Define JSON formatted string
        json_str = """
        {
            "$schema": "￼http://docs.zhinst.com/hdawg/commandtable/v2/schema",
            "header": {
                "version": "0.2"
                "partial": false
            },
            "table": [
                {
                    "index": 0
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.5*0.00
                    }
                    "amplitude1":{
                        "value": 0.5*0.00
                    }
                },
                {
                    "index": 0
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.5*0.05
                    }
                    "amplitude1":{
                        "value": 0.5*0.05
                    }
                },
                {
                    "index": 0
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                },
                {
                    "index": 0
                    "waveform": {
                        "index": 0
                    }
                    "phase0":{
                        "value": 90
                    }
                    "phase1"{
                        "value":180
                    }
                    "amplitude0":{
                        "value": 0.5
                    }
                    "amplitude1":{
                        "value": 0.5
                    }
                }
            ]
        }
        """
        # Upload command table
        self.daq.setVector('/{:s}/awgs/1/commandtable/data'.format(self.device), json_str)
        
    def json_sequence_generator(self, amplitude_list = [1, 1, 1, 1, 1], phase_list = [0, 30, 90, 30, 0]):
        json_head = """
         {
                  "$schema": "http://docs.zhinst.com/hdawg/commandtable/v2/schema",
                  "header": {
                    "version": "0.2",
                    "partial": false
                  },
                  "table": [       """
                            
                       
        json_body =   """   
        {
        "index": $index$,
        "waveform": {
            "index": 0
            }
        "phase0": {
            "value": $phase0$
            }
        "phase1": {
            "value": $phase1$
            }
        "amplitude0": {
            "value": $amplitude0$
            }
        "amplitude1": {
            "value":$amplitude0$
            }
        }"""
        
                            
        json_tail =  """
        ]}"""
                            
        json_body_multi = ''    
        
        length = len(amplitude_list)       
        for i in range(length):
            # tmp = json_body.replace('$index$', str(i)).replace('$amplitude0$', str((i+1)/length)).replace('$phase0$', str(i/length*360)).replace('$phase1$', str(i/length*360+90))  
            tmp = json_body.replace('$index$', str(i)).replace('$amplitude0$', str(amplitude_list[i])).replace('$phase0$', str(phase_list[i])).replace('$phase1$', str(phase_list[i]+90))  

            if i<(length-1):
                json_body_multi += tmp + ','
            else: 
                json_body_multi += tmp

        json_all = json_head + json_body_multi + json_tail
        
        json_str = textwrap.dedent(json_all)
        print(json_str)
        
        # Upload command table
        self.daq.setVector('/{:s}/awgs/1/commandtable/data'.format(self.device), json_str)
        
    
    def json_sequence_generator_2(self, amplitude_list = [1, 1, 1, 1, 1], amplitude_list_2 = [1, 1, 1, 1, 1], phase_list = [0, 30, 90, 30, 0], phase_list_2 = [0, 30, 90, 30, 0]):
        json_head = """
         {
                  "$schema": "http://docs.zhinst.com/hdawg/commandtable/v2/schema",
                  "header": {
                    "version": "0.2",
                    "partial": false
                  },
                  "table": [       """
                            
                       
        json_body =   """   
        {
        "index": $index$,
        "waveform": {
            "index": 0
            }
        "phase0": {
            "value": $phase0$
            }
        "phase1": {
            "value": $phase1$
            }
        "amplitude0": {
            "value": $amplitude0$
            }
        "amplitude1": {
            "value":$amplitude0$
            }
        }"""
        
                            
        json_tail =  """
        ]}"""
                            
        json_body_multi = ''    
        
        length = len(amplitude_list)    
        
        """第一个波形"""
        for i in range(length):
            # tmp = json_body.replace('$index$', str(i)).replace('$amplitude0$', str((i+1)/length)).replace('$phase0$', str(i/length*360)).replace('$phase1$', str(i/length*360+90))  
            tmp = json_body.replace('$index$', str(i)).replace('$amplitude0$', str(amplitude_list[i])).replace('$phase0$', str(phase_list[i])).replace('$phase1$', str(phase_list[i]+90))  

            if i<(length-1):
                json_body_multi += tmp + ','
            else: 
                json_body_multi += tmp
        
        """第二个波形"""
        json_body_multi += ','
        for i in range(length):
            # tmp = json_body.replace('$index$', str(i)).replace('$amplitude0$', str((i+1)/length)).replace('$phase0$', str(i/length*360)).replace('$phase1$', str(i/length*360+90))  
            tmp = json_body.replace('$index$', str(i+length)).replace('$amplitude0$', str(amplitude_list_2[i])).replace('$phase0$', str(phase_list_2[i])).replace('$phase1$', str(phase_list_2[i]+90))  

            if i<(length-1):
                json_body_multi += tmp + ','
            else: 
                json_body_multi += tmp

        json_all = json_head + json_body_multi + json_tail
        
        json_str = textwrap.dedent(json_all)
        print(json_str)
        
        # Upload command table
        self.daq.setVector('/{:s}/awgs/1/commandtable/data'.format(self.device), json_str)
        
        
        