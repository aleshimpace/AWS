
#=====================================================================================+
#                                                                                     |
# Simple example of reading the MCP3008 analog input channels, logg them and send     |
# them all to server.                                                                 |
# Author: Alesh Mahajan                                                               |
# License: Impace Systems                                                             |
#                                                                                     |
#=====================================================================================+

#=====================================================================================+
# Work flow of the system:
#   -Buzzer beeps for 2sec after every 10sec if GSM failed to connect
#   -Buzzer beeps for 0.5sec and goes off for some time if time set to
#       lynux is not working
#=====================================================================================+


import time
import threading
import FINALlog
import re
import serial
import datetime
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
# GPIO library and mode select
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

#Declarations
logInterval = 1 * 60       #[min * 60 seconds]
sendInterval = 2 * 60      #[min * 60 seconds]
buzzer_pin = 26                 #Indication buzzer check manual for debug
rainGuage_pin = 21               #Plug rainGuage in GPIO-02 and 3V3 of RaspberryPi

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

bfo = serial.Serial(
        port='/dev/ttyAMA0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

#--------------------------------------------------------------------------------------------------
#GPIO channel setup
GPIO.setup(buzzer_pin,GPIO.OUT)
GPIO.setup(rainGuage_pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)

#--------------------------------------------------------------------------------------------------


def _linux_set_time(time_tuple):
    import ctypes
    import ctypes.util
    import time

    # /usr/include/linux/time.h:
    #
    # define CLOCK_REALTIME                     0
    CLOCK_REALTIME = 0

    # /usr/include/time.h
    #
    # struct timespec
   #  {
    #    __time_t tv_sec;            /* Seconds.  */
    #    long int tv_nsec;           /* Nanoseconds.  */
    #  };
    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long),
                    ("tv_nsec", ctypes.c_long)]

    librt = ctypes.CDLL(ctypes.util.find_library("rt"))

    ts = timespec()
    ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
    ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

    # http://linux.die.net/man/3/clock_settime
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

#-------------------------------------------------------------------------------

def ADC():
    print('Reading MCP3008 values, press Ctrl-C to quit...')
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*8
        actual_parameter = [0]*8
        for i in range(8):
            # The read_adc function will get the value of the specified channel (0-7).
            values[i] = mcp.read_adc(i)
            a= switch(i, values[i])                  
            actual_parameter[i] = switch(i, values[i])
            
        # Print the ADC values.
        #FINALlog.writeLog('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
        FINALlog.writePara(',{0},{1},{2},{3},{4},{5},{6},{7}'.format(*actual_parameter))

        time.sleep(60)

#-------------------------------------------------------------------------------

def switch (channel, voltage):
    #return:
    if channel == 0:
        return map(voltage, 200, 1023, 0, 60.00)    #wind speed
    elif channel == 1:
        return map(voltage, 200, 1023, 0, 1800)     #solar radiation
    elif channel ==2:
        return map(voltage, 200, 1023, 0, 360)      #wind direction
    elif channel ==3:
        return map(voltage, 200, 1023, 0.00, 2.00)  #Ambiant pressure
    elif channel ==4:
        return map(voltage, 200, 1023, -40, 123.8)  #Ambiant Temprature
    elif channel ==5:
        return map(voltage, 200, 1023, 0, 100.00)   #Humidity
##    elif channel ==6:
##        return map(voltage, 588, 815, 0, 100.00)     #Leaf wetness L

##    elif channel ==6:
##        return round((voltage*0.43122)-255.1,2)
##    elif channel ==6:
##        print(voltage)
####        Rt=(((((voltage*5)/1023)/12.888)/2.060)*1000))
##        Rt=(voltage*0.1840)-5
##        print(Rt)
##        return map(Rt, 100.0, 138.50, 0, 100.00)
##    elif channel ==7:
##        return map(voltage, 95, 613, 0, 100.00)     #Leaf wetness H

    elif channel ==6:
        return map(voltage, 95, 613, 0, 100.00)     #Leaf wetness H
    elif channel ==7:
        return map(voltage, 95, 613, 0, 100.00)     #Leaf wetness L
    


