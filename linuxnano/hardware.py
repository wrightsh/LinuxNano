
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


    def samplerHalPins(self):
        return DigitalInputNode.hal_pins + DigitalOutputNode.hal_pins

    def samplerIndexes(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
        indexes = tool_model.indexesOfType(strings.D_IN_NODE, tool_index)
        indexes += tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)

        return indexes


    def streamerIndexes(self):
        tool_model = self.model()
        tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
        indexes = tool_model.indexesOfType(strings.D_OUT_NODE, tool_index)

        return indexes







    def loadSampler(self):
        cfg = 'cfg='
        connected_pins = []

        #Each halpin is only loaded once
        for index in self.samplerIndexes():
            for hal_pin in index.internalPointer().halPins:
                if hal_pin in self.samplerHalPins() and hal_pin is not None:
                    if hal_pin not in connected_pins:
                        cfg += 'b'
                    connected_pins.append(hal_pin)

        subprocess.call(['halcmd', 'loadrt', 'sampler', 'depth=100', cfg])
        print("\nSampler CFG is: ", cfg)


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


    def connectSamplerSignals(self):
        sampler_pin = 0
        connected_pins = [] #['pin_a','pin_b'], ordered by how its connected to the sampler

        for index in self.samplerIndexes():
            signal_names = index.internalPointer().signals()
            node_sampler_pins = []

            for i, hal_pin in enumerate(index.internalPointer().halPins):
                if hal_pin in self.samplerHalPins() and hal_pin is not None:
                    if hal_pin not in connected_pins:
                        subprocess.call(['halcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin)])
                        print(         '\nhalcmd', 'net', signal_names[i], hal_pin, '=>','sampler.0.pin.'+str(sampler_pin))

                        connected_pins.append(hal_pin)
                        node_sampler_pins.append(sampler_pin)
                        sampler_pin += 1

                    else:
                        node_sampler_pins.append(connected_pins.index(hal_pin))

            index.internalPointer().setSamplerPins(node_sampler_pins) # This is a list of indexes


        subprocess.call(['halcmd', 'setp', 'sampler.0.enable', 'True'])
        subprocess.call(['halcmd', 'addf', 'sampler.0', 'gui'])


        # Sampler userspace component, stdbuf fixes bufering issue
        self.p_sampler = subprocess.Popen(['stdbuf', '-oL', 'halcmd', 'loadusr', 'halsampler', '-c', '0', '-t'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)

        t = Thread(target=self.enqueue_sampler, args=(self.p_sampler.stdout, self.sampler_queue))
        t.daemon = True
        t.start()




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


            for index in self.samplerIndexes():
                #List of indexes for what each bits sampler position is
                sampler_pins = index.internalPointer().samplerPins()
                val = 0

                for shift, pin in enumerate(sampler_pins):
                    bit = bool(int(data[pin])) #b'0' to False, b'1' to True
                    val += bit<<shift

                if val != self._tool_model.data(index.siblingAtColumn(20), QtCore.Qt.DisplayRole):
                    self._tool_model.setData(index.siblingAtColumn(20), val)
                    name = index.internalPointer().parent().name
                    #print("setting index:", name,  ': ', val)



    def enqueue_sampler(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()
