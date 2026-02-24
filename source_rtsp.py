import cv2
import time
import threading
from PIL import Image
from source_base import ImageSource

class RTSPSource(ImageSource):
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.cap = None
        self._warmup_frames = 5
        self._buffer_flush_frames = 15  # Increased to flush more frames
        self._max_reconnect_attempts = 2
        self._use_threading = True  # Enable threading for better performance
        self._latest_frame = None
        self._frame_lock = threading.Lock()
        self._capture_thread = None
        self._stop_capture = False

    def connect(self):
        print(f"Connecting to RTSP feed: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        
        # Configure for minimal buffering and real-time streaming
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # Set reasonable FPS
        
        # Additional settings to reduce latency
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        
        if not self.cap.isOpened():
            raise Exception(f"Failed to open RTSP feed: {self.rtsp_url}")
            
        print("RTSP feed connected.")
        
        # Warm up and flush initial buffer
        self._flush_buffer(self._warmup_frames)
        
        # Start continuous capture thread if enabled
        if self._use_threading:
            self._start_capture_thread()
        
        print("RTSP source ready.")

    def _flush_buffer(self, num_frames):
        """Aggressively flush the buffer to get to the latest frame"""
        print(f"Flushing buffer ({num_frames} frames)...")
        for i in range(num_frames):
            ret = self.cap.grab()
            if not ret:
                print(f"Warning: Failed to grab frame {i+1} during buffer flush")
                break
        time.sleep(0.1)  # Small delay to let buffer settle

    def _start_capture_thread(self):
        """Start background thread to continuously read frames"""
        self._stop_capture = False
        self._capture_thread = threading.Thread(target=self._continuous_capture, daemon=True)
        self._capture_thread.start()
        print("Background frame capture thread started.")

    def _continuous_capture(self):
        """Continuously read frames in background to keep buffer fresh"""
        while not self._stop_capture and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self._frame_lock:
                    self._latest_frame = frame
            time.sleep(0.03)  # ~30 FPS

    def get_image(self) -> Image.Image:
        if not self.cap or not self.cap.isOpened():
            raise Exception("RTSP feed not connected")
        
        frame = None
        
        if self._use_threading and self._latest_frame is not None:
            # Use the latest frame from background thread
            with self._frame_lock:
                frame = self._latest_frame.copy() if self._latest_frame is not None else None
        
        if frame is None:
            # Fallback: aggressive buffer flushing approach
            print("Getting fresh frame with buffer flush...")
            
            # Flush buffer more aggressively to get latest frame
            self._flush_buffer(self._buffer_flush_frames)
            
            # Try multiple reads to ensure we get a good frame
            for attempt in range(self._max_reconnect_attempts):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    break
                    
                print(f"Read attempt {attempt + 1} failed, retrying...")
                time.sleep(0.1)
            
            if frame is None:
                # Last resort: reconnect and try again
                print("Frame still None, attempting reconnect...")
                self.disconnect()
                self.connect()
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    raise Exception("Failed to capture image after reconnection")

        if frame is None:
            raise Exception("Unable to capture any frame from RTSP source")

        # OpenCV uses BGR, convert to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    def disconnect(self):
        if self._use_threading and self._capture_thread:
            print("Stopping background capture thread...")
            self._stop_capture = True
            self._capture_thread.join(timeout=2.0)
            
        if self.cap:
            print("Disconnecting RTSP feed...")
            self.cap.release()
            self.cap = None
            
        with self._frame_lock:
            self._latest_frame = None
            
    def set_threading_mode(self, enable_threading=True):
        """Enable or disable background threading mode"""
        if self._use_threading != enable_threading:
            # If changing modes while connected, restart connection
            was_connected = self.cap and self.cap.isOpened()
            if was_connected:
                rtsp_url = self.rtsp_url
                self.disconnect()
                self._use_threading = enable_threading
                self.rtsp_url = rtsp_url
                self.connect()
            else:
                self._use_threading = enable_threading
            print(f"Threading mode {'enabled' if enable_threading else 'disabled'}")

    def force_buffer_flush(self):
        """Manually flush buffer - useful for debugging"""
        if self.cap and self.cap.isOpened():
            self._flush_buffer(self._buffer_flush_frames)
            print("Buffer manually flushed.")
