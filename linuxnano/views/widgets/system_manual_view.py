#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg
from linuxnano.strings import strings
from linuxnano.views.widgets.device_icon_widget import DeviceIconWidget

class SystemManualView(QtWidgets.QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._previous_index = None
        self.graphics_scene = QtWidgets.QGraphicsScene(self)

        #UI Stuff
        self.graphics_view  = QtWidgets.QGraphicsView(self)
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.scale(1,1)

        #Layout
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(self.graphics_view)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)

        self._current_system_index = None
        self._device_icons = []


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

        if self._previous_index == index:return

        model = index.model()
        node  = index.internalPointer()

        type_info = None
        if node is not None: type_info = node.typeInfo()

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
        self.graphics_scene.clear()
        self._device_icons = []
        self._data_mappers = []

        system_node = system_index.internalPointer()
        svg_image = system_node.backgroundSVG

        extra_margin = 10
        min_view_dim = min(self.width(), self.height()) - extra_margin
        scene_box = QtCore.QRectF(0, 0, min_view_dim, min_view_dim)

        self.graphics_view.setSceneRect(scene_box)

        rectangle = QtWidgets.QGraphicsRectItem(scene_box)
        self.graphics_scene.addItem(rectangle)
        background = QtGui.QPixmap(svg_image)
        background = background.scaled(min_view_dim,min_view_dim,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.graphics_scene.addPixmap(background)


        #self.svgItem = QtSvg.QGraphicsSvgItem(svg_image)
        #self.svgSize = self.svgItem.renderer().defaultSize()
        #self.graphics_scene.addItem(self.svgItem)
        #self.svgItem.setPos(0, 0)

        model = system_index.model()
        icon_indexes = model.systemIcons(system_index)

        for icon_index in icon_indexes:
            icon_node   = icon_index.internalPointer()

            icon_wid = DeviceIconWidget(icon_node.svg, self.setSelection, icon_index.parent())
            proxWid = self.graphics_scene.addWidget(icon_wid)

            self._device_icons.append(icon_wid)

            x       = float(icon_node.x)
            y       = float(icon_node.y)
            rot     = float(icon_node.rotation)
            scale   = float(icon_node.scale)
            pos     = QtCore.QPointF(x,y)

            bounds   = proxWid.boundingRect()
            center_x =  bounds.width() * 0.5
            center_y =  bounds.height() * 0.5

            transform = QtGui.QTransform()

            transform.translate( x , y  )
            transform.translate( center_x , center_y  )

            transform.rotate( rot )
            transform.scale(scale,scale)
            transform.translate( -center_x , -center_y )

            proxWid.setTransform( transform )


            self._data_mappers.append(QtWidgets.QDataWidgetMapper())
            self._data_mappers[-1].setModel(model)
            self._data_mappers[-1].addMapping(icon_wid, 11, bytes('layer','ascii'))

            if icon_node.numberNode is not None:


                #TODO: remove this block
                spin = QtWidgets.QLabel('1.23 mTorr')
                #self._data_mappers[-1].addMapping(spin, 12)
                prox_spin = self.graphics_scene.addWidget(spin)

                number_x = x + float(icon_node.numberX)
                number_y = y + float(icon_node.numberY)
                transform = QtGui.QTransform()
                transform.translate( number_x , number_y)
                prox_spin.setTransform( transform )



            self._data_mappers[-1].setRootIndex(icon_index.parent().parent())
            self._data_mappers[-1].setCurrentModelIndex(icon_index.parent())
