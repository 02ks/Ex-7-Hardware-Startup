import os

from threading import Thread
from pidev.stepper import stepper
import spidev
import os
from time import sleep
spi = spidev.SpiDev()
from Slush.Devices import L6470Registers
import RPi.GPIO as GPIO
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
GAMER_SCREEN_NAME = 'gamer'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)

s0 = stepper(port=0, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                 steps_per_unit=200, speed=8)
s1 = stepper(port=1, micro_steps=32, hold_current=20, run_current=20, accel_current=20, deaccel_current=20,
                 steps_per_unit=200, speed=8)
s0.free_all()
s1.free_all()
global watch
watch = property(None)
global thing
thing = False
class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    global dir
    dir = 0
    global s0
    global on
    on = True
    global speed
    speed = 0
    def motor2(self):
        global dir
        global on

        if dir == 0:
            dir = 1
            if on == True:
                self.motor()
                self.motor()
        else:
            dir = 0
            if on == True:
                self.motor()
                self.motor()
    def motor(self):
        global on
        if on == True:
            s0.run(dir, speed)
            on = False
            print ('moving')
        else:
            s0.softStop()
            s0.free_all()
            on = True
            print('stopped')
    def spec(self):
        global thing
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        s0.set_speed(1)
        s0.relative_move(15)
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        sleep(10)
        s0.set_speed(5)
        s0.relative_move(10)
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        sleep(8)
        s0.goHome()
        sleep(30)
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        s0.set_speed(8)
        s0.relative_move(-100)
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        sleep(10)
        s0.goHome()
        
        self.watch.text = "Current Position: %d" % s0.get_position_in_units()
        thing = True
    def upspec(self):
        global thing
        if thing == False:
            Thread(target=self.spec).start()
        else:
            print("can't use this again")

    def move(self):
        if on == False:
            global speed
            speed = self.ids.slr.value
            self.motor()
            self.motor()
        else:
            speed = self.ids.slr.value

    def exit_program(self):
        s0.free_all()
        spi.close()
        GPIO.cleanup()
        quit()

    def page(self):
        SCREEN_MANAGER.current = GAMER_SCREEN_NAME

global xp
global spd
xp = 1
spd = 0.5
class GamerScreen(Screen):

    def __init__(self, **kwargs):
        super(GamerScreen, self).__init__(**kwargs)

    cyprus.initialize()
    cyprus.setup_servo(1)

    def startthread(self):
        Thread(target=self.run2).start()

    def exit_program(self):
        cyprus.set_servo_position(1, .5)
        cyprus.close()
        spi.close()
        GPIO.cleanup()
        quit()

    def run3(self):
        cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        global xp
        if xp == 1:
            cyprus.set_servo_position(1, .55)
            print('h')
            xp = 0
        else:
            cyprus.set_servo_position(1, .45)
            print('l')
            xp = 1

    def run1(self):
        global spd
        cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
        while spd < 1:
            cyprus.set_servo_position(1, spd)
            sleep(1)
            if spd < 1:
                spd = spd + 0.025
                print('%s' % spd)
            elif spd == 1:
               spd = 0.5
               print('done')

    def run2(self):
        while True:
            if (cyprus.read_gpio() & 0b0001)==1:
                sleep(0.1)
                if (cyprus.read_gpio() & 0b0001)==1:
                    print('a-')
                    cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                    cyprus.set_servo_position(1, .5)
            else:
                print('none')
                cyprus.set_pwm_values(1, period_value=100000, compare_value=50000, compare_mode=cyprus.LESS_THAN_OR_EQUAL)
                cyprus.set_servo_position(1, .55)

            sleep(1/200)

Builder.load_file('MainStartup.kv')
SCREEN_MANAGER.add_widget(GamerScreen(name=GAMER_SCREEN_NAME))
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))




def send_event(event_name):

    global MIXPANEL

    MIXPANEL.set_event_name(event_name)

    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()

cyprus.set_servo_position(1, .5)
cyprus.close()
s0.free_all()
spi.close()
GPIO.cleanup()