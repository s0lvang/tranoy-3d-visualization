# Trame Web Viewer

This application uses Trame to host your PyVista visualization in a web browser.

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using the shell script
```bash
chmod +x run_trame.sh
./run_trame.sh
```

### Option 2: Manual start
```bash
source venv/bin/activate
python trame_app.py
```

## Accessing the Viewer

Once the server starts, open your browser and navigate to:
- Local: http://localhost:8080
- Network: http://0.0.0.0:8080 (accessible from other devices on your network)

## Features

- Interactive 3D terrain visualization
- OSM buildings and roads overlay
- Proposed house visualization
- Viewpoint marker (red sphere)
- Reset camera button
- Full mouse controls:
  - Left click + drag: Rotate
  - Middle click + drag: Pan
  - Scroll: Zoom
  - Right click: Context menu

## Architecture

The trame application:
- Uses your existing `viz.py`, `dtm.py`, `osm.py`, and `horizon.py` modules
- Creates a PyVista plotter with all meshes
- Serves it through a Vue3-based web interface
- Runs on port 8080 by default

## Customization

Edit `trame_app.py` to:
- Change the port (line 92)
- Modify UI layout
- Add additional controls
- Change camera settings
