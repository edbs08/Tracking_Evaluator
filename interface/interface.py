# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:17:02 2019

@author: Daniel
"""


from PyQt5.QtWidgets import *

def hello_world():
    app = QApplication([])
    label = QLabel('Hello World!')
    label.show()
    app.exec_()


def interface_main():
    print("Interface say : Hello World!")