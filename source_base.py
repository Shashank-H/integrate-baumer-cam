import io
import time
from PIL import Image

class ImageSource:
    def connect(self):
        raise NotImplementedError

    def get_image(self) -> Image.Image:
        """Returns a PIL Image object"""
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError
