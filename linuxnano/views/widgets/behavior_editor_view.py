#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets
from linuxnano.strings import strings
import math




class BTGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.zoom = 1
        self.zoom_rate = 1.1
        self.zoom_max = 5
        self.zoom_min = 0.2

        self.setup()


    def setup(self):
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor( QtWidgets.QGraphicsView.AnchorUnderMouse)



    def wheelEvent(self, event):
        old_pos = self.mapToScene(event.pos())

        #zoom
        if event.angleDelta().y() > 0:
            if (self.zoom * self.zoom_rate) < self.zoom_max:
                self.zoom *= self.zoom_rate
                self.scale(self.zoom_rate, self.zoom_rate)

        else:
            if (self.zoom / self.zoom_rate) > self.zoom_min:
                self.zoom /= self.zoom_rate
                self.scale(1/self.zoom_rate, 1/self.zoom_rate)

        #translate so we zoom where the mouse is
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())







class BTGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        # settings
        self.scene_width, self.scene_height = 64000, 64000
        self.setSceneRect(-self.scene_width//2, -self.scene_height//2, self.scene_width, self.scene_height)

        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QtGui.QColor("#393939")
        self._color_light = QtGui.QColor("#2f2f2f")
        self._color_dark = QtGui.QColor("#292929")

        self._pen_light = QtGui.QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QtGui.QPen(self._color_dark)
        self._pen_dark.setWidth(2)
        self.setBackgroundBrush(self._color_background)


    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QtCore.QLine(x, top, x, bottom))
            else: lines_dark.append(QtCore.QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QtCore.QLine(left, y, right, y))
            else: lines_dark.append(QtCore.QLine(left, y, right, y))


        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)





class BTEditor(QtWidgets.QAbstractItemView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._scene = BTGraphicsScene(self)
        self._model = None

        #UI Stuff
        self._view = BTGraphicsView()
        self._view.setScene(self._scene)
        #self._view.scale(1, 1)


        #Layout
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.addWidget(self._view)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)


        self._scene_items = []  #[(index, item),(index2, item2)]
        self._paths = []

        self._from_callback = False






    def setModel(self, model):
        super().setModel(model)

        root_index =  self.model().index(0, 0, QtCore.QModelIndex())
        self.addNodeItem(root_index)

        print(root_index.internalPointer().typeInfo())


        for row in range(self.model().rowCount(root_index)):
            index = root_index.child(row, 0)
            self.addNodeItem(index)
            self._recurseAdd(index)

    def _recurseAdd(self, parent_index):
        for row in range(self.model().rowCount(parent_index)):
            index = parent_index.child(row, 0)
            self.addNodeItem(index)
            self._recurseAdd(index)

    def setData(self, index, value):
        self._from_callback = True
        self.model().setData(index, value)


    def addNodeItem(self, index):

        if index.internalPointer().typeInfo() == strings.WAIT_TIME_NODE:
            item = WaitTimeTestGraphicsItem(index.internalPointer().typeInfo())
            item.setIndexWaitTime(index.siblingAtColumn(10))
        else:
            item = TestGraphicsItem(index.internalPointer().typeInfo())

        item.setIndexXPos(index.siblingAtColumn(1))
        item.setIndexYPos(index.siblingAtColumn(2))


        item.setCallback(self.setData)

        self._scene.addItem(item)
        self._scene_items.append((index, item))

        self.updateNodeItem(index)


        #Deal with the lines between nodes
        if index.parent().internalPointer():
            items = [itemm for itemm in self._scene_items if itemm[0] == index.parent()] # Returns list of all tuples that match
            parent_item = items[0][1]


            new_path = Path(parent_item.centerBottomPos(), item.centerTopPos())
            self._scene.addItem(new_path)

            item.addLine(new_path, 1)
            parent_item.addLine(new_path, 0)







    def updateNodeItem(self, index):
        if not self._from_callback:
            #Find the graphics item that has to do with this index
            index = index.siblingAtColumn(0)
            items = [item for item in self._scene_items if item[0] == index] # Returns list of all tuples that match
            graphics_item = items[0][1] #The graphics item is the second thing in the tuple

            #Get the data
            node = index.internalPointer()
            x, y = node.x_pos, node.y_pos

            #Update the graphics item
            graphics_item.setPos(node.x_pos, node.y_pos )
            graphics_item.updateLines()

            if node.typeInfo() == strings.WAIT_TIME_NODE:
                graphics_item.setWaitTime(node.wait_time)

        self._from_callback = False










    def dataChanged(self, index_top_left, index_bottom_right, roles):
        self.updateNodeItem(index_top_left)




    def display_items(self):
        '''Next we need to start connecting the model to the graphics scene!
           Maybe draw a rectangle per item?
           Also get it to save and load the rectangles position
         '''
        self._scene.clear()

        self._device_icons = []


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






















    def add_stuff(self):


        widget1 = QtWidgets.QPushButton("Hello World")
        proxy1 = self._scene.addWidget(widget1)
        proxy1.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        proxy1.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)



        x, y = 0, 0
        width, height = 200, 100
        brush = QtGui.QBrush(QtCore.Qt.gray)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)

        rect1 = self._scene.addRect(x, y, width, height, pen, brush)
        rect2 = self._scene.addRect(x+100, y+100, width, height, pen, brush)
        rect1.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        rect2.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)





    # TODO : We have to have these methods but aren't currently doing anything with them
    def visualRegionForSelection(self, selection):
        return QtGui.QRegion()

    def scrollTo(self, index, hint):
        return

    def visualRect(self, index):
        return QtCore.QRect()

    def verticalOffset(self):
        return 0

    def horizontalOffset(self):
        return 0

    def moveCursor(self, action, modifier):
        return QtCore.QModelIndex()





class Path(QtWidgets.QGraphicsPathItem):
    def __init__(self, start_pos, end_pos):
        super().__init__()
        self._start_pos = start_pos
        self._end_pos = end_pos

        self.setPen(QtGui.QPen(QtCore.Qt.red, 1.75))
        self.updateElements()


    def startPos(self):
        return self._start_pos

    def setStartPos(self, pos):
        self._start_pos = pos
        self.updateElements()

    def endPos(self):
        return self._end_pos

    def setEndPos(self, pos):
        self._end_pos = pos
        self.updateElements()


    def minChildY(self):
        return self._start_pos.y() + 80

    def updateElements(self):
        start = self._start_pos
        end = self._end_pos

        d = 20 #Diameter of chamfer
        drop = 40 #fixed verticle drop

        path = QtGui.QPainterPath()
        path.moveTo(start)
        path.lineTo(start.x(), start.y() + drop)
        d = min(d, abs(start.x()-end.x()))

        if end.x() > start.x():
            path.lineTo(end.x()-d, start.y() + drop)
            path.arcTo(end.x()-d, start.y() + drop, d, d, 90, -90)

        elif end.x() < start.x():
            path.lineTo(end.x()+d, start.y()+drop)
            path.arcTo( end.x()  , start.y()+drop, d, d, -270, 90)

        else:
            path.lineTo(end.x(), start.y() + drop)

        path.lineTo(end)
        self.setPath(path)






class TestGraphicsItem(QtWidgets.QGraphicsItem):
    def __init__(self, type):
        super().__init__()
        # init our flags
        self._type = type

        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False
        self._index = None

        self._callback = None
        self._index_x_pos = None
        self._index_y_pos = None

        self._lines = []

        self.initSizes()
        self.initAssets()
        self.initUI()
        self.initTitle()


        #if self._type == strings.WAIT_TIME_NODE:
        #    self._wait_time = 238
        #    self.initWaitTime()

    def centerTopPos(self):
        return QtCore.QPoint(self.x() + self.width*0.5, self.y())

    def centerBottomPos(self):
        return QtCore.QPoint(self.x() + self.width*0.5, self.y() + self.height)

    def setCallback(self, value):
        self._callback = value

    def setIndexXPos(self, value):
        self._index_x_pos = value

    def setIndexYPos(self, value):
        self._index_y_pos = value


    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

        self.setAcceptHoverEvents(True)



    def initTitle(self):
        self.title_item = QtWidgets.QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setFont(self._title_font)
        self.title_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)
        self.title_item.setPlainText(self._type)



    def initSizes(self):
        """Set up internal attributes like `width`, `height`, etc."""
        self.width = 200
        self.height = 100
        self.edge_roundness = 10.0
        self.edge_padding = 10.0
        self.title_height = 24.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._title_color = QtCore.Qt.white
        self._title_font = QtGui.QFont("Ubuntu", 10)
        self._title_font2 = QtGui.QFont("Ubuntu", 20)

        self._color = QtGui.QColor("#7F000000")
        self._color_selected = QtGui.QColor("#FFFFA637")
        self._color_hovered = QtGui.QColor("#FF37A6FF")

        self._pen_default = QtGui.QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QtGui.QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QtGui.QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)

        self._brush_title = QtGui.QBrush(QtGui.QColor("#FF313131"))
        self._brush_background = QtGui.QBrush(QtGui.QColor("#E3212121"))


    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width, self.height).normalized()


    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Painting the rounded rectanglar `Node`"""
        r = 10 #radius of edge
        # title
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, r, r)
        path_title.addRect(0, self.title_height - r, r,r)
        path_title.addRect(self.width - r, self.title_height - r, r, r)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())
#
#
        # content
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, r, r)
        path_content.addRect(0, self.title_height, r, r)
        path_content.addRect(self.width - r, self.title_height, r, r)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())


        # outline
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width+2, self.height+2, r, r)
        painter.setBrush(QtCore.Qt.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())


    #def x_pos(self):
    #    self.x()


    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._temp_pos = self.pos()


    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.pos() != self._temp_pos:
            self._callback(self._index_x_pos, self.x())
            self._callback(self._index_y_pos, self.y())

    def updateLines(self):
        #Move all the lines
        for line in self._lines:
            o, index = line[0], line[1]

            if index == 0:
                o.setStartPos(self.centerBottomPos())
            else:
                o.setEndPos(self.centerTopPos())
                min_y = o.minChildY()


    def itemChange(self, change, value):
        min_y = -32000
        
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            self.updateLines()

            #Prevent it from going above it's parent
            if value.y() < min_y:
                return QtCore.QPointF(value.x(), min_y)

        return super().itemChange(change, value)

    def addLine(self, line, pt_index):
        self._lines.append((line, pt_index))


class WaitTimeTestGraphicsItem(TestGraphicsItem):
    def __init__(self, type):
        super().__init__(type)

        self._wait_time = 0.0
        self.initWaitTime()

    def setIndexWaitTime(self, value):
        self._index_wait_time = value

    def initWaitTime(self):
        self.wait_time_item = QtWidgets.QGraphicsTextItem(self)
        self.wait_time_item.setDefaultTextColor(self._title_color)
        self.wait_time_item.setFont(self._title_font2)
        self.wait_time_item.setTextWidth(self.width - 2 * self.title_horizontal_padding)
        self.wait_time_item.setPlainText(str(self._wait_time) + ' sec')

        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        self.wait_time_item.document().setDefaultTextOption(option)
        self.wait_time_item.setPos(self.title_horizontal_padding, self.height*0.4)

        #self.wait_time_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)


    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)

        num,ok = QtWidgets.QInputDialog.getDouble(None,"Set Time","Wait Time (sec)", self._wait_time, 0, 3600, 1)
        if ok:
            print(num)
            self.setWaitTime(num)
            self._callback(self._index_wait_time, self._wait_time)

    def setWaitTime(self, value):
        self._wait_time = value
        self.wait_time_item.setPlainText(str(self._wait_time) + ' sec')
