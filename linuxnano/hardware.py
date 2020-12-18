
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

import ctypes
#use ctypes.c_ulong, c_long and c_float

class HalReader():
    def __init__(self):
        super().__init__()

        self.sampler_queue = Queue()
        self.streamer_queue = Queue()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.processData)

        self._tool_model = None



    def setModel(self, value):
        self._tool_model = value

    def model(self):
        return self._tool_model

    def start(self):
        self._previous_stream = []
        self.setup()
        self.findPins()


        self.loadSampler()
        self.connectSamplerSignals()

        self.loadStreamer()
        self.connectStreamerSignals()

        subprocess.call(['halcmd', 'start'])
        subprocess.call(['halcmd', 'loadusr', 'halmeter'])

        self.timer.start(100)


    def stop(self):
        self.timer.stop()
        subprocess.call(['halcmd', 'stop'])
        subprocess.call(['halcmd', 'unload', 'all'])



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

        #subprocess.call(['halcmd', 'loadusr', 'halscope'])

        #Simulating a digital input with siggen.0.square in tool_model_1
        #subprocess.call(['halcmd', 'loadrt', 'siggen'])
        #subprocess.call(['halcmd', 'addf', 'siggen.0.update', 'gui'])
        #subprocess.call(['halcmd', 'setp', 'siggen.0.amplitude', '0.5'])
        #subprocess.call(['halcmd', 'setp', 'siggen.0.offset', '0.5'])
        #subprocess.call(['halcmd', 'setp', 'siggen.0.frequency', '0.5'])

        subprocess.call(['halcmd', 'loadrt', 'sim_encoder', 'num_chan=1'])
        subprocess.call(['halcmd', 'setp', 'sim-encoder.0.speed', '0.005'])

        subprocess.call(['halcmd', 'addf', 'sim-encoder.make-pulses', 'gui'])
        subprocess.call(['halcmd', 'addf', 'sim-encoder.update-speed', 'gui'])




    def findPins(self):
        pins = subprocess.check_output(['halcmd', 'show', 'pin']).splitlines()
        pins.pop(0) # "Component Pins:""
        pins.pop(-1) # Empty line

        #If we don't lose the reference to the initial list then everything will update correctly
        HalNode.hal_pins.clear()

        for pin in pins:
            line = pin.decode('utf-8')
            items = line.split()

            if items[1] in ['bit']: #, 'S32', 'U32', 'FLOAT']:
                pin = (items[4], items[1], items[2]) #(name, bit, IN)
                HalNode.hal_pins.append(pin)
            #if items[1] == 'bit' and items[2] == 'IN':
                #DigitalOutputNode.hal_pins.append(items[4])

            #if items[1] == 'bit' and items[2] == 'OUT':
                #DigitalInputNode.hal_pins.append(items[4])


    ''' Remove? '''
    #def samplerHalPins(self):
    #    return HalNode.hal_pins
    #    #return DigitalInputNode.hal_pins + DigitalOutputNode.hal_pins

    def samplerIndexes(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
        indexes = tool_model.indexesOfType(strings.D_IN_NODE, tool_index)
        indexes += tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)
        #indexes += tool_model.indexesOfType(strings.A_IN_NODE, tool_index)
        #indexes += tool_model.indexesOfType(strings.A_OUT_NODE, tool_index)
        #indexes += tool_model.indexesOfType(strings.A_FEEDBACK_NODE, tool_index)

        return indexes


    def streamerIndexes(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
        indexes = tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)
        #indexes += tool_model.indexesOfType(strings.A_OUT_NODE, tool_index)
        #indexes += tool_model.indexesOfType(strings.A_FEEDBACK_NODE, tool_index)

        return indexes



    def dInPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] == 'bit']
        pins = [item for item in sub_pins if item[2] == 'OUT']
        return pins

    def dOutPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] == 'bit']
        pins = [item for item in sub_pins if item[2] == 'IN']
        return pins

    def aInPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] in ['S32','U32','FLOAT']]
        pins = [item for item in sub_pins if item[2] == 'OUT']
        return pins

    def aOutPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] in ['S32','U32','FLOAT']]
        pins = [item for item in sub_pins if item[2] == 'IN']
        return pins


    def pinTypeToChar(self, pin_type):
        if pin_type == 'bit':
            return 'b'
        elif pin_type == 'S32':
            return 's'
        elif pin_type == 'U32':
            return 'u'
        elif pin_type == 'FLOAT':
            return 'f'



    def pinNameToType(self, pin_name):
        #TODO add check on pin_name
        all_pins = HalNode.hal_pins #list of (name, type, dir)

        pin_info = [item for item in all_pins if item[0] == pin_name]
        pin_type = pin_info[0][1]

        if pin_type == 'bit':
            return 'b'
        elif pin_type == 'S32':
            return 's'
        elif pin_type == 'U32':
            return 'u'
        elif pin_type == 'FLOAT':
            return 'f'


    def loadSampler(self):
        cfg = 'cfg='
        self.connected_sampler_pins = [] #Maybe?--> [('pin_name', index1, index2, index...), (), ()...]

        #Each halpin is only loaded once
        for index in self.samplerIndexes():
            node = index.internalPointer()
            if node.typeInfo() == strings.D_IN_NODE:
                for pin in node.halPins:
                    if pin in self.dInPins and pin not in connected_pins:
                        cfg += 'b'
                        self.connected_sampler_pins.append(pin)

            elif node.typeInfo() == strings.D_OUT_NODE:
                for pin in node.halPins:
                    if pin in self.dOutPins and pin not in connected_pins:
                        cfg += 'b'
                        self.connected_sampler_pins.append(pin)

            elif node.typeInfo() == strings.A_IN_NODE:
                for pin in node.halPins:
                    if pin in self.aInPins and pin not in connected_pins:
                        cfg += self.pinNameToType(pin)
                        self.connected_sampler_pins.append(pin)

            elif node.typeInfo() == strings.A_OUT_NODE:
                for pin in node.halPins:
                    if pin in self.aOutPins and pin not in connected_pins:
                        cfg += self.pinNameToType(pin)
                        self.connected_sampler_pins.append(pin)


