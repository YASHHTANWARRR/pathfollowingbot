import numpy as np
import cv2 
import math 

img_path='/home/hornet/autonomous-vehicle-/src/mobile_robot/maps/pasted_image.png'

reso=0.05
wall_height=1.0
wall_thick=0.15

img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
_, bw=cv2.threshold(img,200,255,cv2.THRESH_BINARY)


contours, _=cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

def px_to_m(x, y):
    return x * reso, y * reso

print('<?xml version="1.0"?>')
print('<sdf version="1.7">')
print('<model name="track_walls">')
print('<static>true</static>')

wall_id = 0

for contour in contours:
    for i in range(len(contour)-1):
        x1, y1 = contour[i][0]
        x2, y2 = contour[i+1][0]

        mx1, my1 = px_to_m(x1, y1)
        mx2, my2 = px_to_m(x2, y2)

        dx = mx2 - mx1
        dy = my2 - my1
        length = math.hypot(dx, dy)
        yaw = math.atan2(dy, dx)

        cx = (mx1 + mx2) / 2
        cy = (my1 + my2) / 2

        print(f'''
    <link name="wall_{wall_id}">
        <pose>{cx} {cy} {wall_height/2} 0 0 {yaw}</pose>
        <collision name="collision">
        <geometry>
            <box>
            <size>{length} {wall_thick} {wall_height}</size>
            </box>
        </geometry>
        </collision>
        <visual name="visual">
        <geometry>
            <box>
            <size>{length} {wall_thick} {wall_height}</size>
            </box>
        </geometry>
        </visual>
    </link>
        ''')
        wall_id += 1

print('</model>')
print('</sdf>')
