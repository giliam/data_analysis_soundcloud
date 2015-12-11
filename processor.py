#coding:utf8

from scipy.io import wavfile # get the api
from scipy.fftpack import fft
import numpy as np
import matplotlib.pyplot as plt
import math
import argparse
import os
import csv
import pyaudio
import wave

CHUNK_SIZE = 4096
fs = 44100
alpha = 0.99

features_order = ["tag", "title",
                  "mean_centroid", "std_centroid",
                  "mean_rolloff", "std_rolloff",
                  "mean_flux", "std_flux",
                  "mean_zerocrossings", "std_zerocrossings",
                  "low_energy",
                  "period0", "ratioperiod1", "ratioperiod2", "ratioperiod3",
                  "amp0", "amp1", "amp2", "amp3"]


filename = ""
tag = ""
output = ""
title=""
parser = argparse.ArgumentParser()
parser.add_argument('--filename', "-i", type=str)
parser.add_argument('--tag', "-t", type=str)
parser.add_argument('--out', "-o", type=str)
parser.add_argument('--title', "-u", type=str)
args = parser.parse_args()

if args.filename is not None:
    filename = args.filename
if args.tag is not None:
    tag = args.tag
if args.out is not None:
    output = args.out
if args.title is not None:
    title = args.title



def write_csv(features):
    global tag
    global output
    global features_order
    global filename
    with open(output, "a+") as csvfile:
        writer = csv.writer(csvfile, delimiter=",", quotechar='"')
        out = [features[name] for name in features_order]
        writer.writerow(out)
    print "\n\n\n\n"


def to_wav(file_path, wav_file_name):
    import pydub
    pydub.AudioSegment.converter = r"C:\\Users\\etienne\\Downloads\\ffmpeg-20151209-git-82f3d47-win64-static\\ffmpeg-20151209-git-82f3d47-win64-static\\bin\\ffmpeg.exe"
    print "converting {}".format(file_path)
    sound = pydub.AudioSegment.from_mp3(file_path)
    sound.export(wav_file_name, format="wav")

    
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


def compute_tempo(autocorrel,downsampling_factor):
    global fs
    return fs*60/(autocorrel*downsampling_factor)


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



def get_peaks(autocorrel, nb_peaks, lower_limit):
    idx = []
    amps = []
    for i in range(nb_peaks):
        m = autocorrel[lower_limit]
        tmp = lower_limit
        for j in range(lower_limit, len(autocorrel)):
            if autocorrel[j] > m:
                m = autocorrel[j]
                tmp = j
        autocorrel[tmp] = 0
        idx.append(tmp)
        amps.append(m)
    return idx, amps

