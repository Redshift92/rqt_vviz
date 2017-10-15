# -*- coding: utf-8 -*-
# @Author: lorenzo
# @Date:   2017-05-28 16:18:06
# @Last Modified by:   Lorenzo
# @Last Modified time: 2017-10-14 16:37:36

import os
import rospy
import rospkg

import json

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QImage, QPixmap, QBrush
from python_qt_binding.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem
from python_qt_binding import QtCore

from std_msgs.msg import String, Int32

import players

class Channels(QtCore.QObject):
    vehicle_create = QtCore.pyqtSignal(str, str, dict, list)
    vehicle_move   = QtCore.pyqtSignal(str, dict)
    vehicle_hide   = QtCore.pyqtSignal(str)
    vehicle_show   = QtCore.pyqtSignal(str)

    rqt_vviz_resize = QtCore.pyqtSignal(list)
    rqt_vviz_clear  = QtCore.pyqtSignal()

    road_marking_set_size   = QtCore.pyqtSignal(list, int)
    road_marking_edit_first = QtCore.pyqtSignal(str, int)

    draw_circle = QtCore.pyqtSignal(str, dict, int, str)

    remove_circle = QtCore.pyqtSignal(str)

class SubscriptionsHandler:

    def __init__(self, channels):
        self.channels = channels

    def expose(self, group, method):
        rospy.Subscriber(rospy.get_name() + '/' + group + '/' + method, String, getattr(self, group + '_' + method))

    def vehicle_create(self, msg):
        vehicle_data = json.loads(msg.data)
        self.channels.vehicle_create.emit(vehicle_data['name'], vehicle_data['type'], vehicle_data['coords'], vehicle_data['dim'])

    def vehicle_move(self, msg):
        vehicle_data = json.loads(msg.data)
        self.channels.vehicle_move.emit(vehicle_data['name'], vehicle_data['coords'])

    def vehicle_hide(self, msg):
        vehicle_data = json.loads(msg.data)
        self.channels.vehicle_hide.emit(vehicle_data['name'])

    def vehicle_show(self, msg):
        vehicle_data = json.loads(msg.data)
        self.channels.vehicle_show.emit(vehicle_data['name']) 

    def rqt_vviz_resize(self, msg):
        vviz_data = json.loads(msg.data)
        self.channels.rqt_vviz_resize.emit(vviz_data['dim'])

    def rqt_vviz_clear(self, msg):
        self.channels.rqt_vviz_clear.emit()

    def road_marking_set_size(self, msg):
        marking_data = json.loads(msg.data)
        self.channels.road_marking_set_size.emit(marking_data['dim'], marking_data['n'])

    def road_marking_edit_first(self, msg):
        marking_data = json.loads(msg.data)
        self.channels.road_marking_edit_first.emit(marking_data['color'], marking_data['percentage'])

    def draw_circle(self, msg):
        draw_data = json.loads(msg.data)
        self.channels.draw_circle.emit(draw_data['id'], draw_data['pos'], draw_data['radius'], draw_data['color'])

    def remove_circle(self, msg):
        remove_data = json.loads(msg.data)
        self.channels.remove_circle.emit(remove_data['id'])

class VehiclesVizWidget(QWidget):

    def __init__(self):
        super(QWidget, self).__init__()
        self.key_pub = rospy.Publisher(rospy.get_name() + '/keyboard', Int32, queue_size=10)

    def keyPressEvent(self, event):
        self.key_pub.publish(int(event.key()))


