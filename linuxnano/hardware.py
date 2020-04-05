
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import time
import select

from threading import Thread
from queue import Queue, Empty


from PyQt5 import QtCore, QtWidgets, QtGui
from linuxnano.strings import strings
from linuxnano.data import HalNode, DigitalInputNode, DigitalOutputNode #, AnalogInputNode, AnalogOutputNode


class HalReader():
    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.read_it)
        self._tool_model = None

        self.prev = 0

        self.setup()
        self.findPins()


    def setupEthercat(self):
        subprocess.call(['halcmd', 'loadusr', '-W', 'lcec_conf', 'ethercat_config.xml'])
        subprocess.call(['halcmd', 'loadrt', 'lcec'])
        subprocess.call(['halcmd', 'addf', 'lcec.read-all', 'servo'])
        subprocess.call(['halcmd', 'addf', 'lcec.write-all', 'servo'])


    def findPins(self):
        pins = subprocess.check_output(['halcmd', 'show', 'pin']).splitlines()
        pins.pop(0) # "Component Pins:""
        pins.pop(-1) # Empty line

        d_in_pins = ['None']
        d_out_pins = ['None']

        for pin in pins:
            line = pin.decode('utf-8')
            items = line.split()

            if items[1] == 'bit' and items[2] == 'IN':
                d_out_pins.append(items[4])

            if items[1] == 'bit' and items[2] == 'OUT':
                d_in_pins.append(items[4])

        DigitalInputNode.hal_pins = d_in_pins
        DigitalOutputNode.hal_pins = d_out_pins



    def setup(self):
        subprocess.call(['halcmd', 'stop'])
        subprocess.call(['halcmd', 'unload', 'all'])


        subprocess.call(['halcmd', 'loadrt', 'threads', 'name1=gui', 'period1=500000000']) #updates every 0.5 sec, or 500,000,000 ns
        #subprocess.call(['halcmd', 'loadusr', 'halscope'])

        #sudo halcompile --install linuxnano/HAL/hardware_sim.comp
        subprocess.call(['halcmd', 'loadrt', 'hardware_sim'])

        #subprocess.call(['halcmd', 'loadrt', 'siggen'])
        #subprocess.call(['halcmd', 'addf', 'siggen.0.update', 'gui'])

    def start(self):
        self.read_data()
        self.timer.start(700)

    def stop(self):
        self.timer.stop()
        subprocess.call(['halcmd', 'stop'])
        subprocess.call(['halcmd', 'unload', 'all'])


    def setModel(self, value):
        self._tool_model = value

    def model(self):
        return self._tool_model


    def loadSampler(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())

        indexes = tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)

        cfg = 'cfg='

        for index in indexes:
            for hal_pin in index.internalPointer().halPins:
                if hal_pin is not None and hal_pin in DigitalOutputNode.hal_pins:
                    cfg += 'b'

        subprocess.call(['halcmd', 'loadrt', 'sampler', 'depth=100', cfg])
        print("\nCFG is: ", cfg)

        sampler_pin = 0

        for index in indexes:
            sys_name = tool_model.parent(tool_model.parent(index)).internalPointer().name
            dev_name = tool_model.parent(index).internalPointer().name
            pin_name = index.internalPointer().name

            net_name = sys_name+'.'+dev_name+'.'+pin_name
            pin_number = 0

            signal_names = index.internalPointer().signals()

            for i, hal_pin in enumerate(index.internalPointer().halPins):
                if hal_pin is not None and hal_pin in DigitalOutputNode.hal_pins:

                    print('\nhalcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin))
                    feedback = subprocess.check_output(['halcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin)])

                    #feedback = subprocess.check_output(['halcmd', 'net', net_name+'.'+str(pin_number), hal_pin, '=>','sampler.0.pin.'+str(sampler_pin)])
                    #pin_number += 1
                    sampler_pin += 1

                    #print("\n")
                    #print(feedback)




        subprocess.call(['halcmd', 'addf', 'sampler.0', 'gui'])
        subprocess.call(['halcmd', 'setp', 'sampler.0.enable', 'True'])
        subprocess.call(['halcmd', 'start'])
        subprocess.call(['halcmd', 'loadusr', 'halmeter'])

        subprocess.call(['halcmd', 'net', 'Chamber_A.ForelineValve.Output.0', '<=', 'hardware-sim.0.d-in-0'])



    def output_reader(self, process):
        for line in iter(process.stdout.readline, b''):
            print('LINE: {0}'.format(line.decode('utf-8')), end='')



    def read_it(self):
        while True:
            try:
                line = self.q.get_nowait()
                print("line", line)
            except Empty:
                break

        return


    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()


    def read_data(self):
        ###### Sampler #####
        self.p = subprocess.Popen(['stdbuf', '-oL', 'halcmd', 'loadusr', 'halsampler', '-c', '0', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        self.q = Queue()
        t = Thread(target=self.enqueue_output, args=(self.p.stdout, self.q))
        t.daemon = True
        t.start()


        return




        tool_index = self._tool_model.index(0, 0, QtCore.QModelIndex())
        system_index = tool_index.child(0, 0)
        device_index = system_index.child(0, 0)


        for row in range(self._tool_model.rowCount(device_index)):
            if device_index.child(row,0).internalPointer().typeInfo() == strings.D_OUT_NODE:
                d_out_index = device_index.child(row,20)

        if self.prev:
            new = 0
        else:
            new = 1
        self.prev = new
        self._tool_model.setData(d_out_index,new)
