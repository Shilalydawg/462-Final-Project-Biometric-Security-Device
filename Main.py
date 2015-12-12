#!/usr/bin/python
 
import RPi.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import *
from time import sleep, strftime
from datetime import datetime
import os
import FPS, sys 
import signal
import time
lcd = Adafruit_CharLCD()

lcd.begin(16, 1)
lcd_columns = 16
lcd_rows = 2

class keypad():
    def __init__(self, columnCount = 3):
        GPIO.setmode(GPIO.BCM)

        # CONSTANTS 
        if columnCount is 3:
            self.KEYPAD = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                ["*",0,"#"]
            ]

            self.ROW         = [4, 17, 27, 22]
            self.COLUMN      = [18, 23, 24]

        elif columnCount is 4:
            self.KEYPAD = [
                [1,2,3,"A"],
                [4,5,6,"B"],
                [7,8,9,"C"],
                ["*",0,"#","D"]
            ]

            self.ROW         = [18,23,24,25]
            self.COLUMN      = [4,17,22,21]
        else:
            return
     
    def getKey(self):
         
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        while rowVal < 0 or rowVal > 3:
            for i in range(len(self.ROW)):
                tmpRead = GPIO.input(self.ROW[i])
                if tmpRead == 0:
                    rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
         
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >2:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
def POWERFUNC(parg = None):
    if parg == 1:
        os.system("poweroff")
    elif parg == 2:
        os.system("reboot")
    else:
        lcd.clear()
        lcd.message("INVALID ENTRY")
        pass
         
def WelcomeMessage():       
        lcd.clear()
        lcd.message('Press 1 to\nVerify Identity')
        time.sleep(2.5)
        lcd.clear()
        lcd.message('Press 2 to\nEnroll Finger')
        time.sleep(2.5)
        lcd.clear()
        lcd.message('Press 3 to\nRemove Identity')
        time.sleep(2.5) 
        lcd.clear()
        lcd.message("Enter Choice...")
        
def UserStats(fps):
    UserCount = fps.GetEnrollCount()
    lcd.clear()
    lcd.message("Number of Users:\n%s"% str(UserCount))

def Verify(fps):
    lcd.clear() 
    lcd.message("Press Finger\nTo Verify")
    #Verify Test Function
    ID = -1
    print 'Press Finger to Scanner.'
    while not fps.IsPressFinger():
        FPS.delay(1)
    if fps.CaptureFinger(True):
        lcd.clear()
        lcd.message("Identifying..")
        FPS.delay(.5)
        ID = fps.Identify1_N()
        if ID < 200 and ID >= 0:
            print 'Welcome, User #%s'% str(ID)
            lcd.clear()
            lcd.message("Welcome,\nUser #%s"% str(ID))
        else:
            lcd.clear()
            lcd.message("Fingerprint\nnot found.")
            print 'Fingerprint not found. \n'
	
def Enroll(fps):
    lcd.clear()
    lcd.message("Finding open\nID Number.")
    enrollid=0
    okid=False
    iret = 5
    while not okid and enrollid < 200:
        okid = fps.CheckEnrolled(enrollid)
        if not okid:
            enrollid+=1
    if enrollid <200:
        lcd.clear()
        lcd.message("Press Finger\nTo Enroll")
        fps.EnrollStart(enrollid)
        while not fps.IsPressFinger():
            FPS.delay(1)
        if fps.CaptureFinger(True):
            lcd.clear()
            lcd.message("Enrolling 1..")
            FPS.delay(.5)
            iret = fps.Enroll1()
            lcd.clear()
            lcd.message("Remove Finger.")
            while fps.IsPressFinger():
                FPS.delay(1)
            lcd.clear()
            lcd.message("Press same\nfinger again.")
            while not fps.IsPressFinger():
                FPS.delay(1)
            if fps.CaptureFinger(True):
                FPS.delay(.5)
                lcd.clear()
                lcd.message("Enrolling 2..")
                iret = fps.Enroll2()
                lcd.clear()
                lcd.message("Remove Finger.")
                while fps.IsPressFinger():
                    FPS.delay(1)
                lcd.clear()
                lcd.message("Press same\nfinger again.")
                while not fps.IsPressFinger():
                    FPS.delay(1)
                if fps.CaptureFinger(True):
                    FPS.delay(.5)
                    lcd.clear()
                    lcd.message("Enrolling 3..")
                    iret = fps.Enroll3()
                    FPS.delay(1)
                    print '----------------------------> iret value: %s'% str(iret)
                    if iret == 0:
                        print 'Enrolling Successful'
                        print 'Stored as ID #%s'% str(enrollid)
                        lcd.clear()
                        lcd.message("Success!\nID #%s enrolled"% str(enrollid))
                        FPS.delay(3)
                    else:
                        print 'Enrolling Failed with error code: %s' % str(iret)
                        FPS.delay(1.5)
                else:
                    print 'Failed to capture third finger'
                    print 'Enrolling Failed with error code: %s' % str(iret)
                    lcd.clear()
                    lcd.message("Third Capture\nFailed")
                    FPS.delay(3)
            else:
                print 'Failed to capture second finger'
                print 'Enrolling Failed with error code: %s' % str(iret)
                lcd.clear()
                lcd.message("Second Capture\nFailed")
                FPS.delay(3)
        else:
            print 'Failed to capture first finger'
            print 'Enrolling Failed with error code: %s' % str(iret)
            lcd.clear()
            lcd.message("First Capture\nFailed")
            FPS.delay(3)
    else:
        print 'Failed: enroll storage is full'
        lcd.clear()
        lcd.message("Enroll Failed\nStorage Full")
        FPS.delay(3)
    if iret == 1:
        lcd.clear()
        lcd.message("Enroll Failed")
        FPS.delay(2)
    elif iret == 2:
        lcd.clear()
        lcd.message("Enroll Failed\nBad Finger")
        FPS.delay(2)
    elif iret == 3:
        lcd.clear()
        lcd.message("Enroll Failed\nPrint in Use")
        FPS.delay(2)
    else:
        pass
	
