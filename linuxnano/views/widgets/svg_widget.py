# -*- coding: utf-8 -*-
from PyQt5 import QtSvg

class SVGWidget(QtSvg.QSvgWidget):
    def __init__(self, image):
        QtSvg.QSvgWidget.__init__(self, image)




#class SVGItem2(QtSvg.QGraphicsSvgItem):
#
#    def __init__(self, matrix=QtGui.QTransform()):
#        super(SVGItem2, self).__init__('/usr/local/LinuxNano/resources/icons/general/unknown.svg')
#
#        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable|
#                      QtWidgets.QGraphicsItem.ItemIsFocusable)
#
#        self.setAcceptHoverEvents(True)
#
#        self._tree_view = None
#        self._icon_layer = 'normal'
#        self._icon_layer_selected = 'normal-selected'
#        self._selected_flag = False
#
#
#        self.setElementId(self._icon_layer)
#

#
#    def setIconFile(self,file):
#        #XXX this needs some work to reduce assumptions about the svg and add error handling
#        try:
#            renderer = QtSvg.QSvgRenderer( QtCore.QLatin1String(file) )
#            self.setSharedRenderer(renderer)
#
#            tree = ET.parse(file)
#            root = tree.getroot()
#
#            self._icon_layer = root[0].attrib['id']
#            self._icon_layer_selected = root[1].attrib['id']
#            self.setElementId(self._icon_layer)
#
#            self.setFocus()
#            self.show()
#
#
#
#
#        except:
#            pass
#            #Error handling
#
#    def setDeviceIndex(self, val):
#        self._device_index = val
#
#    def setDeviceParentIndex(self, val):
#        self._device_parent_index = val
#
#    def setTreeView(self,val):
#        self._tree_view = val
#
#    def mouseReleaseEvent(self, event):
#        '''When clicked the icon needs to send a signal to its relevent scene graph that this device was clicked '''
#
#        index =  self._tree_view.currentIndex()
#
#        try:
#            self._tree_view.selectionModel().setCurrentIndex(  self._device_index,  QtGui.QItemSelectionModel.ClearAndSelect)
#            self._tree_view.expand(self._device_parent_index)
#
#        except:
#            pass
#
#
#
#
#
#    def hoverEnterEvent(self, event):
#        self._selected_flag = True
#
#        self.setElementId(self._icon_layer_selected)
#        self.show()
#
#    def hoverLeaveEvent(self, event):
#        self._selected_flag = False
#
#        self.setElementId(self._icon_layer)
#        self.show()
#
#
#
#    def layerSelected(self):
#        return self._icon_layer_selected
#
#    def setLayerSelected(self,layer):
#        self._icon_layer_selected = layer
#
#        if self._selected_flag:
#            self.setElementId(self._icon_layer_selected)
#            self.show()
#
#    def layer(self):
#        return self._icon_layer
#
#    def setLayer(self,layer):
#        self._icon_layer = layer
#
#        if not self._selected_flag:
#            self.setElementId(self._icon_layer)
#            self.show()
#
#
#    def hoverMoveEvent(self, event):
#        pass
#
#
#
#
#    #def parentWidget(self):
#    #    return self.scene().views()[0]
#
#
#    def updatePosition(self, x, y,rot, scale):
#        x       = float(x)
#        y       = float(y)
#        rot     = float(rot)
#        scale   = float(scale)
#
#        pos = QtCore.QPointF(x,y)
#
#        bounds = self.boundingRect()
#        center_x =  bounds.width() * 0.5
#        center_y =  bounds.height() * 0.5
#
#        transform = QtGui.QTransform()
#
#        transform.translate( x , y  )
#        transform.translate( center_x , center_y  )
#
#        transform.rotate( rot )
#        transform.scale(scale,scale)
#        transform.translate( -center_x , -center_y )
#
#        self.setTransform( transform )
#
#
#
