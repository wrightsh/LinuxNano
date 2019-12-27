#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time

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

try:
    output = subprocess.check_output(['halcmd', 'status'], universal_newlines=True)
except subprocess.CalledProcessError as e:
    output = e.output
print(output)
