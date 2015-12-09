#coding:utf8

from scipy.io import wavfile # get the api
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
import math
import argparse

import pyaudio  
import wave 

CHUNK_SIZE = 4096
fs = 44100 
alpha = 0.99
filename = ""
parser = argparse.ArgumentParser()
parser.add_argument('--filename', "-i", type=str)
args = parser.parse_args()
if args.filename is not None:
	filename = args.filename



    
def to_mono(data):
    try:
        out = np.mean(data, axis=1)
        return out
    except IndexError:
        return data


def get_hamming(N):
    out = []
    for k in range(N):
        out.append(0.54 - 0.46*math.cos((2*math.pi*k)/N))
    return out
    
def apply_window(data, window):
    return [data[k]*window[k] for k in range(len(data))]

"""to be called after to_mono"""
def pull_chunk(data, k):
    return data[k*CHUNK_SIZE:(k+1)*CHUNK_SIZE]


def sum_amplitude(spectrum):
    return np.sum(spectrum)


def compute_fft(data):
    return fft(data)
    

def compute_centroid(spectrum, sum_amp):
    num = sum([spectrum[k]*k*float(fs)/CHUNK_SIZE for k in range(len(spectrum))])
    return num/sum_amp

def compute_rolloff(spectrum, sum_amp):
    tmp = 0.
    for k in range(len(spectrum)):
        tmp += spectrum[k]
        if tmp > 0.85*sum_amp:
            return k
    raise Exception("WTF")

def compute_flux(spectrum, prev_spectrum):
    return math.sqrt(np.sum([(i-j)**2 for i,j in zip(spectrum, prev_spectrum)]))

def compute_zerocrossings(chunk):
    nb_zero = 0
    m = np.mean(chunk)
    signs = np.sign([c-m for c in chunk])
    prev_sign = 0
    for k in signs:
        if k * prev_sign == -1:
            nb_zero += 1
        prev_sign = k
    return nb_zero
    

def compute_energy(spectrum):
    return sum([amp**2 for amp in spectrum])


def normalize(spectrum):
    s = float(np.sum(spectrum))
    return [x/s for x in spectrum]
    

def fullwave_rectify(signal):
    return map(abs, signal)

def lowpass_filter(signal, alpha):
    out = [signal[0]]
    for i in range(1, len(signal)):
        out.append(alpha*signal[i]-out[i-1]*(1-alpha))
    return out
    

def downsampling(signal, factor):
    out = []
    return [signal[k] for k in range(0, len(signal), factor)]


def recenter(signal):
    m = np.mean(signal)
    return [s-m for s in signal]

def autocorrelation(signal):
    N = len(signal)/2
    out = []
    for k in range(N):
        s = 0.
        for j in range(N):
            s += signal[k+j]*signal[j]
        out.append(s/N)
    return out

def process():
    k = 0
    global fs
    global filename
    global alpha
    NB_WINDOWS = int(10/(float(CHUNK_SIZE)/fs)) # 10 seconds excerpt
    play(NB_WINDOWS, CHUNK_SIZE)
    fs, data = wavfile.read(filename)
    data = to_mono(data)
    k = len(data)/3/CHUNK_SIZE
    features = {"centroid" : [], "rolloff" : [], "flux" : [], "zerocrossings" : [],
    "lowenergy":[]}
    count_windows = 0
    hamming = get_hamming(CHUNK_SIZE)
    prev_spectrum = normalize(abs(compute_fft(apply_window(pull_chunk(data, k-1), hamming))[0:CHUNK_SIZE/2]))
    energy_list = []
    b = True
    sig = []
    beat_histogram = [0]*300
    NB_ACCU_RYTHM = 131072/CHUNK_SIZE
    nb_rythm_count = 0
    rythmic_data = []
    while ((k+1)*CHUNK_SIZE < len(data) and count_windows < NB_WINDOWS):
        
        
        """ Extraction of spectral descriptors """
        chunk_before = pull_chunk(data, k)
        k+=1
        count_windows+=1
        #~ chunk = apply_window(chunk_before, hamming)
        #~ spectrum = compute_fft(chunk)
        #~ spectrum = normalize(abs(spectrum[0:len(spectrum)/2]))
        #~ energy_list.append(compute_energy(spectrum))
        #~ sum_amp = 1
        #~ cent = compute_centroid(spectrum, sum_amp)
        #~ features["centroid"].append(cent)
        #~ roll = compute_rolloff(spectrum, sum_amp)
        #~ features["rolloff"].append(roll)
        #~ flux = compute_flux(spectrum, prev_spectrum)
        #~ features["flux"].append(flux)
        #~ zc = compute_zerocrossings(chunk)
        #~ m = np.mean(chunk)
        #~ if count_windows < 100:
            #~ sig_part = [c-m for c in chunk]
            #~ sig.extend(sig_part)
        #~ features["zerocrossings"].append(zc)
        #~ prev_spectrum = spectrum
        
        """ Accumulation of rythmic data """
        if nb_rythm_count < NB_ACCU_RYTHM:
            rythmic_data.extend(chunk_before)
            nb_rythm_count+=1
        
    """ Extraction of rythmic descriptors """
    signal = fullwave_rectify(rythmic_data)
    signal = lowpass_filter(signal, alpha)
    signal = downsampling(signal, 32)
    signal = recenter(signal)
    print "autocorrelating"
    autocorrel = autocorrelation(signal)
    plt.plot(autocorrel)
    plt.show()
    print "mean_centroid", np.mean(features["centroid"])
    print "std_centroid", np.std(features["centroid"])
    print "mean_rolloff", np.mean(features["rolloff"])
    print "std_rolloff", np.std(features["rolloff"])
    print "mean_flux", np.mean(features["flux"])
    print "std_flux", np.std(features["flux"])
    print "mean_zerocrossings", np.mean(features["zerocrossings"])
    print "std_zerocrossings", np.std(features["zerocrossings"])
    mean_energy = np.mean(energy_list)
    low_energy = float(sum([e < mean_energy for e in energy_list]))/len(energy_list)
    print "low_energy", low_energy
    


def play(NB_WINDOWS, CHUNK_SIZE):
    #define stream chunk   
    chunk = CHUNK_SIZE  
    
    #open a wav format music  
    f = wave.open(filename,"rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data
    f.readframes(f.getnframes()/3)
    for k in range(NB_WINDOWS):
        data = f.readframes(chunk)  
        stream.write(data)  

    #stop stream  
    stream.stop_stream()  
    stream.close()  
    
    #close PyAudio  
    p.terminate()  
    
process()
