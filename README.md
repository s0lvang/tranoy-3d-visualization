---
title: Tranøy Map 3D Terrain Viewer
emoji: 🗺️
colorFrom: green
colorTo: blue
sdk: docker
app_file: trame_app.py
pinned: false
---

# Tranøy Map 3D Terrain Viewer

Interactive 3D terrain visualization tool for analyzing horizon profiles and view obstruction from proposed buildings. Built with PyVista and Trame for web-based visualization.

## Features

- **3D Terrain Visualization**: High-resolution DTM (Digital Terrain Model) rendering with elevation colormap
- **OSM Integration**: Automatically fetches and displays buildings and roads from OpenStreetMap
- **Horizon Analysis**: Computes horizon profiles from a viewpoint and calculates view obstruction
- **Proposed Building Visualization**: Shows impact of new structures on the landscape
- **Interactive Web Interface**: Full mouse controls (rotate, pan, zoom) in the browser
- **Solid Angle Calculation**: Quantifies blocked view using spherical geometry

## Live Demo

[Deploy to Hugging Face Spaces](#deployment-to-hugging-face-spaces) for instant web hosting.

## Local Installation

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)

### Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Run Web Viewer

```bash
python trame_app.py
```

Then open http://localhost:8080 in your browser.

### Run CLI Analysis

```bash
python main.py
```

This will:
1. Fetch DTM data for the configured area
2. Compute horizon profiles with and without the proposed building
3. Display 3D visualization
4. Show polar plot of horizon angles

## Configuration

Edit `config.py` to customize:

```python
Config(
    viewpoint=(easting, northing),          # Observer position (EPSG:25833)
    house_polygon=[...],                     # Building footprint coordinates
    center_xyz=(x, y, z),                    # Camera focus point
    house_base_elevation=21.0,               # Ground level (meters)
    house_height=5.5,                        # Building height (meters)
    eye_height=1.6,                          # Observer eye height
    analysis_radius=50,                      # Analysis distance (meters)
    azimuth_step=0.5,                        # Horizon sampling resolution
    dtm_resolution=1.0,                      # Terrain grid resolution
    koordsys=25833,                          # Coordinate system (EPSG code)
)
```

## Deployment to Hugging Face Spaces

### Quick Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Space**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Select **Docker** as SDK
   - Link your GitHub repository

3. **Auto-Deploy**
   - Hugging Face automatically builds and deploys
   - Access at `https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME`

### Environment Variables

If using external APIs that require authentication, add secrets in HF Spaces settings:
- Go to Space Settings → Repository secrets
- Add required API keys

## Project Structure

```
.
├── config.py           # Configuration and example scenarios
├── dtm.py             # DTM data fetching from elevation APIs
├── horizon.py         # Horizon profile computation and ray tracing
├── osm.py             # OpenStreetMap data fetching
├── viz.py             # Mesh building and visualization functions
├── main.py            # CLI entry point
├── trame_app.py       # Web application server
├── requirements.txt   # Python dependencies
└── Dockerfile         # Container configuration for deployment
```

## How It Works

1. **Terrain Acquisition**: Fetches elevation data from Norwegian mapping services
2. **OSM Data**: Retrieves nearby buildings and roads for context
3. **Mesh Construction**: Converts terrain and structures into 3D meshes
4. **Horizon Tracing**: Raycast in all azimuths to find maximum elevation angles
5. **Obstruction Analysis**: Compares horizon profiles with/without proposed building
6. **Visualization**: Renders interactive 3D scene in web browser

## Analysis Output

The tool computes:
- **Max horizon angle increase**: Peak obstruction in degrees
- **Mean horizon angle increase**: Average impact across all azimuths
- **Blocked solid angle**: View obstruction in steradians (sr)

## Technologies

- **PyVista**: 3D visualization and mesh processing
- **Trame**: Web framework for scientific visualization
- **Rasterio**: Geospatial raster data handling
- **Shapely**: Geometric operations and ray intersection
- **NumPy/SciPy**: Numerical computations
- **Matplotlib**: Polar horizon profile plots

## Browser Support

Modern browsers with WebGL support:
- Chrome/Edge (recommended)
- Firefox
- Safari

## Performance Notes

- Initial load time depends on DTM resolution and analysis radius
- Larger terrain areas require more memory
- Consider caching computed meshes for repeated views

## License

MIT

## Contributing

Issues and pull requests welcome!

## Acknowledgments

- DTM data from Norwegian mapping authorities
- Building/road data from OpenStreetMap contributors
