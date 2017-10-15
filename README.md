rqt_vviz
========

ROS rqt plugin to visualize 2D vehicles.

![2D vehicles on the road](https://raw.githubusercontent.com/Redshift92/rqt_vviz/master/screens/vviz.gif)

### Usage:

Launch multiple visualizer instances specifying `n` parameter:

    roslaunch rqt_vviz rqt_vviz.launch n:=2

Several command topics will be open to interact with the visualizer, each topic exposing a specific function and accepting JSON strings.
One topic will be open publishing.

##### Command Topics:

**/rqt_vviz/**  namespace will be repaced by **/rqt_vviz_0/**, **/rqt_vviz_1/**, ..., **/rqt_vviz_n/** in case of multiple visualizer instances.

 - ###### visualizer functions:
   ```
    /rqt_vviz/rqt_vviz/clear
   ``` 
   send an empty string to clear visualizer screen
   ```
    /rqt_vviz/rqt_vviz/resize
   ```
   send `{ "dim": [x_dim, y_dim] }` to set visualizer size (pixels)

 - ###### vehicle functions:

   ```
    /rqt_vviz/vehicle/create
   ```
   send
   ```
   {
      "type": "vehicle_type",
      "name": "vehicle_identifier", 
      "dim": [x_dim, y_dim], 
      "coords": { "x": x, "y": y, "theta": theta}
   }
    ```
    to create a new vehicle 
     -  of type `"vehicle_type"` (can be one in `[ "car", "roomba", "truck" ]`), 
     - with name `"vehicle_identifier"` (must be unique)
     - dimensions `[x_dim, y_dim]` (pixels)
     - placed at point `x,y` with orientation `theta` (pixels, pixels, degrees)

   ```
    /rqt_vviz/vehicle/move
   ```
   send
   ```
   {
      "name": "vehicle_identifier", 
      "coords": { "x": x, "y": y, "theta": theta}
   }
    ```
    to move vehicle 
     - with name `"vehicle_identifier"`
     - to point point `x,y` with orientation `theta` (pixels, pixels, degrees)

   ```
    /rqt_vviz/vehicle/hide
   ```
   send `{ "name": "vehicle_identifier" }` to hide vehicle `vehicle_identifier`

   ```
    /rqt_vviz/vehicle/show
   ```
   send `{ "name": "vehicle_identifier" }` to show vehicle `vehicle_identifier`
    
 - ###### road marking functions:

   ```
    /rqt_vviz/road_marking/set_size
   ```
   send `{ "dim": [x_dim, y_dim], "n": n }` to create road markings with `[x_dim, y_dim]` size (pixels) separating `n` road lanes

   ```
    /rqt_vviz/road_marking/edit_first
   ```
   send `{ "color": color, "percentage": percentage }` to select first visible road marking as one with color `color` (`'white'` or `'black'`) and a visible portion of percentage `percentage`

 - ###### generic items functions:

   ```
    /rqt_vviz/draw/circle
   ```
   send
   ```
   {
      "id": "circle_identifier",
      "pos": [x, y], 
      "radius": radius, 
      "color": color
   }
    ```
    to draw a circle with id `circle_identifier` of color `color`, placed at `[x, y]` (pixels) and radius `radius` (pixels)

   ```
    /rqt_vviz/remove/circle
   ```
   send `{ "id": circle_identifier }` to remove circle with id `circle_identifier`.

##### Publishing Topics:

Subscribe to
```
 /rqt_vviz/keyboard
```
to receive Qt Keyboard events, listened by the GUI, as Int32 QtCodes.


###### This project is licensed under the terms of the MIT license.