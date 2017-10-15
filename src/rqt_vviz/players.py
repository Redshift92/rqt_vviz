# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-05-28 21:39:51
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-14 15:39:00

from python_qt_binding.QtGui import QPixmap, QTransform, QPen, QBrush
from python_qt_binding.QtWidgets import QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsRectItem
from python_qt_binding import QtCore

class Vehicle:

    def __init__(self, name, img, coords):
        self.name  = name
        self.cur_coords = {}

        self.visible = True

        self.pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(img))

        bd = self.pixmap_item.boundingRect()
        self.pixmap_item.setTransformOriginPoint(bd.center())

        self.cur_coords['theta'] = coords['theta']
        self.pixmap_item.setRotation(coords['theta'])

        self.cur_coords['xy'] = (coords['x'], coords['y'])
        self.pixmap_item.setPos(coords['x'] - bd.width()/2, coords['y'] - bd.height()/2)

        self.img = img

    def moveto(self, x, y):
        if self.cur_coords['xy'] != (x,y):
            bd = self.pixmap_item.boundingRect()
            self.pixmap_item.setPos(x - bd.width()/2, y - bd.height()/2)
            self.cur_coords['xy'] = (x,y)

    def rotate(self, theta):
        if (self.cur_coords['theta'] != theta):
            self.cur_coords['theta'] = theta
            self.pixmap_item.setRotation(theta)

    def hide(self):
        if self.visible:
            self.pixmap_item.hide()
            self.visible = False

    def show(self):
        if not self.visible:
            self.pixmap_item.show()
            self.visible = True

class RoadMarking:

    def __init__(self, mark_dim, view_dim):
        self.mark_dim  = mark_dim
        self.view_dim  = view_dim

        self._pens =    {'black': QPen(QtCore.Qt.black), 'white': QPen(QtCore.Qt.white)}
        self._brushes = {'black': QBrush(QtCore.Qt.black), 'white': QBrush(QtCore.Qt.white)}
        self._prepare()

    def _prepare(self):
        self._groups = { 'black': QGraphicsItemGroup(), 'white': QGraphicsItemGroup()}
        for start_color in ['black', 'white']:
            self._groups[start_color].setZValue(-1)
            current_color = start_color
            current_marking_end = 0
            while current_marking_end < self.view_dim[0] + self.mark_dim[0]*2:
                rect = QGraphicsRectItem(current_marking_end, self.view_dim[1], self.mark_dim[0], self.mark_dim[1])
                rect.setBrush(self._brushes[current_color])
                rect.setPen(self._pens[current_color])
                rect.setParentItem(self._groups[start_color])
                current_marking_end += self.mark_dim[0]
                current_color = ('white' if current_color == 'black' else 'black')
            self._groups[start_color].hide()

    def add_to_scene(self, scene):
        for col in ['black', 'white']:
            scene.addItem(self._groups[col])

    def remove_from_scene(self, scene):
        for col in ['black', 'white']:
            scene.removeItem(self._groups[col])

    def edit_first(self, color, percentage):
        self._groups[color].show()
        self._groups[('black' if color == 'white' else 'white')].hide()
        self._groups[color].setX(- self.mark_dim[0] * (float(100 - percentage) / 100))