# really the problem is defining states for analog nodes
# example.  temp setpoint and 2 thermcouples.  can have large delta between set and thermcouple for a while, but even
# a small difference between thermcouples should alarm as that  means a TC broke



        subprocess.call(['halcmd', 'loadrt', 'sampler', 'depth=100', cfg])
        print("\nSampler CFG is: ", cfg)





















        ''' ------------------------'''
        cfg = 'cfg='

        pins_to_connect = []
        for index in self.samplerIndexes():
            pins_to_connect.append(index.internalPointer().samplerPins())



        for pin_name, dir, type in HalNode.hal_pins:
            if dir == 'OUT' and pin_name in pins_to_connect:
                if type == 'bit':
                    cfg += 'b'
                #elif type == 'S32':
                #    cfg += 'b'
                #elif type == 'U32':
                #    cfg += 'b'
                #elif type == 'FLOAT':
                #    cfg += 'b'



        connected_pins = []
        #Each halpin is only loaded once
        for index in self.samplerIndexes():
            node = index.internalPointer()

            for hal_pin in node.samplerPins():
                #ugh this isn't even right now
                if hal_pin in HalNode.hal_pins and hal_pin is not None:
                    if hal_pin not in connected_pins:
                        cfg += 'b'
                    connected_pins.append(hal_pin)

        subprocess.call(['halcmd', 'loadrt', 'sampler', 'depth=100', cfg])
        print("\nSampler CFG is: ", cfg)


    def connectSamplerSignals(self):
        sampler_pin = 0
        connected_pins = [] #['pin_a','pin_b'], ordered by how its connected to the sampler

        for index in self.samplerIndexes():
            node = index.internalPointer()
            signal_names = node.samplerSignals()
            node_sampler_pins = []

            for i, hal_pin in enumerate(node.samplerPins()):
                if hal_pin in HalNode.hal_pins and hal_pin is not None:  #TODO this doesn't check if the pin is the right type
                    if hal_pin not in connected_pins:
                        subprocess.call(['halcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin)])
                        print(         '\nhalcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin))

                        connected_pins.append(hal_pin)
                        node_sampler_pins.append(sampler_pin)
                        sampler_pin += 1

                    else:
                        node_sampler_pins.append(connected_pins.index(hal_pin))

            node.setSamplerPins(node_sampler_pins) # This is a list of indexes


        subprocess.call(['halcmd', 'setp', 'sampler.0.enable', 'True'])
        subprocess.call(['halcmd', 'addf', 'sampler.0', 'gui'])


        # Sampler userspace component, stdbuf fixes bufering issue
        self.p_sampler = subprocess.Popen(['stdbuf', '-oL', 'halcmd', 'loadusr', 'halsampler', '-c', '0', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        t = Thread(target=self.enqueue_sampler, args=(self.p_sampler.stdout, self.sampler_queue))
        t.daemon = True
        t.start()


    ''' FIX '''
    def loadStreamer(self):
        cfg = 'cfg='
        connected_pins = []

        #Each halpin is only loaded once
        for index in self.streamerIndexes():
            for hal_pin in index.internalPointer().halPins:
                if hal_pin in DigitalOutputNode.hal_pins and hal_pin is not None:
                    if hal_pin not in connected_pins:
                        cfg += 'b'
                        self._previous_stream.append(0)
                    connected_pins.append(hal_pin)

        subprocess.call(['halcmd', 'loadrt', 'streamer', 'depth=100', cfg])
        print("\nStreamer CFG is: ", cfg)




    def connectStreamerSignals(self):
        streamer_pin = 0
        connected_pins = [] #['pin_a','pin_b'], ordered by how its connected to the streamer

        for index in self.streamerIndexes():
            signal_names = index.internalPointer().signals()
            node_streamer_pins = []

            for i, hal_pin in enumerate(index.internalPointer().halPins):
                if hal_pin is not None and hal_pin in DigitalOutputNode.hal_pins:
                    if hal_pin not in connected_pins:
                        subprocess.call(['halcmd', 'net', signal_names[i], hal_pin, '=>','streamer.0.pin.'+str(streamer_pin)])
                        print(         '\nhalcmd', 'net', signal_names[i], hal_pin, '=>','streamer.0.pin.'+str(streamer_pin))

                        connected_pins.append(hal_pin)
                        node_streamer_pins.append(streamer_pin)
                        streamer_pin += 1

                    else:
                        raise ValueError("Cannot have halpin connected from multiple output nodes")
                        #node_streamer_pins.append(connected_pins.index(hal_pin))

            index.internalPointer().setStreamerPins(node_streamer_pins) # This is a list of indexes


        subprocess.call(['halcmd', 'setp', 'streamer.0.enable', 'True'])
        subprocess.call(['halcmd', 'addf', 'streamer.0', 'gui'])


        # Streamer userspace component, stdbuf fixes bufering issue
        self.p_streamer = subprocess.Popen(['halcmd', 'loadusr', 'halstreamer', '-c', '0'], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)



    def processData(self):
        self.readSampler()
        self.writeStreamer()


        #set all the device states
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
        indexes = tool_model.indexesOfType(strings.DEVICE_NODE, tool_index)

        for index in indexes:
            device_state = index.internalPointer().stateFromChildren()

            if device_state != tool_model.data(index.siblingAtColumn(16), QtCore.Qt.DisplayRole):
                self._tool_model.setData(index.siblingAtColumn(16), device_state)
                device_status = index.internalPointer().status()
                self._tool_model.setData(index.siblingAtColumn(11), device_status)
                print("Device State: ", device_state)



        #set all the device icon layers
        indexes = tool_model.indexesOfType(strings.DEVICE_ICON_NODE, tool_index)
        for index in indexes:
            icon_layer = index.parent().internalPointer().iconLayer()

            if icon_layer != index.internalPointer().layer():
                tool_model.setData(index.siblingAtColumn(11), icon_layer)



    def writeStreamer(self):
        new_stream = self._previous_stream[:]

        for index in self.streamerIndexes():
            try:
                new_val = index.internalPointer().manualQueueGet()

                if new_val is not None:
                    streamer_pins = index.internalPointer().streamerPins()

                    for shift, pin in enumerate(streamer_pins):
                        if (new_val>>shift)&1 == 1:
                            new_stream[pin] = 1
                        else:
                            new_stream[pin] = 0

            except Empty:
                pass

        if new_stream != self._previous_stream:
            print("new_stream: ", new_stream)

            tmp = ''
            for item in new_stream:
                tmp += str(item)
                tmp += ' '

            tmp = tmp[:-1]+'\n'

            self.p_streamer.stdin.write( tmp.encode() )#hstrip brackets, add \n and convert to bytes
            self.p_streamer.stdin.flush()

            self._previous_stream = new_stream


    def readSampler(self):
        while not self.sampler_queue.empty():
            data = self.sampler_queue.get_nowait()
            #print('sampler:', data)

            data = data.split(b' ')
            data.pop(-1) #remove trailing b'\n'
            current_sample = int(data[0])
            data.pop(0)

            ''' # TODO:
                     - Find what pins are different
                     - figure out what indexes they belong to
                     - Figure out how to do the setData for those indexes


                     need to call setData

                    A_Feedback:

                    make a setHalData in the tool model?

            '''




            for index in self.samplerIndexes():
                node = index.internalPointer()
                #List of indexes for what each bits sampler position is
                sampler_pins = node.samplerPins()

                if node.typeInfo() in [strings.DigitalInputNode, strings.DigitalOutputNode]:
                    val = 0

                    for shift, pin in enumerate(sampler_pins):
                        bit = bool(int(data[pin])) #b'0' to False, b'1' to True
                        val += bit<<shift

                    if val != self._tool_model.data(index.siblingAtColumn(20), QtCore.Qt.DisplayRole):
                        self._tool_model.setData(index.siblingAtColumn(20), val)
                        name = node.parent().name
                        #print("setting index:", name,  ': ', val)



    def enqueue_sampler(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()
