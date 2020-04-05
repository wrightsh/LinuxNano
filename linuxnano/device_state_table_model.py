#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import itertools

import linuxnano.strings
from linuxnano.message_box import MessageBox



class DeviceStateTableModel(QtCore.QAbstractTableModel):
    '''This is owned by the device node.  When setup first calls setNodeStates, passing a 2d array where each row
       has the name of the HalNode followed by it's possible states.  This is used to form a truth table of all
       possible states.

       setNodeStates is called anytime one of the devices HalNode is added/removed/changed
       dataArray is used to load/save the information in the table
    '''
    def __init__(self, parent = None):
        super().__init__(parent)

        self._default_headers = ['Status',
                                 'Icon Layer\nName',
                                 'Is Warning',   #True / False
                                 'Warning\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Warning Message',   # "Warning: Foreline valve taking longer then 5 seconds to open"
                                 'Is Alarm',   #True / False
                                 'Alarm\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Alarm Message',   # "Alarm: Foreline failed to open withing 5 sec time out"
                                 'Triggers\nAction',   #True / False
                                 'Action\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Action',   # "set valve_output to True" - TODO need to make interface for setting a devices outputs in a recipe
                                 'Log Entrance'] # True / False

        self._default_data_row = ['unknown status', 'layer_n', False, 0, '', False, 0, '', False, 0, None, True]

        self._headers = self._default_headers
        self._data = [self._default_data_row]

        self._data_array_headers = ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance']
        self._truth_table = [['off'],
                             ['on']]


    def statusColumn(self):         return len(self._truth_table[0])
    def iconLayerColumn(self):      return len(self._truth_table[0]) + 1
    def isWarningColumn(self):      return len(self._truth_table[0]) + 2
    def warningTimeoutColumn(self): return len(self._truth_table[0]) + 3
    def warningMessageColumn(self): return len(self._truth_table[0]) + 4
    def isAlarmColumn(self):        return len(self._truth_table[0]) + 5
    def alarmTimeoutColumn(self):   return len(self._truth_table[0]) + 6
    def alarmMessageColumn(self):   return len(self._truth_table[0]) + 7
    def triggersActionColumn(self): return len(self._truth_table[0]) + 8
    def actionTimeoutColumn(self):  return len(self._truth_table[0]) + 9
    def actionColumn(self):         return len(self._truth_table[0]) + 10
    def logEntranceColumn(self):    return len(self._truth_table[0]) + 11

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])


    #TODO I think this being called too often during load
    def setNodeStates(self, list_of_states):
        err = "List of states must be in form [ ('io_name_1', ['state_1', 'state_2']), ('io_name_2', ['state_1','state_2']) ]"

        states = list_of_states[::-1] #reverses the order
        headers = [row[0] for row in states]
        states  = [row[1] for row in states]

        if not all(isinstance(item, str) for item in headers):
            raise TypeError(err)

        for row in states:
            if not isinstance(row, list):
                raise TypeError(err)

            if not all(isinstance(item, str) for item in row):
                raise TypeError(err)

        tbl = []
        for e in itertools.product(*states):
            tbl.append(list(e))

        self._truth_table = tbl

        #Anytime the truth table is changed we need to update the data layout and the headers
        self.beginResetModel()

        new_data = self._truth_table[:]
        for i, row in enumerate(new_data):
            new_data[i] = new_data[i] + self._default_data_row[:]

        self._data = new_data
        self._headers = headers + self._default_headers

        self.endResetModel()

        return True

    def truthTable(self):
        return self._truth_table


    def setDeviceStates(self, data):
        '''
            in format [ ['state', 'status'      , 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message',
                        [   0   , 'my status 1' , 'layer_0'   ,        False,               0.0,                '',      False,             0.0,              '',
                        [   1   , 'my status 2' , 'layer_1'   ,         True,               5.0,      'my warning',       True,            10.0,    'some alarm',
                        [   2   , 'my status 3' , 'layer_2'   ,        False,               0.0,                '',      False,             0.0,              '',
                        [   3   , 'my status 4' , 'layer_3'   ,        False,               0.0,                '',      False,             0.0,              '',


                                    'triggers_action', 'action_timeout', 'action', 'log_entrance'],
                                                False,              0.0,     None,           True],
                                                 True,             10.0,     None,           True],
                                                False,              0.0,     None,           True],
                                                False,              0.0,     None,           True],



        '''


        if not isinstance(data, list):
            raise TypeError('Invalid data format')

        if not data[0] == self._data_array_headers:
            raise ValueError('Invalid header row, must be: ' + self._data_array_headers)

        data_main = data[1:]
        if len(data_main) != len(self._truth_table):
            raise ValueError('Number of rows must be same as number of states')

        #State column is in order, 0,1,2,.. n
        first_col = [row[0] for row in data_main]
        if first_col != list(range(0, len(self._truth_table))):
            raise ValueError('State column must be in format 0, 1, 2, ...n')

        for row in data_main:
            if not isinstance(row[1], str): raise TypeError('status column must be of type str')
            if not isinstance(row[2], str): raise TypeError('icon_layer column must be of type str')

            if not isinstance(row[3],         bool): raise TypeError('is_warning column must be of type bool')
            if not isinstance(row[4], (int, float)): raise TypeError('warning_timeout column must be of type float')
            if not isinstance(row[5],         str): raise TypeError('warning_message column must be of type str')

            if not isinstance(row[6],         bool): raise TypeError('is_alarm column must be of type bool')
            if not isinstance(row[7], (int, float)): raise TypeError('alarm_timeout column must be of type (int, float)')
            if not isinstance(row[8],          str): raise TypeError('alarm_message column must be of type str')

            if not isinstance( row[9],             bool): raise TypeError('triggers_action must be of type bool')
            if not isinstance(row[10],     (int, float)): raise TypeError('action_timeout must be of type (int, float)')
            if not isinstance(row[11],(int, type(None))): raise TypeError('action must be of type int')
            if not isinstance(row[12],             bool): raise TypeError('log_entrance must be of type bool')


        self.beginResetModel()

        new_data = self._truth_table[:]
        for i, row in enumerate(data_main):
            new_data[i] = new_data[i] + row[1:]
        self._data = new_data

        self.endResetModel()

        return True


    def deviceStates(self):
        data = []
        data.append(self._data_array_headers[:])

        for i, row in enumerate(self._data):
            data.append([ i,
                         self._data[i][self.statusColumn()],
                         self._data[i][self.iconLayerColumn()],
                         self._data[i][self.isWarningColumn()],
                         self._data[i][self.warningTimeoutColumn()],
                         self._data[i][self.warningMessageColumn()],
                         self._data[i][self.isAlarmColumn()],
                         self._data[i][self.alarmTimeoutColumn()],
                         self._data[i][self.alarmMessageColumn()],
                         self._data[i][self.triggersActionColumn()],
                         self._data[i][self.actionTimeoutColumn()],
                         self._data[i][self.actionColumn()],
                         self._data[i][self.logEntranceColumn()] ])

        return data


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return str(section).format("%1")

    def flags(self, index):
        if index.column() < len(self._truth_table[0]):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        elif index.column() in [self.warningTimeoutColumn(), self.warningMessageColumn()] and self._data[index.row()][self.isWarningColumn()] == False:
            return QtCore.Qt.ItemIsSelectable

        elif index.column() in [self.alarmTimeoutColumn(), self.alarmMessageColumn()] and self._data[index.row()][self.isAlarmColumn()] == False:
            return QtCore.Qt.ItemIsSelectable

        elif index.column() in [self.actionTimeoutColumn()] and self._data[index.row()][self.triggersActionColumn()] == False:
            return QtCore.Qt.ItemIsSelectable

        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def data(self, index, role):
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self._data[row][col]

        elif role == QtCore.Qt.ToolTipRole:
            return 'Need to add a tooltip'

        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if type(value) == type(QtCore.QVariant()):
                value = value.toPyObject()

            row = index.row()
            col = index.column()


            if col == self.statusColumn():
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True

            elif col in [self.iconLayerColumn(), self.warningMessageColumn(), self.alarmMessageColumn()]:
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True

            elif col in [self.warningTimeoutColumn(), self.alarmTimeoutColumn(), self.actionTimeoutColumn()]:
                if value == None:
                    self._data[row][col] = None
                else:
                    self._data[row][col] = float(value)

                self.dataChanged.emit(index, index)
                return True

            #FIXME
            elif col == self.actionColumn():
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True

            elif col in [self.isWarningColumn(), self.isAlarmColumn(), self.triggersActionColumn(), self.logEntranceColumn()]:
                if value == True:
                    self._data[row][col] = True
                else:
                    self._data[row][col] = False
                self.dataChanged.emit(index, index)
                return True

        return False
