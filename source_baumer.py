import neoapi
import numpy as np
from PIL import Image
from source_base import ImageSource


class BaumerSource(ImageSource):
    def __init__(self):
        self.camera = None

    def connect(self):
        print("Connecting to Baumer camera...")

        infolist = neoapi.CamInfoList.Get()  # Get the info list
        infolist.Refresh()  # Refresh the list to reflect the current status
        model = ""
        for info in infolist:
            model = info.GetModelName()
            print(
                info.GetModelName(), info.IsConnectable(), sep=" :: "
            )  # print a list of all connected cameras with its connection status

        self.camera = neoapi.Cam()
        self.camera.Connect(model)

        print("Camera connected?  ", self.camera.IsConnected())

        if self.camera.IsConnected():  # if the camera is connected
            print(self.camera.f.ExposureTime.value)  # do something with the camera

        # Read model and serial (your SDK returns them as simple attributes)
        try:
            model = self.camera.f.DeviceModelName.GetCurrent()
            serial = self.camera.f.DeviceSerialNumber.GetCurrent()
        except:
            model = "UnknownModel"
            serial = "UnknownSerial"

        print(f"Connected to: {model} ({serial})")

    def get_image(self) -> Image.Image:
        if not self.camera or not self.camera.IsConnected():
            raise Exception("Baumer camera not connected")

        # Start acquisition (same flow as your working script)
        self.camera.f.AcquisitionStart.Execute()

        img = self.camera.GetImage()  # 1s timeout

        self.camera.f.AcquisitionStop.Execute()

        if img.IsEmpty():
            return None

        # Convert to RGB8 so Pillow always works
        rgb_img = img.Convert("RGB8")

        img_array = rgb_img.GetNPArray()

        # Pillow image
        return Image.fromarray(img_array, mode="RGB")

    def disconnect(self):
        if self.camera and self.camera.IsConnected():
            print("Disconnecting Baumer camera...")
            self.camera.Disconnect()