class VehiclesViz(Plugin):

    def __init__(self, context):
        super(VehiclesViz, self).__init__(context)
        self.setObjectName('VehiclesViz')

        self.exposed_methods = { 'vehicle': ['create', 'move', 'hide', 'show' ], 
                                 'rqt_vviz': ['resize', 'clear'], 
                                 'road_marking': ['set_size', 'edit_first'], 
                                 'draw': ['circle'], 'remove': ['circle'] 
                               }
        self._init_subs_and_channels()

        self.vehicles = {}

        self._widget = VehiclesVizWidget()
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_vviz'), 'resource', 'widget.ui')
        loadUi(ui_file, self._widget)

        self._widget.setObjectName('VehiclesViz')
        self._widget.setWindowTitle('VehiclesViz')
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))

        self._view = self._widget.findChild(QGraphicsView, 'graphicsView')
        self._view.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self._view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._view.resize(100,100)

        self._scene = QGraphicsScene()
        self._scene.setSceneRect(0,0, self._view.size().width(), self._view.size().height())
        self._view.setScene(self._scene)

        self._load_images()

        context.add_widget(self._widget)

        self.items_cache = { 'circle': {} }


    def _init_subs_and_channels(self):
        self.channels = Channels()
        self.subs_handler = SubscriptionsHandler(self.channels)
        for group, methods in self.exposed_methods.items():
            for method in methods:
                self.subs_handler.expose(group, method)
                getattr(self.channels, group + '_' + method).connect(getattr(self, 'scene_' + group + '_' + method))

    def _load_images(self):
        images_path = os.path.join(rospkg.RosPack().get_path('rqt_vviz'), 'resource', 'img')
        self.images = {}
        for img_file in os.listdir(images_path):
            self.images[img_file.split('.')[0]] = QImage(os.path.join(images_path, img_file))

    ############# scene update methods #######################

    def scene_vehicle_create(self, name, vtype, coords, width_height):
        img = self.images[vtype]
        if width_height[0] is None:
            img = img.scaledToHeight(width_height[1])
        elif width_height[1] is None:
            img = img.scaledToWidth(width_height[0])
        else:
            img = img.scaled(width_height[0], width_height[1])
        vv = players.Vehicle(name, img, coords)
        self.vehicles[name] = vv
        self._scene.addItem(vv.pixmap_item)

    def scene_vehicle_remove(self, name):
        if name in self.vehicles:
            self._scene.removeItem(self.vehicles[name].pixmap_item)
            del self.vehicles[name]

    def scene_vehicle_move(self, name, coords):
        self.vehicles[name].moveto(coords['x'], coords['y'])
        self.vehicles[name].rotate(coords['theta'])

    def scene_vehicle_hide(self, name):
        self.vehicles[name].hide()

    def scene_vehicle_show(self, name):
        self.vehicles[name].show()

    def scene_rqt_vviz_resize(self, dim):
        self._view.resize(*dim)
        self._scene.setSceneRect(0,0, self._view.size().width(), self._view.size().height())

    def scene_rqt_vviz_clear(self):
        self.scene_road_marking_remove()
        for vname, vv in self.vehicles.items():
            self.scene_vehicle_remove(vname)
        for circle_id, cc in self.items_cache['circle'].items():
            self.scene_remove_circle(circle_id)

    def scene_road_marking_set_size(self, dim, n):
        self.road_markings = []
        for i in range(1, n):
            self.road_markings.append(players.RoadMarking(dim, (self._view.size().width(), (self._view.size().height()*i) / n)))
            self.road_markings[-1].add_to_scene(self._scene)

    def scene_road_marking_edit_first(self, color, percentage):
        for marking in self.road_markings:
            marking.edit_first(color, percentage)

    def scene_road_marking_remove(self):
        if hasattr(self, 'road_markings'):
            for road_marking in self.road_markings:
                road_marking.remove_from_scene(self._scene)
            self.road_markings = []

    def scene_draw_circle(self, id, pos, radius, color):
        ellipse = QGraphicsEllipseItem(pos['x'] - radius, pos['y'] - radius, radius*2, radius*2)
        ellipse.setBrush(QBrush(getattr(QtCore.Qt, color.lower())))
        self._scene.addItem(ellipse)
        self.items_cache['circle'][id] = ellipse

    def scene_remove_circle(self, id):
        if id in self.items_cache['circle']:
            self._scene.removeItem(self.items_cache['circle'][id])
            del self.items_cache['circle'][id]

    ###########################################################

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog
