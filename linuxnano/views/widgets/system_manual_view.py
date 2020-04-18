#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg
from linuxnano.strings import strings
from linuxnano.views.widgets.device_icon_widget import DeviceIconWidget


class SystemManualView(QtWidgets.QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scene_box = QtCore.QRectF(0, 0, 1000, 1000)

        self._previous_index = None
        self._scene = QtWidgets.QGraphicsScene(self)
        self._renderers = []
        self._device_icons = []

        #UI Stuff
        self._view = QtWidgets.QGraphicsView(self)
        self._view.setScene(self._scene)
        self._view.scale(1, 1)


        #Layout
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(self._view)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)

        self._current_system_index = None


    def resizeEvent(self, event):
        self._view.fitInView(self._scene_box, QtCore.Qt.KeepAspectRatio)


    #TODO will this called too often?
    def dataChanged(self, index_top_left, index_bottom_right, roles):

        index = index_top_left
        tool_model = self.model()

        if index == self._current_system_index and index.column() == 10: #systems background svg is changed
            self.setBackground(tool_model.data(index, QtCore.Qt.DisplayRole))

        elif index.internalPointer().typeInfo() == strings.DEVICE_ICON_NODE and  index.parent().parent() == self._current_system_index:
            if index.column() == 10:
                try:
                    icon_node = index.internalPointer()
                    wid = self._device_icons[index.parent().row()]
                    wid.renderer().load(icon_node.svg)
                    wid.setElementId(icon_node.layer())
                except:
                    pass

            elif index.column() == 11:
                try:
                    icon_node = index.internalPointer()
                    wid = self._device_icons[index.parent().row()]
                    wid.setElementId(icon_node.layer())
                except:
                    pass

            elif index.column() in [14, 15, 16, 17]: # [x, y, scale, rotation]
                try:
                    icon_node = index.internalPointer()

                    #Since each device has to have a single icon the parents row is the same as this index
                    wid = self._device_icons[index.parent().row()]
                    wid.setPos(float(icon_node.x) , float(icon_node.y))
                    wid.setRotation(float(icon_node.rotation))
                    wid.setScale(float(icon_node.scale))
                except:
                    pass


            #print(index_top_left.row(), index_top_left.column(), index_bottom_right.row(), index_bottom_right.column())


    def rowsAboutToBeRemoved(self, parent_index, start, end):
        #TODO when this is called those rows still exist so this isn't really delt with correctly
        #this is almost a start but not there...
        #if parent_index.internalPointer().typeInfo() == strings.DEVICE_NODE and  index.parent() == self._current_system_index:
        #    self._device_icons.pop(1)
        #self.displaySystem(self._current_system_index)
        pass

    def rowsInserted(self, parent_index, start, end):
        self.displaySystem(self._current_system_index)

    #This abstract view needs to emit a currentChanged(
    def setSelection(self, index):#, old):
        if hasattr(index.model(), 'mapToSource'):
            index = index.model().mapToSource(index)

        if self._previous_index == index:
            return

        model = index.model()
        node  = index.internalPointer()

        type_info = None
        if node is not None:
            type_info = node.typeInfo()

        if type_info == strings.SYSTEM_NODE:
            self._current_system_index = index
            self.displaySystem(self._current_system_index)


        elif type_info == strings.DEVICE_NODE:
            if index.parent() != self._current_system_index:
                self._current_system_index = index.parent()
                self.displaySystem(self._current_system_index)

            for icon in self._device_icons:
                icon.clearSelected()

            self._device_icons[index.row()].setSelected()
            self._previous_index = index
            self.setCurrentIndex(index)



    def displaySystem(self, system_index):
        self._view.resetTransform() #Needed?
        self._scene.clear()
        self._device_icons = []

        if system_index == None:
            return

        system_node = system_index.internalPointer()
        svg_image = system_node.backgroundSVG

        #Border line around background image
        rectangle = QtWidgets.QGraphicsRectItem(self._scene_box)
        self._scene.addItem(rectangle)

        background = QtGui.QPixmap(svg_image)
        background = background.scaled(self._scene_box.width(), self._scene_box.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self._scene.addPixmap(background)


        #Add the Device Icons
        icon_indexes = self.model().indexesOfType(strings.DEVICE_ICON_NODE, system_index)

        for icon_index in icon_indexes:

            icon_node = icon_index.internalPointer()

            renderer = QtSvg.QSvgRenderer(self)
            renderer.load(icon_node.svg)

            wid = DeviceIconWidget(renderer)
            wid.setCallback(self.setSelection)
            wid.setIndex(icon_index.parent())
            wid.setElementId(icon_node.layer())

            wid.setPos(float(icon_node.x) , float(icon_node.y))
            wid.setRotation(float(icon_node.rotation))
            wid.setScale(float(icon_node.scale))

            self._device_icons.append(wid)
            self._scene.addItem(wid)

            #if icon_node.numberNode is not None:
            #    #TODO: remove this block
            #    spin = QtWidgets.QLabel('1.23 mTorr')
            #    #self._data_mappers[-1].addMapping(spin, 12)
            #    prox_spin = self._scene.addWidget(spin)

            #    number_x = x + float(icon_node.numberX)
            #    number_y = y + float(icon_node.numberY)
            #    transform = QtGui.QTransform()
            #    transform.translate( number_x , number_y)
            #    prox_spin.setTransform( transform )


        #Resize the view
        self._view.fitInView(self._scene_box, QtCore.Qt.KeepAspectRatio)



    # TODO : No idea what this should do.
    def visualRegionForSelection(self, selection):
        return QtGui.QRegion()

    # TODO : No idea what this should do.
    def scrollTo(self, index, hint):
        return

    # TODO : No idea what this should do.
    def visualRect(self, index):
        return QtCore.QRect()

    # TODO : No idea what this should do.
    def verticalOffset(self):
        return 0

    # TODO : No idea what this should do.
    def horizontalOffset(self):
        return 0

    # TODO : No idea what this should do.
    def moveCursor(self, action, modifier):
        return QtCore.QModelIndex()
