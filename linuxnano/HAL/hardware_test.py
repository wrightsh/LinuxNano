#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets


def halSetup():

    subprocess.call(['halcmd', 'stop'])
    subprocess.call(['halcmd', 'unload', 'all'])

    subprocess.call(['halcmd', 'loadusr', '-W', 'lcec_conf', 'ethercat_config.xml'])
    subprocess.call(['halcmd', 'loadrt', 'lcec'])

    subprocess.call(['halcmd', 'loadrt', 'threads', 'name1=servo', 'period1=1000000'])
    subprocess.call(['halcmd', 'addf', 'lcec.read-all', 'servo'])
    subprocess.call(['halcmd', 'addf', 'lcec.write-all', 'servo'])
    subprocess.call(['halcmd', 'start'])
    subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-3','True'])


    for i in range(0,5):
        subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-0','True'])
        subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-1','True'])
        subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-2','True'])
        subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-3','True'])
        time.sleep(1)
        subprocess.call(['halcmd', 'setp', 'lcec.0.3.dout-0','False'])
        time.sleep(1)



    subprocess.call(['halcmd', 'stop'])
    subprocess.call(['halcmd', 'unload', 'all'])


class Form(QDialog):
   def __init__(self, parent=None):
      super(Form, self).__init__(parent)

      layout = QVBoxLayout()
      self.b1 = QPushButton("Button1")
      self.b1.setCheckable(True)
      self.b1.toggle()
      self.b1.clicked.connect(lambda:self.whichbtn(self.b1))
      self.b1.clicked.connect(self.btnstate)
      layout.addWidget(self.b1)

      self.b2 = QPushButton()
      self.b2.setIcon(QIcon(QPixmap("python.gif")))
      self.b2.clicked.connect(lambda:self.whichbtn(self.b2))
      layout.addWidget(self.b2)
      self.setLayout(layout)
      self.b3 = QPushButton("Disabled")
      self.b3.setEnabled(False)
      layout.addWidget(self.b3)

      self.b4 = QPushButton("&Default")
      self.b4.setDefault(True)
      self.b4.clicked.connect(lambda:self.whichbtn(self.b4))
      layout.addWidget(self.b4)

      self.setWindowTitle("Button demo")

   def btnstate(self):
      if self.b1.isChecked():
         print "button pressed"
      else:
         print "button released"

   def whichbtn(self,b):
      print "clicked button is "+b.text()


def main():
    halSetup()

    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
   main()



try:
    output = subprocess.check_output(['halcmd', 'status'], universal_newlines=True)
except subprocess.CalledProcessError as e:
    output = e.output
print(output)
