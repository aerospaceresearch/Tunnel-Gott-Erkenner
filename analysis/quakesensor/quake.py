import numpy as np
import matplotlib.pylab as plt
from scipy.io.wavfile import write

def generate_test_signal(filename, start, jitter):
    time = 10
    samplerate = 70
    data_size = [time * samplerate]


    x1 = np.random.randint(jitter, size=data_size)
    y1 = np.random.randint(jitter, size=data_size)
    z1 = np.random.randint(jitter, size=data_size)
    pps = np.ones(data_size)
    x2 = np.random.randint(jitter, size=data_size)
    y2 = np.random.randint(jitter, size=data_size)
    z2 = np.random.randint(jitter, size=data_size)

    header = ['x1', 'y1', 'z1', 'pps', 'x2', 'y2', 'z2']

    gps = []

    res = 30
    start_index = start
    for i in range(res):
        x1[start_index + i] += (np.sin((360/res * i * np.pi / 180.0))) *100
        y1[start_index + i] += (np.sin((360/res * i * np.pi / 180.0))) *100
        z1[start_index + i] += (np.sin((360/res * i * np.pi / 180.0))) *100

    data = [x1, y1, z1, pps, x2, y2, z2]

    np.save(filename, {'data': data, 'header': header, 'gps': gps})

    x = np.load(filename)
    #gps = dict(x.tolist())['gps']


def run(input3, filename):

    result = []
    result_index = []

    stepsize = 300
    signal_threshold = 100

    data3 = dict(input3.tolist())['data']

    #print(dict(input3.tolist())['header'])
    #print(data3)
    #print(data3[:, 0])

    # mean trick, but it needs to be corrected with real range of sensor
    sensor = 0
    x1 = data3[:, sensor + 0] - np.mean(data3[:, sensor + 0])
    y1 = data3[:, sensor + 1] - np.mean(data3[:, sensor + 1])
    z1 = data3[:, sensor + 2] - np.mean(data3[:, sensor + 2])

    signal3 = (x1**2 + y1**2 + z1**2)**0.5

    #plt.plot(signal3)
    #plt.show()

    #print(np.min(x1), np.max(x1), np.mean(x1))

    print(len(signal3))

    printing = 0

    for i in range(0, len(signal3), stepsize):
        signal_chunk = signal3[i: i+stepsize]

        min = np.min(signal_chunk)
        max = np.max(signal_chunk)
        mean = np.mean(signal_chunk)
        s = np.std(signal_chunk)
        #print(i, min, max, mean, s)
        for j in range(0, len(signal_chunk)):
            if signal_chunk[j] >= signal_threshold:
                result_index.append(i + j)
                result.append(signal_chunk[j])
                print(i + j, signal_chunk[j])
                printing = 1

    if printing == 1:
        plt.plot(signal3)
        plt.title("Detontation 2017-04-30 01:26 CEST")
        plt.xlabel("samples")
        plt.ylabel("amplitude [int]")
        plt.savefig(filename+ "_2.png")
        plt.clf()
        sound = []
        for i in range(len(signal3)):
            for j in range(12):
                sound.append(signal3[i])

        scaled = np.int16(sound/np.max(np.abs(sound)) * 32767)
        write(filename + '.wav', 20000, scaled)

        plt.plot(x1)
        plt.plot(y1)
        plt.plot(z1)
        plt.title("Detontation 2017-04-30 01:26 CEST")
        plt.xlabel("samples")
        plt.ylabel("amplitude [int]")
        plt.savefig(filename+ "_1.png")
        plt.clf()

import os
for root, dirs, files in os.walk("data", topdown=False):
    for name in files:
        print("reading in", os.path.join(root, name))
        run(np.load(os.path.join(root, name), encoding='latin1'), name)
    for name in dirs:
        print(os.path.join(root, name))

