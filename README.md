# Integrate Baumer Cam

A modular Python utility to capture high-quality images from Baumer industrial cameras (via NeoAPI) or RTSP feeds, convert them to lossless WebP, and submit them to a headless inspection API.

## Prerequisites

- **Python**: 3.10 or higher.
- **uv**: Recommended for dependency management.
- **Baumer Camera Drivers**: Ensure the Baumer SDK/drivers are installed if using a physical camera.
- **RTSP Feed**: Ensure the URL is accessible if using the RTSP source.

## Setup

1. **Install Dependencies**:
   The project uses `uv` for fast, reproducible environments.
   ```bash
   uv sync
   ```
   *Note: This will automatically install the local Baumer NeoAPI wheel located in `libs/`.*

2. **Configure Environment**:
   Copy the example environment file and fill in your specific API keys, workspace IDs, and source details.
   ```bash
   cp .env.example .env
   ```

3. **Camera Permissions (Linux)**:
   If using a Baumer USB camera, ensure your user has permissions:
   ```bash
   sudo cp libs/99-baumer-cameras.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

## Usage

Run the application using `uv`:

```bash
uv run python main.py
```

### Controls
- Type `c` and press **Enter** to capture an image and trigger the API call.
- Type `x` and press **Enter** to safely disconnect the camera/feed and exit.

### Features
- **Modular Sources**: Switch between `baumer` and `rtsp` in `.env`.
- **High Quality**: Captures are converted to **Lossless WebP** to preserve maximum detail for inspection.
- **Local Backup**: Every capture is saved locally in the `images/` folder (configured in `.env`).
- **Headless API**: Automates multipart form-data submission with custom headers.

## Directory Structure
- `main.py`: Entry point and orchestration logic.
- `source_*.py`: Modular implementations for different image sources.
- `libs/`: Contains the Baumer NeoAPI wheel for offline installation.
- `images/`: Local storage for captures (gitignored).