#-------------------------------------------------------------------------------

def map(x,in_min,in_max,out_min,out_max):
    return round (float((x-in_min)*(out_max-out_min)/(in_max-in_min)+out_min),2)


#-------------------------------------------------------------------------------
def GSMinit():
    gsmInit = 0
    while True:
        if SIM808('AT'):
            if SIM808('AT+CREG?'):
                if SIM808('AT+CGATT?'):
                    if SIM808('AT+SAPBR=3,1,"Contype","GPRS"'):
                        if SIM808('AT+SAPBR=3,1,"APN","airtelgprs.com"'):           #Airtel
                        #if SIM808('AT+SAPBR=3,1,"APN","www"'):                     #Vodafone
                        #if SIM808('AT+SAPBR=3,1,"APN","TATA.DOCOMO.INTERNET"'):    #Tata docomo
                        #if SIM808('AT+SAPBR=3,1,"APN","imis"'):                    #Idea
                        #if SIM808('AT+SAPBR=3,1,"APN","bsnlnet"'):                 #BSNL
                            SIM808('AT+SAPBR=0,1')
                            if SIM808('AT+SAPBR=1,1'):
                                SIM808('AT+HTTPTERM')
                                if SIM808('AT+HTTPINIT'):
                                    print('GSM initialized')
                                    loc = atData('AT+CIPGSMLOC=1,1',1)
                                    print(loc)
                                    return loc
                                else:
                                    print('Failed to connect with internet')
                            else:
                                print('GSM network failure:5')
                        else:
                            print('GSM network failure:4')
                    else:
                        print('GSM network failure:3')
                else:
                    print('GSM network failure:2')
            else:
                print('GSM network failure:1')
        else:
            print('GSM connection failure')
        time.sleep(1)
        gsmInit += 1        #any command faliure causes increment in gsmInit
        
        if gsmInit == 10:   #if GSM fails to initelize more than 10 times return false to report problem
            return False

#-------------------------------------------------------------------------------


def SIM808(AT):
    attemptRead = 0
    print("at sent was: ",AT)
    bfo.write(AT + '\r')
    time.sleep(1)
    response = ''
    while attemptRead != 5:
        while bfo.inWaiting()!=0:
            response = bfo.readline()            
        if response == 'OK\r\n' and AT != 'AT+HTTPACTION=0':
            return True
        elif response != 'OK\r\n' or AT == 'AT+HTTPACTION=0':
            return response
        else:
            print(AT)
            attemptRead += 1
            print(attemptRead)
            if attemptRead == 10:
                return False
#-------------------------------------------------------------------------------

def connctionCheck():

    GSMreq = False
    connectionfail = 0

    while True:
        if GSMreq == False:
            gsmOK = SIM808('AT')

        if gsmOK == True:
            print('connection OK')
            return True

        else:
            connectionfail +=1
            if connectionfail == 20:
                print('Connection failed')
                return False

#-------------------------------------------------------------------------------
##
##def atData(atD, listElement):
##    flush = bfo.readline()
##    data = []
##    atDatafail = 0
##    print("at sent was: ",atD)
##    bfo.write(atD + '\r')
##    time.sleep(3)
##
##    if atD == 'AT+HTTPACTION=0':
##        count = 0
##        while bfo.inWaiting() != 0 or data[count].find('+HTTPACTION:')==-1:
##            data.append(bfo.readline())
##            print(data[count].find('+HTTPACTION:'))
##            count=+1
##    else:
##        while bfo.inWaiting() != 0:
##            data.append(bfo.readline())
##            print(data)
##
##    if len(data)>2 and atD != 'AT+HTTPACTION=0':
##        flush = bfo.readline()
##        return data[listElement]
##    elif len(data)>3 and atD == 'AT+HTTPACTION=0':
##        flush = bfo.readline()
##        return data[listElement]
##    else:
##        return 'ERROR1'



