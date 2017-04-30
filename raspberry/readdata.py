import datetime
import time
import smbus
import Adafruit_ADS1x15
import numpy
import serial
import config


adc = Adafruit_ADS1x15.ADS1115()
bus = smbus.SMBus(1)

# MMA7455L address, 0x1D
if config.MMA7455L:
    bus.write_byte_data(0x1D, 0x16, 0x01)
if config.MPU6050:
    # Configure MPU-6050: Leave sleep mode and choose better clock
    bus.write_byte_data(0x68, 0x6b, 0x01)
    # Configure MPU-6050: Use sample-rate divider to drop duplicate samples
    bus.write_byte_data(0x68, 0x19, 0x07)

time.sleep(0.5)

start = datetime.datetime.now()
ndata = None
values = [0]*7
while True:
    # Read all the ADC channel values in a list.
    for i in range(4):
        values[i] = adc.read_adc(i, gain=1)

    # Read 6 bytes data back from 0x00
    try:
        data=bus.read_i2c_block_data(acc_i2c_id, 0x00, 6)
    except:
        data = [0] * 6

    if config.MMA7455L:
        # Convert the data to 10-bits
        xAcc = (data[1] & 0x03) * 256 + data [0]
        if xAcc > 511 :
            xAcc -= 1024
        values[4] = xAcc
        yAcc = (data[3] & 0x03) * 256 + data [2]
        if yAcc > 511 :
            yAcc -= 1024
        values[5] = yAcc
        zAcc = (data[5] & 0x03) * 256 + data [4]
        if zAcc > 511 :
            zAcc -= 1024
        values[6] = zAcc
    if config.MPU6050:
        # MPU6050: Read 6 bytes data back from 0x3b
        data=bus.read_i2c_block_data(0x68, 0x3b, 6)

        # Join the data to 16-bits 2-complement
        xAcc = data[0] * 256 + data [1]
        xAxx = xAcc - ((xAcc & 0x8000) << 1)
        values[4] = xAcc
        yAcc = data[2] * 256 + data [3]
        yAxx = yAcc - ((yAcc & 0x8000) << 1)
        values[5] = yAcc
        zAcc = data[4] * 256 + data [5]
        zAxx = zAcc - ((zAcc & 0x8000) << 1)
        values[6] = zAcc


    if ndata is None:
        ndata = numpy.array(values)
    else:
        ndata = numpy.vstack([ndata, values])
    if (datetime.datetime.now() - start).seconds > 120:
        data = []
        header = ['x', 'y', 'z', 'pps', 'x2', 'y2', 'z2']
        s = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)
        line = ""
        while True:
            line = s.readline()
            if line.startswith('$GPGGA'):
                break

        gps = line
        fn = int(time.mktime(start.timetuple()))
        numpy.save('/tmp/{fn}.npy'.format(fn=fn), {'data': ndata, 'header': header, 'gps': gps})
        ndata = None
        start = datetime.datetime.now()
