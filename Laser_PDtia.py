# Imports and Connections
import matplotlib.pyplot as plt
import numpy as np
import ITLA as itla
import time as time 
import pandas as pd
import serial

start = time.time()
# Configure serial connection
sercon=itla.ITLAConnect('COM4',9600)
ser = serial.Serial('COM5', 9600, timeout=1)  # Change COM port (Linux: '/dev/ttyUSB0')
time.sleep(2)  # Allow Arduino to reset

#Get Frequency array 
max_wav = 1556.5               # in nm
min_wav = 1555.5               # in nm
step    = 1                  # in GHz   
c = 299792458.0

min_frq = c/max_wav * 0.001
max_frq = c/min_wav * 0.001
flag = True 
freq = []
i = min_frq                  # in THz
while flag:
    freq.append(i)
    i = i + 0.025             
    if (i>max_frq): break

# The input to laser is in two parts - THz and GHz
fghz = []
fthz = []
for i in range (len(freq)):
    fghz.append(freq[i]%int(freq[i]) * 10000)
    fthz.append(int(freq[i]))


#Initial settings 
itla.ITLA(sercon, 0x31, 850, 1)                 # Set Power to 700dBm
itla.ITLA(sercon, 0x35, fthz[0], 1)             # Set frequency
itla.ITLA(sercon, 0x36, fghz[0], 1)         

print(f"Set Power = {itla.ITLA(sercon,0x31,0,0)}")
print(f"Set frequency = {itla.ITLA(sercon,0x35,0,0)} THz {itla.ITLA(sercon, 0x36,0,0)/10} GHz")

data = []  # To store readings
# #Check only 3 freqs 
rec_f = []
rec_oop = []

for i in range(len(freq)):
    itla.ITLA(sercon,0x32,0,1)                      #Laser off
    itla.ITLA(sercon, 0x35, fthz[i], 1)             # Set frequency
    itla.ITLA(sercon, 0x36, fghz[i], 1)             #Set frequency
    itla.ITLA(sercon,0x32,0x08,1)                   #Laser on
    time.sleep(25)
    print(f"Set frequency = {itla.ITLA(sercon,0x35,0,0)} THz {itla.ITLA(sercon, 0x36,0,0)/10} GHz")
    itla.ITLA(sercon,0x62,-12000,1) 
    frq = int(itla.ITLA(sercon,0x35,0,0)) + (itla.ITLA(sercon, 0x36,0,0)/10000)         #Set FTF to -12 Ghz
    # rec_f.append(itla.ITLA(sercon,0x62,0,0))                 
    time.sleep(20)
    k=0
    for j in range(-12000,12001,500):
        itla.ITLA(sercon,0x62,j,1)
        time.sleep(10)
        print(f"Set FTF = {itla.ITLA(sercon,0x62,0,0)}")
        rec_f.append(itla.ITLA(sercon,0x62,0,0))
        time2 = time.time()
        while True:
            time1 = time.time()
            input_pow=itla.ITLA(sercon,0x42,0,0)
            if input_pow > 840 and input_pow < 860:
                break
            if time1-time2 > 20:
                break
        for l in range(100):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line.isdigit():  # Ensure valid integer
                    value = int(line)*5.0/1023.0
                    timestamp = time.time()
                    data.append([timestamp, rec_f[k], value,freq ])
                    # print(f"{timestamp}, {value}")                                         
        rec_oop.append(itla.ITLA(sercon,0x42,0,0))
        k=k+1

# df = pd.DataFrame({"X": trace_x_values, "Y": trace_y_values, "Set F": rec_f, "OOP": rec_oop, "OSA Freq": osa_f, "OSA Power": osa_p})
# df.to_csv("Datafromloop1.csv", index=False)

#Turning off and diconnecting
itla.ITLA(sercon,0x32,0,1)                      
sercon.close()
ser.close()
stop = time.time()
print(f"Recorder Freq: \n {rec_f}")
print(f"Recorder OOP: \n{rec_oop}")
# columns=["Timestamp", "Recorded_Freq", "ADC_Value", "Frequency"]
df = pd.DataFrame(data)
df.to_csv("adc_readings_mrr_5pm3.csv", index=False)
print("Data saved to adc_readings_mrr_5pm3.csv")
print(f"Time Taken: {(stop - start)/60} mins ", )