def atData(atD, listElement):
    flush = bfo.readline()
    #while True:
    data = []
    atDatafail = 0
    bfo.write(atD + '\r')
    time.sleep(3)
    while bfo.inWaiting() != 0:
        data.append(bfo.readline())
        #print(data)
    if len(data)>2:
        #print (data)
        flush = bfo.readline()
        return data[listElement]
    else:
        #atDatafail +=1
        #if atDatafail == 2:
        return 'ERROR1'


#-------------------------------------------------------------------------------

def tipping_bucket(pin):
    FINALlog.tipBucket()


#-------------------------------------------------------------------------------

def sendData_rain():
    while True:

        lines_R = []
        upNo_R = []

        with open ('/home/pi/zAWS/tipping_bucket.log', 'rt') as data_file_R:  # Open file lorem.txt for reading of text data.
            for dataline_R in data_file_R:                                  # For each line of text, store it in a string variable named "line", and
                lines_R.append(dataline_R)
        with open ('/home/pi/zAWS/UPLOADcount_rain.log', 'rt') as up_file_R: # Open file lorem.txt for reading of text data.
            for upline_R in up_file_R:                                      # For each line of text, store it in a string variable named "line", and
                upNo_R.append(upline_R)

        data_collected_R = len(lines_R)  #lengthPumpdata
        data_uploaded_R = len(upNo_R)    #lengthUpdata
        dataCollect_R = data_collected_R - data_uploaded_R

        if dataCollect_R > 0:

            DATA_R = []
            DATA_R = re.split('[ |,\n-!?"+]', lines[data_uploaded_R])

            if len(DATA_R) > 4:

                rain=DATA_R[0]+'%20'+DATA_R[1]
                
                if SIM808('AT+HTTPPARA="URL","http://219.91.255.134:5353/AWSWebService.asmx/setRainGaugeDetails?TippingTime='+rain+'"'):

                    time.sleep(1)
                    actionR = atData('AT+HTTPACTION=0',3)
                    split_actionR = []
                    split_actionR = actionR.split(',')

                    if len(split_actionR)>1:

                        if split_actionR[1] == '200':

                            FINALlog.writeUpcount_Rain()
                            print('data upload No:')
                            print(data_uploaded_R)
                            #data_uploaded_R += 1

                        else:
                            print('Response other than "200"')

                    else:
                        print('HTTP action response error')

                else:
                    #data_uploaded_R += 1
                    FINALlog.writeUpcount_Rain()
                    #print('Upload count:')
                    #print(data_uploaded_R)
                    print('Data loss or garbage string, moving on to next sample')
            else:
                #data_uploaded_R += 1
                FINALlog.writeUpcount_Rain()
                #print('Upload count:')
                #print(data_uploaded_R)
                print('Data loss or garbage string, moving on to next sample')
        else:
            break
            
            #print(time.time()-start2)
            #time.sleep(sendInterval-(time.time()-start3))

    #--------------------------------------------------------------------------------

