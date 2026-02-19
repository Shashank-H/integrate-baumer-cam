import cv2
from PIL import Image
from source_base import ImageSource

class RTSPSource(ImageSource):
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None

    def connect(self):
        print(f"Connecting to RTSP feed: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP feed: {self.rtsp_url}")
        print("RTSP feed connected.")

    def get_image(self) -> Image.Image:
        if not self.cap or not self.cap.isOpened():
            raise Exception("RTSP feed not connected")
        
        # RTSP feeds often have buffers; for a single capture, 
        # we might want the most recent frame. 
        # This simple implementation takes the next frame.
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None

        # OpenCV uses BGR, convert to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    def disconnect(self):
        if self.cap:
            print("Disconnecting RTSP feed...")
            self.cap.release()
