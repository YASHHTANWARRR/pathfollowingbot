import cv2 
import numpy as np 
import yaml 
import os 

img_path='/home/hornet/autonomous-vehicle-/src/mobile_robot/maps/pasted_image.png'
out_path='/home/hornet/autonomous-vehicle-/src/mobile_robot/maps/'
map_name ="test_track"
resolution = 0.05  
origin = [-10.0, -10.0, 0.0]


os.makedirs(out_path, exist_ok=True)

img=cv2.imread(img_path,cv2.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError("not found image file")

#converting to black and white
_,bw = cv2.threshold(img,200,255,cv2.THRESH_BINARY)

# Invert image (Gazebo expects obstacles = black)
bw = cv2.bitwise_not(bw)

# Save processed map
map_path = os.path.join(out_path, f"{map_name}.png")
cv2.imwrite(map_path, bw)

# Create YAML file
yaml_data = {
    "image": f"{map_name}.png",
    "resolution": resolution,
    "origin": origin,
    "negate": 0,
    "occupied_thresh": 0.65,
    "free_thresh": 0.2
}

yaml_path = os.path.join(out_path, f"{map_name}.yaml")
with open(yaml_path, "w") as f:
    yaml.dump(yaml_data, f)

print("✅ Gazebo map created!")
print(f" - {map_path}")
print(f" - {yaml_path}")