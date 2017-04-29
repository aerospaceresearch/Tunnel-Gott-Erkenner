import datetime
import time
import smbus
import Adafruit_ADS1x15
import numpy
import serial


adc = Adafruit_ADS1x15.ADS1115()
bus = smbus.SMBus(1)

# MMA7455L address, 0x1D
acc_i2c_id = 0x1D
bus.write_byte_data(acc_i2c_id, 0x16, 0x01)

time.sleep(0.5)

# Print nice channel column headers.
#print('|  x1    |  y1    |  z1    |  x2    |  y2    |  z2    |')
#print('-' * 55)

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
