import os
import io
import time
import requests
import neoapi
import numpy as np
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL")
IMAGE_FIELD_NAME = os.getenv("IMAGE_FIELD_NAME", "file")
IMAGES_SAVE_PATH = os.getenv("IMAGES_SAVE_PATH", "./images")

def capture_and_send(camera):
    try:
        print("Capturing image...")
        # Get image from camera
        img = camera.GetImage()
        if img.IsEmpty():
            print("Captured image is empty.")
            return

        # Convert to RGB8 to ensure consistent format for Pillow
        rgb_img = img.Convert("RGB8")
        img_array = rgb_img.GetNPArray()
        
        # Convert numpy array to PIL Image
        pil_img = Image.fromarray(img_array, mode='RGB')

        # Always prepare the WebP buffer for high quality
        buffer = io.BytesIO()
        pil_img.save(buffer, format="WEBP", quality=100, lossless=True)
        image_data = buffer.getvalue()

        # Generate a timestamped filename for local saving
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"capture_{timestamp}.webp"
        
        # Ensure save directory exists
        os.makedirs(IMAGES_SAVE_PATH, exist_ok=True)
        local_path = os.path.join(IMAGES_SAVE_PATH, filename)

        # Save locally by default
        with open(local_path, "wb") as f:
            f.write(image_data)
        print(f"Image saved locally to: {local_path}")

        # If API_URL is provided, also send it
        if API_URL:
            print(f"Sending image to {API_URL}...")
            files = {IMAGE_FIELD_NAME: (filename, image_data, "image/webp")}
            try:
                response = requests.post(API_URL, files=files, timeout=30)
                if 200 <= response.status_code < 300:
                    print(f"Successfully sent image. Response: {response.status_code}")
                else:
                    print(f"Failed to send image. Status code: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as api_err:
                print(f"API call failed: {api_err}")
        else:
            print("No API_URL configured, skipping upload.")

    except Exception as e:
        print(f"Error during capture process: {e}")

def main():
    camera = None
    try:
        print("Connecting to camera...")
        camera = neoapi.Cam()
        camera.Connect()
        print(f"Connected to: {camera.f.DeviceModelName.Get()} ({camera.f.DeviceSerialNumber.Get()})")

        print("\nReady.")
        while True:
            user_input = input("Enter 'c' to capture, 'x' to exit: ").strip().lower()
            if user_input == 'c':
                capture_and_send(camera)
            elif user_input == 'x':
                print("Exiting...")
                break
            elif user_input == '':
                continue
            else:
                print(f"Unknown command: '{user_input}'")

    except neoapi.NeoException as e:
        print(f"NeoAPI Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        if camera and camera.IsConnected():
            print("Disconnecting camera...")
            camera.Disconnect()

if __name__ == "__main__":
    main()
