import datetime
import time
import smbus
import Adafruit_ADS1x15
import numpy


adc = Adafruit_ADS1x15.ADS1115()
bus = smbus.SMBus(1)

# MMA7455L address, 0x1D
bus.write_byte_data(0x1D, 0x16, 0x01)

time.sleep(0.5)

# Print nice channel column headers.
#print('|  x1    |  y1    |  z1    |  x2    |  y2    |  z2    |')
#print('-' * 55)

start = datetime.datetime.now()
values = [0]*7
while True:
    # Read all the ADC channel values in a list.
    for i in range(4):
        values[i] = adc.read_adc(i, gain=1)

    # Read 6 bytes data back from 0x00
    data=bus.read_i2c_block_data(0x1D, 0x00, 6)

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

#    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} | {4:>6} | {5:>6} |'.format(*values))
    # maybe not fast enough
    data = numpy.vstack([data, values])
    if (datetime.datetime.now() - start).seconds > 120:
        data = []
        header = ['x', 'y', 'z', 'ppd', 'x2', 'y2', 'z2']
        gps = []
        fn = int(time.mktime(start.timetuple()))
        numpy.save('/tmp/{fn}.npy'.format(fn=fn), {'data': data, 'header': header, 'gps': gps})

