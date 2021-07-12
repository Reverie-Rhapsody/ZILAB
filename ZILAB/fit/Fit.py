# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 21:59:43 2020

@author: Rhapsody
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.optimize import curve_fit

class BaseFit(object):
    def __init__(self, data, **kw):
        self.data = data
    
    def func_fit(self, t, T1, A, B):
        """a example of T1 fit function""" 
        result = A*np.exp(-t/T1)+B
        return result
    
    def curve_fit(self, p0=None, **kw):
        t, y = self.data
        print(p0)
        p_est, p_cov = curve_fit(self.func_fit, t, y, p0)
        self.p_est = p_est
        self.p_cov = p_cov
        self._error = np.sqrt(np.diag(p_cov))
        
    # def func_err(self, T1, A, B, y, t):
    #     return y-self.function_fit_example(t, T1, A, B)
        
    # def lsq_fit(self, **kw):
    #     t, y = self.data
    #     c, ret_val = leastsq(self.func_err, [0.01, 0.01, 0.01], args=(y, t))
    
    
    def plot(self, fmt2='k--',
                   kw1={},
                   kw2={}, sort=None):
        plt.figure()
        ax = plt.gca()
        t,y=self.data
        scatter_kw={'marker':'o','color':'','edgecolors':'r'}
        scatter_kw.update(kw1)
        ax.scatter(t, y, **scatter_kw)
        plot_kw={}
        plot_kw.update(kw2)
        ax.plot(t, self.func_fit(t, *self.p_est), fmt2, **plot_kw)
        if sort=='ramsey':
            ax.set_xlabel('Time/us', fontsize=20)
            ax.set_ylabel('Vpp/V', fontsize=20)
            ax.set_title('Ramsey Fit', fontsize=20)
        elif sort=='rabi':
            ax.set_xlabel('Time/us', fontsize=20)
            ax.set_ylabel('Vpp/V', fontsize=20)
            ax.set_title('Rabi Fit', fontsize=20)
        elif sort=='T1':
            ax.set_xlabel('Time/us', fontsize=20)
            ax.set_ylabel('Vpp/V', fontsize=20)
            ax.set_title('T1 Fit', fontsize=20)
        elif sort=='spinecho':
            ax.set_xlabel('Time/us', fontsize=20)
            ax.set_ylabel('Vpp/V', fontsize=20)
            ax.set_title('Spin echo Fit', fontsize=20)
        elif sort=='picali_freq':
            ax.set_xlabel('Amplitude/Relative[0,1]', fontsize=20)
            ax.set_ylabel('Rabi Freq/MHz', fontsize=20)
            ax.set_title('Pi Calibration', fontsize=20)
        elif sort=='picali_leng':
            ax.set_xlabel('Amplitude/Relative[0,1]', fontsize=20)
            ax.set_ylabel('Pi Pulse Length/us', fontsize=20)
            ax.set_title('Pi Calibration', fontsize=20)
        elif sort=='cavity':
            ax.set_xlabel('Cavity Frequency/GHz', fontsize=20)
            ax.set_ylabel('dB', fontsize=20)
            ax.set_title('Cavity Fit', fontsize=20)
        else:
            pass
        
    @property
    def params(self):
        '''optimized parameters '''
        return self.p_est
      
    @property
    def error(self):
        '''standard deviation errors on the parameters '''
        return self._error


class Fit_Cavity(BaseFit):
    """Cavity Fit"""
    def func_fit(self,x,kc,km,x0,y0):
        """fit function of cavity"""
        result = y0+20*np.log10(np.abs(1-2*kc*1e6/((km+kc)*1e6+1j*(x-x0*1e9))))
        #result = y0+20*np.log10(np.abs(-1+2*kc*1e6/((km+kc)*1e6+1j*(x-x0)*1e9)))
        return result
        
    @property
    def fit_result(self):
        kc,km,x0,y0 = self.p_est
        return [kc,km,x0,y0]
    
    @property
    def Q_result(self):
        """计算Qi,Qe,QL值"""
        kc,km,x0,y0 = self.p_est
        x0 = x0*1e9
        Qi = x0/kc/1e6
        Qe = x0/km/1e6
        QL = Qi*Qe/(Qi+Qe)
        return [Qi, Qe, QL]
    
class Fit_Cavity_2(BaseFit):
    """Cavity Fit"""
    def func_fit(self,x,Q,Qe,x0,y0,phi):
        """fit function of cavity"""
        result =y0+20*np.log10(np.abs(1-(2*Q*np.abs(1/Qe)*np.exp(1j*phi*np.pi))/(1+2*1j*Q*(x-x0*1e9)/(x0*1e9))))
        return result
        
    @property
    def fit_result(self):
        Q,Qe,x0,y0,phi = self.p_est
        return [Q,Qe,x0,y0,phi]
    
    @property
    def Q_result(self):
        """计算Qi,Qe,QL值"""
        Q,Qe,x0,y0,phi = self.p_est
        x0 = x0*1e9
        Qe = np.real(Qe)
        QL = Q
        Qi = QL*Qe/(Qe-QL)
        return [Qi, Qe, QL]
    
