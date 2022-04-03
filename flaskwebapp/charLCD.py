import time
import board
import digitalio

class charLCD(object):
    import time
    import board
    import digitalio
    import adafruit_character_lcd.character_lcd as characterlcd


    # Modify this if you have a different sized character LCD
    lcd_columns = 16
    lcd_rows = 2

    # Metro M0/M4 Pin Config:
    lcd_rs = digitalio.DigitalInOut(board.D22)
    lcd_en = digitalio.DigitalInOut(board.D17)
    lcd_d4 = digitalio.DigitalInOut(board.D25)
    lcd_d5 = digitalio.DigitalInOut(board.D24)
    lcd_d6 = digitalio.DigitalInOut(board.D23)
    lcd_d7 = digitalio.DigitalInOut(board.D18)
    lcd_backlight = digitalio.DigitalInOut(board.D12)

        # Initialise the LCD class
    lcd = characterlcd.Character_LCD_Mono(
        lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight
    )

    def __init__(self):
        return

    def setMessage(self,line1,line2):
        self.lcd.clear()
        if(len(line1)<16 and len(line2)<16):
            self.lcd.message = line1 + "\n" + line2
            self.lcd.backlight = False
        return

    def tempMessage(self,line1,line2,t):
        if(len(line1)<16 and len(line2)<16):
            self.lcd.message = line1 + "\n" + line2
            self.lcd.backlight = False
        time.sleep(t)
        self.lcd.clear()
        return

    def clearLCD(self):
        self.lcd.clear()
        return

    def clearLCDLeft(self):
        for i in range(len(18)):
            time.sleep(.2)
            self.lcd.move_left()
        self.lcd.clear()
        return
        

