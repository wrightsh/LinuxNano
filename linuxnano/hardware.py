
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

        self.sampler_queue = Queue()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.readSampler)

        self._tool_model = None

        self.setup()
        self.findPins()


    def setModel(self, value):
        self._tool_model = value

    def model(self):
        return self._tool_model


    def setupEthercat(self):
        subprocess.call(['halcmd', 'loadusr', '-W', 'lcec_conf', 'ethercat_config.xml'])
        subprocess.call(['halcmd', 'loadrt', 'lcec'])
        subprocess.call(['halcmd', 'addf', 'lcec.read-all', 'servo'])
        subprocess.call(['halcmd', 'addf', 'lcec.write-all', 'servo'])


    def setup(self):
        subprocess.call(['halcmd', 'stop'])
        subprocess.call(['halcmd', 'unload', 'all'])

        subprocess.call(['halcmd', 'loadrt', 'threads', 'name1=gui', 'period1=100000000']) #updates every 0.5 sec, or 500,000,000 ns

        #sudo halcompile --install linuxnano/HAL/hardware_sim.comp
        subprocess.call(['halcmd', 'loadrt', 'hardware_sim'])


        #Old
        #subprocess.call(['halcmd', 'loadusr', 'halscope'])
        #subprocess.call(['halcmd', 'loadrt', 'siggen'])
        #subprocess.call(['halcmd', 'addf', 'siggen.0.update', 'gui'])


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


    def start(self):
        self.loadSampler()
        self.timer.start(100)

    def stop(self):
        self.timer.stop()
        subprocess.call(['halcmd', 'stop'])
        subprocess.call(['halcmd', 'unload', 'all'])


    def loadSampler(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())

        indexes = tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)

        cfg = 'cfg='
        pins_in_use = []

        #find how many of each type of pin
        #if a pin is used twice it needs a pointer to the first instance
        for index in indexes:
            for hal_pin in index.internalPointer().halPins:
                if hal_pin is not None and hal_pin in DigitalOutputNode.hal_pins:
                    if hal_pin not in pins_in_use:
                        cfg += 'b'
                    pins_in_use.append(hal_pin)

        #load sampler with one pin for each
        subprocess.call(['halcmd', 'loadrt', 'sampler', 'depth=100', cfg])
        #print("\nCFG is: ", cfg)






        sampler_pin = 0
        pins_in_use = []
        self._sampler_sequence = ()

        for index in indexes:
            sys_name = tool_model.parent(tool_model.parent(index)).internalPointer().name
            dev_name = tool_model.parent(index).internalPointer().name
            pin_name = index.internalPointer().name

            net_name = sys_name + '.' + dev_name + '.' + pin_name
            pin_number = 0

            signal_names = index.internalPointer().signals()
            sampler_pins = []

            for i, hal_pin in enumerate(index.internalPointer().halPins):
                if hal_pin is not None and hal_pin in DigitalOutputNode.hal_pins:
                    if hal_pin not in pins_in_use:
                        print('\nhalcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.' + str(sampler_pin))
                        feedback = subprocess.check_output(['halcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin)])
                        sampler_pin += 1
                        sampler_pins.append(sampler_pin-1)

                    else:
                        sampler_pins.append(pins_in_use.index(hal_pin))

                    pins_in_use.append(hal_pin)

            index.internalPointer().setSamplerPins(sampler_pins)


        subprocess.call(['halcmd', 'setp', 'sampler.0.enable', 'True'])
        subprocess.call(['halcmd', 'addf', 'sampler.0', 'gui'])


        # Sampler userspace component, stdbuf fixes bufering issue
        self.p = subprocess.Popen(['stdbuf', '-oL', 'halcmd', 'loadusr', 'halsampler', '-c', '0', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        t = Thread(target=self.enqueue_output, args=(self.p.stdout, self.sampler_queue))
        t.daemon = True
        t.start()



        subprocess.call(['halcmd', 'start'])
        #subprocess.call(['halcmd', 'loadusr', 'halmeter'])

        #subprocess.call(['halcmd', 'net', 'Chamber_A.ForelineValve.Output.0', '<=', 'hardware-sim.0.d-in-0'])



    #def output_reader(self, process):
    #    for line in iter(process.stdout.readline, b''):
    #        print('LINE: {0}'.format(line.decode('utf-8')), end='')



    def readSampler(self):
        while True:
            try:
                data = self.sampler_queue.get_nowait()
                #print('sampler:', data)

                data = data.split(b' ')
                data.pop(-1) #remove trailing b'\n'

                current_sample = int(data[0])
                data.pop(0)


                tool_model = self.model()
                tool_index = tool_model.index(0, 0, QtCore.QModelIndex())

                indexes = tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)

                for index in indexes:

                    #List of indexes for what each bits sampler position is
                    sampler_pins = index.internalPointer().samplerPins()
                    val = 0
                    for shift, pin in enumerate(sampler_pins):
                        bit = bool(int(data[pin])) #b'0' to False, b'1' to True
                        val += bit<<shift

                    #print("setting index:", name,  ': ', val)

                    if val != self._tool_model.data(index.siblingAtColumn(20), QtCore.Qt.DisplayRole):
                        self._tool_model.setData(index.siblingAtColumn(20), val)
                        name = index.internalPointer().parent().name
                        print("setting index:", name,  ': ', val)


            except Empty:
                break

        return


    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()





    ''' OLD


    def old_loadSampler(self):
        ###### Sampler #####
        self.p = subprocess.Popen(['stdbuf', '-oL', 'halcmd', 'loadusr', 'halsampler', '-c', '0', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        self.sampler_queue = Queue()
        t = Thread(target=self.enqueue_output, args=(self.p.stdout, self.sampler_queue))
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
        '''