def sendData():
    uploadFails = 0
    while True:
        if uploadFails > 9:
            GSMinit()
            uploadFails =  0
        else:
            lines = []
            upNo = []
            with open ('/home/pi/zAWS/Parameters.csv', 'rt') as data_file:  # Open file lorem.txt for reading of text data.
                for dataline in data_file:                                  # For each line of text, store it in a string variable named "line", and
                    lines.append(dataline)
            with open ('/home/pi/zAWS/UPLOADcount.log', 'rt') as up_file: # Open file lorem.txt for reading of text data.
                for upline in up_file:                                       # For each line of text, store it in a string variable named "line", and
                    upNo.append(upline)
            data_collected = len(lines)  #lengthPumpdata
            data_uploaded = len(upNo)    #lengthUpdata
            dataCollect = data_collected - data_uploaded

            if dataCollect > 0:
                DATA = []
                DATA=re.split('[ |,\n!?"+]', lines[data_uploaded])

                if len(DATA) > 11:
                    if SIM808('AT+HTTPPARA="CID",1'):
                        windSpeed=DATA[3]
                        solarRad=DATA[4]
                        windDir=DATA[5]
                        ambiantPressure=DATA[6]
                        temprature=DATA[7]
                        humidity=DATA[8]
                        leafWetL=DATA[9]
                        leafWetH=DATA[10]
                        soilTemp='121'
                        TimeStamp=DATA[0]+'%20'+DATA[1]
                        if SIM808('AT+HTTPPARA="URL","http://219.91.255.134:5353/AWSWebService.asmx/SaveAWSDetails?Wind_Speed='+windSpeed+'&Solar_Radiation='+solarRad+'&Wind_Direction='+windDir+'&Ambient_Pressure='+ambiantPressure+'&Air_Temperature='+temprature+'&Relative_Humidity='+humidity+'&Leaf_Wetness_L='+leafWetL+'&Leaf_Wetness_H='+leafWetH+'&Soil_Temperature=35&TimeStamp='+TimeStamp+'"'):

                            time.sleep(1)
                            actionP = atData('AT+HTTPACTION=0',3)
                            print(actionP)
                            split_actionP = []
                            split_actionP = actionP.split(',')

                            if len(split_actionP)>1:

                                if split_actionP[1] == '200':

                                    FINALlog.writeUpcount()
                                    print('data upload No:')
                                    print(data_uploaded)

                                    #data_uploaded += 1

                                else:
##                                    uploadFails += 1
                                    time.sleep(1)

                                    #data_uploaded += 1
                                    #FINALlog.writeUpcount()
                                    print('Upload failed')

                            else:
                                time.sleep(1)
                                print('Upload failed due error in HTTPACTION reply')
                        else:
                            time.sleep(1)
                    else:
                        time.sleep(1)
                else:
                        #data_uploaded += 1
                    FINALlog.writeUpcount()
                        #print('Upload count:')
                        #print(data_uploaded)
                    print('Data loss or garbage string, moving on to next sample')
            
            else:
                break

                #print(time.time()-start2)
                #time.sleep(sendInterval-(time.time()-start2))


#--------------------------------------------------------------------------------

def execution():
    GPIO.add_event_detect(rainGuage_pin, GPIO.FALLING, tipping_bucket)
    while True:
        time.sleep(1)
        start2= time.time()
        #print(start2)
        sendData()
        sendData_rain()
        #print(sendInterval)
        start=sendInterval-(time.time()-start2)
        print(start)
        time.sleep(start)

#--------------------------------------------------------------------------------
def Main():
    print('Main:')
##    GSMinit()
    t1 = threading.Thread(target=ADC)
    t1.start()
    t2 = threading.Thread(target=execution)
    t2.start()

if __name__=='__main__':
##    FINALlog.createLOGs()
##    Main()
    if connctionCheck():
        while True:
            
            RTCtime = GSMinit()        #atData('AT+CCLK?', 1)
            if RTCtime != 'ERROR1':
                split_RTC = re.split('[, /\-!?:"+]', RTCtime)
                print(split_RTC)
                split_RTC[10]=int(split_RTC[10])+30
                if (split_RTC[10]>60):
                    split_RTC[10]=split_RTC[10]-60
                    split_RTC[9]=int(split_RTC[9])+6
                else:
                    split_RTC[9]=int(split_RTC[9])+5
                print(split_RTC)
                time_tuple = ( int(split_RTC[6]), int(split_RTC[7]), int(split_RTC[8]), split_RTC[9], split_RTC[10], 0, 0)
                _linux_set_time(time_tuple)
                time.sleep(1)
                FINALlog.createLOGs()
                Main()
                break
            elif RTCtime == 'ERROR1':
                print('RTC error')
                GPIO.output(buzzer_pin,True)
                time.sleep(1)
                GPIO.output(buzzer_pin,False)
            else:
                time.sleep(1)
    else:
        while True:
            GPIO.output(buzzer_pin,True)
            time.sleep(2)
            GPIO.output(buzzer_pin,False)
            time.sleep(10)
