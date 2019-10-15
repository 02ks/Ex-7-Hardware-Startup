import os

from threading import Thread
from pidev.stepper import stepper
import spidev
import os
from time import sleep
spi = spidev.SpiDev()
import RPi.GPIO as GPIO
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'


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
        elif on == False:
            s0.softStop()
            s0.free_all()
            on = True
            print('stopped')
        else:
            s0.run(dir, 1000)
            on = True
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
        if on == True:
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


Builder.load_file('MainStartup.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))




def send_event(event_name):

    global MIXPANEL

    MIXPANEL.set_event_name(event_name)

    MIXPANEL.send_event()


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    ProjectNameGUI().run()

s0.free_all()
spi.close()
GPIO.cleanup()