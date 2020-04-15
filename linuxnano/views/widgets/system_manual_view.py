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
        self.graphics_scene = QtWidgets.QGraphicsScene(self)

        #UI Stuff
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.scale(1,1)

        self._extra_margin = 10

        #Layout
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(self.graphics_view)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)

        self._current_system_index = None
        self._device_icons = []

    def resizeEvent(self, event):
        self.graphics_view.fitInView(self._scene_box, QtCore.Qt.KeepAspectRatio)

    #ToDo will this called too often?
    def dataChanged(self, index_top_left, index_bottom_right, roles):

        index = index_top_left
        tool_model = self.model()


        if index == self._current_system_index and index.column() == 10: #systems background svg is changed
            self.setBackground(tool_model.data(index, QtCore.Qt.DisplayRole))

        elif index.internalPointer().typeInfo() == strings.DEVICE_ICON_NODE:
            if index.column() == 11:
                my_icon_wid.layer = tool_model.data(index, QtCore.Qt.DisplayRole)

            elif index.column() in [14, 15, 16, 17]:
                my_icon_wid.setTranslation(stuff)


            print('updating icons....')
            #print(index_top_left.row(), index_top_left.column(), index_bottom_right.row(), index_bottom_right.column())








            

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




    def updateIcons(self):

        for icon_proxy in self._device_icon_proxies:

            transform = QtGui.QTransform()
            transform.translate( float(icon_node.x) , float(icon_node.y)  )
            transform.rotate( float(icon_node.rotation) )
            transform.scale(float(icon_node.scale), float(icon_node.scale) )

            icon_proxy.setTransform( self.iconTransform(icon_node))






    def iconTransform(self, icon_node):
        transform = QtGui.QTransform()

        transform.translate( float(icon_node.x) , float(icon_node.y)  )
        transform.rotate( float(icon_node.rotation) )
        transform.scale(float(icon_node.scale), float(icon_node.scale) )

        return transform

    def addDeviceIcon(self, icon_index):
        '''
          - Must keep each icon inside of the self._scene_box
          - Do we want to map all these?
          - Add a mapping to the other things that just calls the same functin to set a icons position?
        '''
        icon_node   = icon_index.internalPointer()

        wid = DeviceIconWidget()
        wid.setIcon(icon_node.svg)
        wid.setCallback(self.setSelection)
        wid.setIndex(icon_index.parent())

        self._device_icons.append(wid)
        proxWid = self.graphics_scene.addWidget(wid)
        proxWid.setTransform( self.iconTransform(icon_node))

        #x       = float(icon_node.x)
        #y       = float(icon_node.y)
        #rot     = float(icon_node.rotation)
        #scale   = float(icon_node.scale)
#
        #bounds   = proxWid.boundingRect()
        #center_x =  bounds.width() * 0.5
        #center_y =  bounds.height() * 0.5
#
        #transform = QtGui.QTransform()
#
        #transform.translate( x , y  )
        #transform.translate( center_x , center_y  )
#
        #transform.rotate( rot )
        #transform.scale(scale,scale)
        #transform.translate( -center_x , -center_y )




        #if icon_node.numberNode is not None:
        #    #TODO: remove this block
        #    spin = QtWidgets.QLabel('1.23 mTorr')
        #    #self._data_mappers[-1].addMapping(spin, 12)
        #    prox_spin = self.graphics_scene.addWidget(spin)
#
        #    number_x = x + float(icon_node.numberX)
        #    number_y = y + float(icon_node.numberY)
        #    transform = QtGui.QTransform()
        #    transform.translate( number_x , number_y)
        #    prox_spin.setTransform( transform )



        mapper = QtWidgets.QDataWidgetMapper()
        mapper.setModel(self.model())
        mapper.addMapping(wid, 11, bytes('layer','ascii'))

        mapper.setRootIndex(icon_index.parent().parent())
        mapper.setCurrentModelIndex(icon_index.parent())

        self._data_mappers.append(mapper)



    def displaySystem(self, system_index):
        self.graphics_scene.clear()
        self._device_icons = []
        self._data_mappers = []

        system_node = system_index.internalPointer()
        svg_image = system_node.backgroundSVG

        #Border line around background image
        rectangle = QtWidgets.QGraphicsRectItem(self._scene_box)
        self.graphics_scene.addItem(rectangle)

        background = QtGui.QPixmap(svg_image)
        background = background.scaled(self._scene_box.width(), self._scene_box.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.graphics_scene.addPixmap(background)


        #Add the Device Icons
        icon_indexes = self.model().indexesOfType(strings.DEVICE_ICON_NODE, system_index)

        for icon_index in icon_indexes:
            self.addDeviceIcon(icon_index)

        #Resize the view
        self.graphics_view.fitInView(self._scene_box, QtCore.Qt.KeepAspectRatio)
