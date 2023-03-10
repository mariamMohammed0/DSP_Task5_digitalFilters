import abc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import signal
import scipy


class Filters:
    # filter
    zeros=[]
    poles=[]
    uploaded_zeros=[]
    uploaded_poles=[]
    # signal
    uploaded_signal_x=[]
    uploaded_signal_y=[]
    input_signal=[]
    output_signal=[]
    # graph
    frequencies=[]
    magnitud_response=[]
    phase_response=np.zeros(512)
    allpass_response=np.zeros(512)
    total_phase_response=[]

    def __init__(self, zeros , poles):
            self.update_zerosAndPoles(zeros,poles)

    def change_to_complex(self,number):
        # number=data['zeros']
        counter=0      
        complexNumbers   = [0]*len(number)
        conjugateNumbers = [0]*len(number)

        for i in np.arange(0,len(number)):
            x = float(number[i]["X"])
            y = float(number[i]["Y"])
            complexNumbers[i] =complex( x+ y*1j)
            if number[i]['conjugate'] == True :
                conjugateNumbers[counter]= complexNumbers[i]
                counter+=1
        conjugateNumbers = [i for i in conjugateNumbers if i != 0]
        complexNumbers=complexNumbers+conjugateNumbers

        return complexNumbers

# /******************************************************** */
# /**********************SIGNAL**************************** */
# /******************************************************** */
    def applying_filter(self):
        # transfet function coefficients
        num_coeff,deno_coeff=scipy.signal.zpk2tf(self.zeros, self.poles, 1)
        # calc output signal
        y_n=[]
        if(len(self.input_signal)>max(len(num_coeff),len(deno_coeff))):

            y_n=[0]*(len(self.input_signal)-max(len(num_coeff),len(deno_coeff)))

            for j in  np.arange(0,len(self.input_signal)-max(len(num_coeff),len(deno_coeff))):
                y_n[j] = num_coeff[0]*self.input_signal[j]
                # past readings
                for m in np.arange(1,len(num_coeff)):
                    y_n[j] += num_coeff[m]*self.input_signal[j-m] 
                # past outputs
                
                for k in np.arange(1,len(deno_coeff)):
                    y_n[j] += - deno_coeff[k]*y_n[j-k]

                y_n[j]=np.abs(y_n[j])

        self.output_signal=   y_n  

        export_data1 = pd.DataFrame( {
                            'in':self.input_signal,})
        export_data2 =  pd.DataFrame({
                            'out':self.output_signal,})
        temp=pd.concat([export_data1, export_data2], axis=1)
        df = pd.DataFrame(temp)
        df.to_csv("static/assets/data/inputOutput.csv")   
            
    def upload_signal(self,filename):
        data = pd.read_csv(filename, delimiter= ',')
        self.uploaded_signal_x=data['time'].tolist()
        self.uploaded_signal_x=list(np.float_(self.uploaded_signal_x))
       
        self.uploaded_signal_y=data['amp'].tolist()
        self.input_signal=self.uploaded_signal_y

    def input_output_signals(self,input):
        self.input_signal=list(np.float_(input))
        self.applying_filter()

# /******************************************************** */
# /**********************FILTER**************************** */
# /******************************************************** */

    def update_zerosAndPoles(self,zeros,poles):
        self.zeros=zeros
        self.poles=poles
        self.update_graph()

    def update_graph (self):

        w, h = signal.freqz_zpk(self.zeros,self.poles, 1)
        self.frequencies =w
        self.magnitud_response=20 * np.log10(abs(h))
        self.phase_response=np.unwrap(np.angle(h))
        self.get_total_phase()
        self.save_phaseAndMag()

    def save_phaseAndMag(self):

        export_data1 = pd.DataFrame( {
                            'zeros':self.zeros,})
        export_data2 =  pd.DataFrame({
                            'poles':self.poles,})
        temp=pd.concat([export_data1, export_data2], axis=1)
        df = pd.DataFrame(temp)
        df.to_csv("static/assets/data/Zeros_poles.csv")

        ploting_data = {
            'frequency':self.frequencies,
            'mag':self.magnitud_response,
            'phase' :self.total_phase_response
                }
        df = pd.DataFrame(ploting_data)
        df.to_csv("static/assets/data/magAndPhase.csv")

    def upload_filter(self,filename): 
        data = pd.read_csv(filename, delimiter= ',')

        zeros     =data['zeros'].tolist()
        zeros_real=data['zeros'].tolist()
        zeros_img =data['zeros'].tolist()
        for index in np.arange(0,len(zeros)):
                zeros[index]=complex(zeros[index])
                zeros_real[index]=np.real(zeros[index])
                zeros_img[index]=np.imag(zeros[index])

        poles     =data['poles'].tolist()
        poles_real=data['poles'].tolist()
        poles_img =data['poles'].tolist()

        for index in np.arange(0,len(poles)):
                poles[index]=complex(poles[index])
                poles_real[index]=np.real(poles[index])
                poles_img[index]=np.imag(poles[index])

        self.uploaded_zeros=zeros
        self.uploaded_poles=poles

        # self.zeros=self.zeros+zeros
        # self.poles=self.zeros+poles
        self.update_graph()

        return zeros_real,zeros_img,poles_real,poles_img

# /********************************************************* */
# /**********************ALLPASS**************************** */
# /********************************************************* */

    def allpass_filter(self,coefficents):
        filter_angles = np.zeros(512)
        if not coefficents:
            coefficents=[complex(1)]
        for coeffient in coefficents:
            w, h =signal.freqz([-np.conj(coeffient), 1.0], [1.0, -coeffient])
            # print('z')
            angles = np.zeros(512) if coeffient==1 else np.unwrap(np.angle(h))
            filter_angles = np.add(filter_angles, angles)
            self.frequencies=w/max(w)
            self.allpass_response=filter_angles
            self.get_total_phase()

    def get_total_phase(self):
        self.total_phase_response=np.add(self.allpass_response,self.phase_response)


            

