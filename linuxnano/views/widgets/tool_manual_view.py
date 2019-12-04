#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from linuxnano.strings import strings


class ToolManualView(QtWidgets.QAbstractItemView):
    def __init__(self, parent=None):
        QtWidgets.QAbstractItemView.__init__(self, parent)

        self.graphics_scene = QtWidgets.QGraphicsScene(self)
        self.graphics_view  = QtWidgets.QGraphicsView(self)


        #UI Stuff
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.scale(1,1)

        #Layout
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(self.graphics_view)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)

        self._current_system = None
        self._device_icons = []


# work here.... XXX
# work here.... XXX
# work here.... XXX
# work here.... XXX
# work here.... XXX
# I think the device deals need to know what their device index is....


        #selection_model = QtGui.QItemSelectionModel()
        #self.setSelectionModel(selection_model)

     #   sel_1 = QtGui.QItemSelection()
     #   sel_2 = QtGui.QItemSelection()
     #   #self.selectionModel().emitSelectionChanged(sel_1,sel_2)
     #   self.selectionModel().select(sel_1)
     #   print 'cats'




    # TODO : No idea what this should do.
    def verticalOffset(self):
        return 0

    # TODO : No idea what this should do.
    def horizontalOffset(self):
        return 0






    #This abstract view needs to emit a currentChanged(
    def setSelection(self, current, old):

        current_index = current
        model = current_index.model()

        if hasattr(model, 'mapToSource'):
            current_index = model.mapToSource(current)
            model = model.sourceModel()


        node  = current_index.internalPointer()



        type_info = None
        if node is not None: type_info = node.typeInfo()


        if type_info == strings.SYSTEM_NODE:
            self._current_system = current_index
            self.displaySystem(current_index)


        elif type_info == strings.DEVICE_NODE:

            if current_index.parent() != self._current_system:
                self._current_system = current_index
                self.displaySystem(current_index.parent())

            for icon in self._device_icons:
                icon.clearSelected()
            self._device_icons[current_index.row()].setSelected()

            self.setCurrentIndex(current_index.parent())





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

        rectangle = QtGui.QGraphicsRectItem(scene_box)
        self.graphics_scene.addItem(rectangle)

        background = QtGui.QPixmap(svg_image)
        background = background.scaled(min_view_dim,min_view_dim,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        self.graphics_scene.addPixmap(background)



        model = system_index.model()
        icon_indexes = model.iconChildrenForSystem(system_index)

        for icon_index in icon_indexes:

            icon_node   = icon_index.internalPointer()
            icon_image  = icon_node.iconSVG
            self._device_icons.append( DeviceIconWidget(icon_index))


            proxWid = self.graphics_scene.addWidget(self._device_icons[-1])


            x       = float(icon_node.iconX)
            y       = float(icon_node.iconY)
            rot     = float(icon_node.iconRotation)
            scale   = float(icon_node.iconScale)
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



            self._data_mappers.append(QtGui.QDataWidgetMapper())


            self._data_mappers[-1].setModel(model)
            self._data_mappers[-1].addMapping(self._device_icons[-1], 16, bytes('current_state','ascii'))




            #TODO: remove this block
            spin = QtGui.QSpinBox()
            self._data_mappers[-1].addMapping(spin, 16)
            prox_spin = self.graphics_scene.addWidget(spin)

            x       = float(icon_node.iconX)
            y       = float(icon_node.iconY)
            transform = QtGui.QTransform()
            transform.translate( x , y  )
            prox_spin.setTransform( transform )

            #TODO : Next add thing so when click icon it selects the right thing in the treeeee
            #XXX END TEMP


            self._data_mappers[-1].setRootIndex(icon_index.parent().parent())
            self._data_mappers[-1].setCurrentModelIndex(icon_index.parent())



            self.clicked.emit(icon_index)
