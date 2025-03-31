import RPi.GPIO as GPIO
import time
#Pin number, not gpio number
OUT = 36
S0 = 16
S1 = 18
S2 = 22
S3 = 32
NUM_CYCLES = 10
NUM_OF_SCANS = 5

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(OUT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(S2, GPIO.OUT)
    GPIO.setup(S3, GPIO.OUT)
    GPIO.setup(S0, GPIO.OUT)
    GPIO.setup(S1, GPIO.OUT)
    
    GPIO.output(S0, 0) # %2 mode for catching frequencies
    GPIO.output(S1, 1)    
        
def redScan():
    
    GPIO.output(S2, 0)
    GPIO.output(S3, 0)
    time.sleep(0.1)

    return meanFrequency()
    
def blueScan():
    
    GPIO.output(S2, 0)
    GPIO.output(S3, 1)
    time.sleep(0.1)
    return meanFrequency()


    
def greenScan():
    
    GPIO.output(S2, 1)
    GPIO.output(S3, 1)
    time.sleep(0.1)
    
    return meanFrequency()
    
    
def  frequencyGrab():
    
    GPIO.wait_for_edge(OUT, GPIO.RISING)
    start = time.time()
    for impulse_count in range(NUM_CYCLES):
        GPIO.wait_for_edge(OUT, GPIO.FALLING)
    duration = time.time() - start
    return (NUM_CYCLES/duration)

def meanFrequency():
    temp = 0
    for i in range(NUM_OF_SCANS):
        temp += frequencyGrab()
    return (temp / NUM_OF_SCANS)

def determineColor(red, green, blue):
    if (red > green) and (red > blue):
        print("it's red")
    elif (blue > green):
        print("it's blue")
    elif (green > blue):
        print("it's green")

def runsensor(mode):
    red = 0
    blue = 0
    green = 0
    
    if mode:
        #scan - black / white - black
        red = round(255 * ((redScan() - 40) / (106 - 40)))#- 
        green = round(255 * ((greenScan() - 40) / (108 - 40))) #- 1542
        blue = round(255 * ((blueScan() - 48) / (123 - 48))) #- 1910
        determineColor(red, green, blue)
    else:
        red = redScan() # w:  B: 
        green = greenScan() # w:  B: 
        blue = blueScan() #w:  B: 
    # print("r: ", red, "\n\n")
    print("r: ", red, "\ng: ", green, "\nb: ", blue, "\n\n")

print("Start")
tstart = time.time()
setup()

for i in range(100):
    runsensor(1) # mode 0 for uncalibrated, mode 1 for calibrated
    print(time.time() - tstart)
    tstart = time.time()
# print(time.time() - tstart)