class Fit_Rabi(BaseFit):
    """Rabi Fit"""
    
    def func_fit(self, t, A, B, C, lmda, Tr):
        """ fit function of rabi"""
        # lmda: lambda,rabi's wavelength
        result = A*np.exp(-t/Tr)*np.cos(2*np.pi/lmda*t+B)+C
        return result
    
    @property
    def Tr(self):
        A, B, C, lmda, Tr = self.p_est
        return Tr
    
    @property
    def rabi_freq(self):
        '''rabi frequency'''
        A, B, C, lmda, Tr = self.p_est
        # lambda 默认单位为us, 所以返回频率为MHz
        rabi_freq = np.abs(1/lmda)
        return rabi_freq
    
    @property
    def rabi_freq_error(self):
        '''rabi frequency error'''
        A, B, C, lmda, Tr = self.p_est
        A_err, B_err, C_err, lmda_err, Tr_err = self._error
        rabi_freq_err = np.abs(1/(lmda**2))*lmda_err
        return rabi_freq_err
    
    @property
    def PPlen(self):
        '''Pi Pulse Length, equal 1/2 lambda'''
        A, B, C, lmda, Tr = self.p_est
        _PPlen=np.abs(lmda/2)
        return _PPlen
    
    
class Fit_T1(BaseFit):
    """T1 Fit"""
    
    def func_fit(self, t, A, B, T1):
        """T1 fit function"""
        result = A*np.exp(-t/T1)+B
        return result
    
    @property
    def T1(self):
        A, B, T1 = self.p_est
        return T1
    
    @property
    def T1_error(self):
        A_err, B_err, T1_err = self._error
        return T1_err
    
class Fit_Ramsey(BaseFit):
    """Ramsey Fit"""
    def __init__(self, data, T1, **kw):
        self.T1 = T1
        self.data = data
        
    def func_fit(self, t, A , B, C, Tphi, Delta):
        """fit function of ramsey"""
        result = A*np.exp(-t/2/self.T1-np.square(t/Tphi))*np.cos(Delta*t+C)+B
        return result
    
    @property
    def Tphi(self):
        A, B, C, Tphi, Delta = self.p_est
        return Tphi
    
    @property
    def Tphi_error(self):
        A_err, B_err, C_err, Tphi_err, Delta_err = self._error
        return Tphi_err
    
    @property
    def detuning(self):
        A, B, C, Tphi, Delta = self.p_est
        return Delta/2/np.pi
    
    @property
    def T2(self):
        result = 2*np.abs(self.Tphi)*(self.T1)/(np.abs(self.Tphi)+2*(self.T1))
        return result
        
    
class Fit_Spinecho(BaseFit):
    """Fit spinecho"""
    def func_fit(self, t, A, B, T2E):
        """fit function of spinecho"""
        result = A*np.exp(-t/T2E)+B
        return result
    
    @property
    def T2E(self):
        A, B, T2E = self.p_est
        return T2E

    @property
    def T2E_error(self):
        A_err, B_err, T2E_err = self._error
        return T2E_err
    
class Fit_Pi_Freq(BaseFit):
    """Fit Pi Pulse calibration"""
    def func_fit(self, x, A, B, C, D):
        """fit function of Pi pulse calibration"""
        result = A*x+B*np.square(x)+C*pow(x,3)+D
        return result
    
    @property
    def fit_result(self):
        A, B, C, D = self.p_est
        return [A, B, C, D]
    
class Fit_Pi_Leng(BaseFit):
    """Fit Pi Pulse calibration"""
    def func_fit(self, x, A, B, C, D):
        """fit function of Pi pulse calibration"""
        result = 1/(A*x+B*np.square(x)+C*pow(x,3)+D)
        return result
    
    @property
    def fit_result(self):
        A, B, C, D = self.p_est
        return [A, B, C, D]
    
class Fit_RBM(BaseFit):
    '''Randomized Benchmarking Fit'''
    def __init__(self, data, d=2, **kw):
        '''d: d-dimensional system, for the Clifford group, d=2'''
        #super(RBM_Fit, self).__init__(data=data,**kw)
        self.d = d 
        self.data = data

    def func_fit(self,t,A,B,p):
        y=A*p**t+B
        return y

    @property
    def ppp(self):
        A,B,p=self.p_est
        return A,B,p

    @property
    def p_error(self):
        A_e,B_e,p_e=self._error
        return p_e

    @property
    def Fidelity(self):
        '''Fidelity '''
        d = self.d
        A,B,p=self.p_est
        F=1-(1-p)*(d-1)/d
        return F
    
    @property
    def F_error(self):
        d = self.d
        A_e,B_e,p_e=self._error
        F_e=p_e*(1-d)/d
        return F_e
    
    @property
    def Fidelity_gate(self):
        '''Fidelity '''
        d = self.d
        A,B,p=self.p_est
        F_gate=1-((1-p)*(d-1)/d)/1.875
        return F_gate
    
    @property
    def R_inco(self):
        d = self.d
        A,B,p=self.p_est
        r_inco=(1-np.sqrt(p))*(d-1)/d
        return r_inco
    
    @property
    def R_inco_gate(self):
        d = self.d
        A,B,p=self.p_est
        r_inco_gate=((1-np.sqrt(p))*(d-1)/d)/1.875
        return r_inco_gate
    