def process(filename, output_file, music_title):
    k = 0
    global fs
    global alpha
    NB_WINDOWS = int(10/(float(CHUNK_SIZE)/fs)) # 10 seconds excerpt
    play(filename, NB_WINDOWS, CHUNK_SIZE)
    MAX_BPM = 200 # discard peaks for faster bpm in autocorrel
    downsampling_factor = 16
    fs, data = wavfile.read(filename)
    data = to_mono(data)

    k = len(data)/3/CHUNK_SIZE
    features = {"centroid" : [], "rolloff" : [], "flux" : [], "zerocrossings" : [],
    "lowenergy":[]}
    count_windows = 0
    hamming = get_hamming(CHUNK_SIZE)
    # get previous window for flow computation.
    prev_spectrum = normalize(abs(compute_fft(apply_window(pull_chunk(data, k-1), hamming))[0:CHUNK_SIZE/2]))
    energy_list = []
    b = True
    sig = []
    beat_histogram = [0]*MAX_BPM
    NB_ACCU_RYTHM = 131072/CHUNK_SIZE
    nb_rythm_count = 0
    rythmic_data = []
    while ((k+1)*CHUNK_SIZE < len(data) and count_windows < NB_WINDOWS):
        
        
        """ Extraction of spectral descriptors """
        chunk_before = pull_chunk(data, k)
        k+=1
        count_windows+=1
        chunk = apply_window(chunk_before, hamming)
        spectrum = compute_fft(chunk)
        spectrum = normalize(abs(spectrum[0:len(spectrum)/2]))
        energy_list.append(compute_energy(spectrum))
        sum_amp = 1
        cent = compute_centroid(spectrum, sum_amp)
        features["centroid"].append(cent)
        roll = compute_rolloff(spectrum, sum_amp)
        features["rolloff"].append(roll)
        flux = compute_flux(spectrum, prev_spectrum)
        features["flux"].append(flux)
        zc = compute_zerocrossings(chunk)
        m = np.mean(chunk)
        if count_windows < 100:
            sig_part = [c-m for c in chunk]
            sig.extend(sig_part)
        features["zerocrossings"].append(zc)
        prev_spectrum = spectrum
        
        """ Accumulation of rythmic data """
        if nb_rythm_count < NB_ACCU_RYTHM:
            rythmic_data.extend(chunk_before)
            nb_rythm_count+=1
        
    """ Extraction of rythmic descriptors """
    signal = fullwave_rectify(rythmic_data)
    signal = lowpass_filter(signal, alpha)
    signal = downsampling(signal, 32)
    signal = recenter(signal)
    
    autocorrel = autocorrelation(signal)
    lower_limit = int(60. * fs / (downsampling_factor*MAX_BPM))
    idxs, amps = get_peaks(autocorrel, 4, lower_limit)
    sum_amps = sum(amps)
    period0 = (60. * fs)/(idxs[0]*downsampling_factor) # bmp associated with the first peak
    amp0 = amps[0]/sum_amps
    period1 = (60. * fs)/(idxs[1]*downsampling_factor)
    ratio_period1 = period1/period0
    amp1 = amps[1]/sum_amps
    period2 = (60. * fs)/(idxs[2]*downsampling_factor)
    ratio_period2 = period2/period1
    amp2 = amps[2]/sum_amps
    period3 = (60. * fs)/(idxs[3]*downsampling_factor)
    ratio_period3 = period3/period2
    amp3 = amps[3]/sum_amps

    final_features={}
    final_features["period0"] = period0
    final_features["ratioperiod1"] = ratio_period1
    final_features["ratioperiod2"] = ratio_period2
    final_features["ratioperiod3"] = ratio_period3
    
    final_features["amp0"] = amp0
    final_features["amp1"] = amp1
    final_features["amp2"] = amp2
    final_features["amp3"] = amp3

    final_features["mean_centroid"] = np.mean(features["centroid"])
    final_features["std_centroid"] = np.std(features["centroid"])
    final_features["mean_rolloff"] = np.mean(features["rolloff"])
    final_features["std_rolloff"] = np.std(features["rolloff"])
    final_features["mean_flux"] = np.mean(features["flux"])
    final_features["std_flux"] = np.std(features["flux"])
    final_features["mean_zerocrossings"] = np.mean(features["zerocrossings"])
    final_features["std_zerocrossings"] = np.std(features["zerocrossings"])
    mean_energy = np.mean(energy_list)
    low_energy = float(sum([e < mean_energy for e in energy_list]))/len(energy_list)
    final_features["low_energy"] = low_energy
    final_features["title"] = music_title
    final_features["tag"] = tag
    # print final_features
    if output_file is not None:
        to_print = [str(final_features[t]) if t in final_features else '.' for t in features_order]
        output_file.write(csvlike(to_print))
    else:
        write_csv(final_features)


def play(filename, NB_WINDOWS, CHUNK_SIZE):
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
    
def csvlike(l):
    return '\t'.join(l) + '\n'

def print_titles(output_file):
    output_file.write(csvlike(features_order))


process(filename, None, title)

def main():
    current_path = os.path.dirname(os.path.realpath(__file__))
    input_path = os.path.join(current_path, 'input')
    output_file = open(os.path.join(current_path, 'output', 'output.csv'), 'w+')

    print_titles(output_file)
    for music_title in os.listdir(input_path):
        fn = os.path.join(input_path, music_title)
        if os.path.isfile(fn):
            if '.mp3' in fn:
                wav_file_name = fn.replace('.mp3', '.wav')
                if not os.path.isfile(wav_file_name):
                    to_wav(fn, wav_file_name)
                    process(wav_file_name, output_file, music_title)
            else:
                process(fn, output_file, music_title)

if __name__ == "__main__" and filename == "":
    main()
