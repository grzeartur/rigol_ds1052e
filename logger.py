import serial
import time
import threading
import msvcrt

shunt_resistance = 1.5  # ohm

iterations = 10000000
timeout_after_cmd = 0.1
read_interval = 1

crlf = b"\n"
beep_action = b":BEEP:ACT "
measure_Vaverage = b":MEAS:VAV? "
measure_src = b":MEAS:SOUR "
measure_src_which = b":MEAS:SOUR?"
chan1 = b"CHAN1"
chan2 = b"CHAN2"


print("Hello, logger started!")

exit_now = False

ser = serial.Serial(
    port='COM1',
    baudrate=9600)

def rs232_send(text):
    ser.write(text + crlf)
    time.sleep(timeout_after_cmd)

def rs232_receive_float():
    retv = ser.readline().decode().replace('\n', '')
    try:
        retv = float(retv)
    except:
        retv = 0
    return retv


rs232_send(beep_action) #  send duummy beep
rs232_send(beep_action) #  beep 

logfile=open("ds1052_log", 'a')
t_start = time.time()
total_ws = 0
total_as = 0
tab_columns_description = "chan1_val\tchan2_val\tcurrent_actual\titeration_ws\ttotal_ws\titeration_as\ttotal_as"
logfile.write(tab_columns_description + '\n')

for iteration in range(iterations):
    
    rs232_send(measure_Vaverage + chan1)
    chan1_val = rs232_receive_float()

    rs232_send(measure_Vaverage + chan2)
    chan2_val = rs232_receive_float()

    current_actual = chan2_val/shunt_resistance
    iteration_ws = chan1_val*current_actual
    iteration_as = current_actual
    total_ws += iteration_ws
    total_as += iteration_as

    data_line = str(chan1_val) + "\t" + str(chan2_val) + "\t" + str(current_actual) +\
                "\t" + str(iteration_ws) + "\t" + str(total_ws) + "\t" + str(iteration_as) + "\t" + str(total_as)
    print("iteration: " + str(iteration + 1))
    print("chan1 value: " + str(chan1_val) +  "\n" +\
          "chan2 value: " + str(chan2_val) +  "\n" +\
          "current actual: " + str(current_actual) +  "\n" +\
          "iteration Ws: " + str(iteration_ws) +  "\n" +\
          "iteration As: " + str(iteration_as) +  "\n" +\
          "total Wh: " + str(total_ws/3600) +  "\n" +\
          "total mAh: " + str(total_as/3.6))
    logfile.write(data_line + '\n')
    logfile.flush()

    total_time_used = time.time() - t_start
    time_used_in_this_iteration = total_time_used - iteration*read_interval
    print("time used in this iteration: " + str(time_used_in_this_iteration))
    print("time used in total: " + str(total_time_used) + "\n")
    time.sleep(read_interval - time_used_in_this_iteration)

    if msvcrt.kbhit():
        key = msvcrt.getch().decode()
        if key == 'q':
            print("you pressed \'" + key + "\' so I will quit")
            break
        

t_end = time.time()
elapsed_time = t_end - t_start
end_message = "Measurements took " + str(elapsed_time) + " seconds\ntotal mAh: " + str(total_as/3.6) + "\ntotal Wh: " + str(total_ws/3600)  
print(end_message)
logfile.write(end_message)
logfile.close()
ser.close()




    


