# -*- coding: utf-8 -*-
from PyQt5 import QtSvg

class SVGWidget(QtSvg.QSvgWidget):
    def __init__(self, image):
        QtSvg.QSvgWidget.__init__(self, image)