def Delete(fps):
    lcd.clear()
    lcd.message("Press Finger\nTo Remove")
    while not fps.IsPressFinger():
        FPS.delay(1)
    if fps.CaptureFinger(True):
        lcd.clear()
        lcd.message("Indentifying..")
        UserID = fps.Identify1_N()
    if UserID < 200 and UserID >= 0:
        FPS.delay(1)
        fps.DeleteID(UserID)
        lcd.clear()
        lcd.message("Identity #%s\nRemoved."% str(UserID))
        print 'Identity %s Removed.'% str(UserID)
    else:
        lcd.clear()
        lcd.message("Fingerprint\nnot found.")
def DeleteEverything(fps):
    lcd.clear()
    lcd.message("Wiping all Data.")
    FPS.delay(.5)
    fps.DeleteAll()
    lcd.clear()
    lcd.message("All Users' Data\nDeleted.")
    
    # Initialize the keypad class
def main():
    fps = FPS.FPS_GT511C3(device_name='/dev/ttyAMA0',baud=9600,timeout=2,is_com=False) #settings for raspberry pi GPIO
    fps.Open()
    kp = keypad()
    digit = None
        
    # Loop while waiting for a keypress
    WelcomeMessage()
    
    digit = kp.getKey()
        
    if digit == 1:
        if fps.SetLED(True):
            Verify(fps)
        FPS.delay(2)
    elif digit == 2:
        if fps.SetLED(True):
            Enroll(fps)
        FPS.delay(2)
    elif digit == 3:
        if fps.SetLED(True):
            Delete(fps)
        FPS.delay(2)
    elif digit == 4:
        UserStats(fps)
    elif digit == 0:
        lcd.clear()
        lcd.message("Don't just\npress buttons.")
        FPS.delay(.5)
        digit = kp.getKey()
        if digit == 8:
            lcd.clear()
            lcd.message("Seriously, stop\ndoing that.")
            FPS.delay(.5)
            digit = kp.getKey()
            if digit == 5:
                lcd.clear()
                lcd.message("I'm Serious! Not\none more button!")
                FPS.delay(.5)
                digit = kp.getKey()
                if digit == 2:
                    lcd.clear()
                    lcd.message("NO! That button\ndeletes all the-")
                    time.sleep(2)
                    DeleteEverything(fps)
        elif digit == 0:
            lcd.clear()
            lcd.message("~~~~~~~~~~~~~~~~")
            FPS.delay(.5)
            digit = kp.getKey()
            if digit == 0:
                lcd.clear()
                lcd.message("\n~~~~~~~~~~~~~~~~")
                FPS.delay(.5)
                digit = kp.getKey()
                if digit == 0:
                    lcd.clear()
                    lcd.message("POWER OPTIONS\nOFF=1 | RSET=2")
                    FPS.delay(.5)
                    digit = kp.getKey()
                    POWERFUNC(digit)
    else:
        lcd.clear()
        lcd.message("Invalid Input\nTry Again")
        time.sleep(1.5)
        
    print digit
    #return digit
    fps.SetLED(False)
    FPS.delay(1)
    fps.Close()

lcd.clear()
lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
lcd.message("Press * to Start")
keypay = keypad()
diggity = None
while diggity != '*':
        diggity = keypay.getKey()
while 1:
    main()
