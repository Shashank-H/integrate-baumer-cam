import cv2
from PIL import Image
from source_base import ImageSource

class RTSPSource(ImageSource):
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self._warmup_frames = 5
        self._read_retries = 3

    def connect(self):
        print(f"Connecting to RTSP feed: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP feed: {self.rtsp_url}")
        # Drain a few frames so the next read is closer to live
        for _ in range(self._warmup_frames):
            self.cap.grab()
        print("RTSP feed connected.")

    def get_image(self) -> Image.Image:
        if not self.cap or not self.cap.isOpened():
            raise Exception("RTSP feed not connected")
        
        # RTSP feeds often buffer; grab a few frames and use the last decoded.
        frame = None
        for _ in range(self._read_retries):
            # Grab to drop buffered frames, then retrieve the most recent
            self.cap.grab()
            ret, frame = self.cap.retrieve()
            if ret and frame is not None:
                break

        if frame is None:
            # Try a reconnect once if the stream stalled
            self.disconnect()
            self.connect()
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
