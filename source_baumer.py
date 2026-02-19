import neoapi
import numpy as np
from PIL import Image
from source_base import ImageSource

class BaumerSource(ImageSource):
    def __init__(self):
        self.camera = None

    def connect(self):
        print("Connecting to Baumer camera...")
        self.camera = neoapi.Cam()
        self.camera.Connect()
        print(f"Connected to: {self.camera.f.DeviceModelName.Get()} ({self.camera.f.DeviceSerialNumber.Get()})")

    def get_image(self) -> Image.Image:
        if not self.camera or not self.camera.IsConnected():
            raise Exception("Baumer camera not connected")
        
        img = self.camera.GetImage()
        if img.IsEmpty():
            return None

        # Convert to RGB8 to ensure consistent format for Pillow
        rgb_img = img.Convert("RGB8")
        img_array = rgb_img.GetNPArray()
        return Image.fromarray(img_array, mode='RGB')

    def disconnect(self):
        if self.camera and self.camera.IsConnected():
            print("Disconnecting Baumer camera...")
            self.camera.Disconnect()
