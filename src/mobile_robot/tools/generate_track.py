import numpy as np

WALL_LENGTH = 0.8
WALL_THICKNESS = 0.2
WALL_HEIGHT = 3.0
TRACK_HALF_WIDTH = 6
NUM_POINTS = 220

CENTERLINE_WIDTH = 0.15
CENTERLINE_HEIGHT = 0.02

t = np.linspace(0, 2*np.pi, NUM_POINTS)

# ===== CENTERLINE SHAPE =====
x = 22*np.cos(t) + 8*np.sin(2*t)
y = -35*np.sin(t)

dx = np.gradient(x)
dy = np.gradient(y)
yaw = np.arctan2(dy, dx)

norm = np.sqrt(dx**2 + dy**2)
nx = -dy / norm
ny = dx / norm

left_x  = x + TRACK_HALF_WIDTH * nx
left_y  = y + TRACK_HALF_WIDTH * ny
right_x = x - TRACK_HALF_WIDTH * nx
right_y = y - TRACK_HALF_WIDTH * ny

def wall_block(name, px, py, yaw):
    return f"""
    <link name="{name}">
      <pose>{px:.3f} {py:.3f} 0.5 0 0 {yaw:.3f}</pose>
      <collision name="c">
        <geometry>
          <box><size>{WALL_LENGTH} {WALL_THICKNESS} {WALL_HEIGHT}</size></box>
        </geometry>
      </collision>
      <visual name="v">
        <geometry>
          <box><size>{WALL_LENGTH} {WALL_THICKNESS} {WALL_HEIGHT}</size></box>
        </geometry>
      </visual>
    </link>
    """

def centerline_block(name, px, py, yaw):
    return f"""
    <link name="{name}">
      <pose>{px:.3f} {py:.3f} {CENTERLINE_HEIGHT/2:.3f} 0 0 {yaw:.3f}</pose>
      <visual name="v">
        <geometry>
          <box><size>{WALL_LENGTH} {CENTERLINE_WIDTH} {CENTERLINE_HEIGHT}</size></box>
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
        </material>
      </visual>
    </link>
    """

sdf = ['<?xml version="1.0" ?>',
        '<sdf version="1.7">',
        '<model name="track_walls">',
        '<static>true</static>']

for i in range(NUM_POINTS):
    sdf.append(wall_block(f"left_{i}", left_x[i], left_y[i], yaw[i]))
    sdf.append(wall_block(f"right_{i}", right_x[i], right_y[i], yaw[i]))
    sdf.append(centerline_block(f"center_{i}", x[i], y[i], yaw[i]))

sdf.append('</model>')
sdf.append('</sdf>')

with open("../models/track_walls/model.sdf", "w") as f:
    f.write("\n".join(sdf))

print("✅ Track + centerline generated successfully.")
