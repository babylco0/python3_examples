import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import socket
import _thread
import http.client
from chuix import *
import _thread
import json
import socket
import time
import urllib
from os.path import join, exists

import kivy
from kivy.app import App
from kivy.base import Builder
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
from http.client import HTTPConnection

from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.pagelayout import PageLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from Crypto.PublicKey import RSA
from ChatScreen import *
from login import *
from ChatApp import *


__version__ = "2.0.0"

'''
class Chat2App(App):
    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.screen1 = ChatScreen(name='s1')
        self.screen2 = LoginScreen(name='s2')
        self.sm.add_widget(self.screen1)
        self.sm.add_widget(self.screen2)
        self.sm.current = 's2'
        return self.sm
'''


if __name__ == '__main__':
    ChatApp2().run()
