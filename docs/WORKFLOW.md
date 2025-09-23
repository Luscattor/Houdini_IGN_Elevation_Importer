# Detailed Workflow Guide

This document provides a comprehensive guide for using the IGN Elevation Map Importer in professional production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Data Acquisition](#data-acquisition)
3. [Download Process](#download-process)
4. [Houdini Integration](#houdini-integration)
5. [Advanced Usage](#advanced-usage)
6. [Production Tips](#production-tips)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Software Requirements
- **Python 3.7+** with standard libraries
- **SideFX Houdini 19.0+** (tested with 19.5, 20.0)
- **Internet connection** for downloading tiles
- **Web browser** for IGN Géoportail interface

### System Requirements
- **Disk Space**: ~5-50MB per tile (depending on resolution)
- **RAM**: 2GB+ recommended for large datasets
- **Network**: Stable connection for bulk downloads

## Data Acquisition

### Step 1: Access IGN LiDAR HD Portal

1. Navigate to [https://diffusion-lidarhd.ign.fr/mnx/](https://diffusion-lidarhd.ign.fr/mnx/)
2. **Select the correct data type**:
   - **MNT** (Modèle Numérique de Terrain) - ✅ **RECOMMENDED** - Bare ground elevation
   - MNS (Modèle Numérique de Surface) - Surface with vegetation and buildings
   - MNH (Modèle Numérique de Hauteur) - Height above ground
3. Use the search function or navigate to your area of interest

### Step 2: Define Your Area

1. **Zoom Level**: Use appropriate zoom for your needs
   - Higher zoom = more detailed tiles = more downloads
   - Consider your project's LOD requirements

2. **Area Selection**:
   - Use polygon selection tools if available
   - Note the coordinate bounds for reference

### Step 3: Export Tile URLs

1. Open browser developer tools (F12)
2. Navigate to Network tab
3. Filter by "wms" or search for "data.geopf.fr"
4. Pan/zoom in your area to trigger tile requests
5. Right-click on tile requests → "Copy as cURL" or copy URL
6. Save URLs to a `.txt` file (one URL per line)

**Example URL structure:**
```
https://data.geopf.fr/wms-r/LHD_FXX_0957_6218_MNT_O_0M50_LAMB93_IGN69.tif?SERVICE=WMS&VERSION=1.3.0&EXCEPTIONS=text/xml&REQUEST=GetMap&LAYERS=IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93&FORMAT=image/geotiff&STYLES=&CRS=EPSG:2154&BBOX=956999.75,6217000.25,957999.75,6218000.25&WIDTH=2000&HEIGHT=2000&FILENAME=LHD_FXX_0957_6218_MNT_O_0M50_LAMB93_IGN69.tif
```

## Download Process

### Configuration

Edit `src/ign_downloader.py` configuration:

```python
CONFIG = {
    # Input file containing tile URLs
    "TXT_SOURCE": "examples/sample_tiles.txt",

    # Output directory for downloaded tiles
    "DOWNLOAD_DIR": "elevation_data",

    # JSON metadata file for Houdini
    "METADATA_FILE": "tiles_metadata.json",

    # Network settings
    "HTTP_TIMEOUT": 60,      # Timeout per download (seconds)
    "HTTP_RETRIES": 2,       # Retry attempts for failed downloads

    # HTTP headers
    "USER_AGENT": "IGN-MNT-Downloader/1.0 (Python urllib)",

    # Logging
    "VERBOSE": True,         # Enable detailed output
}
```

### Execution

```bash
# Basic usage
python src/ign_downloader.py

# With custom configuration
python src/ign_downloader.py --config my_config.py
```

### Output Structure

```
elevation_data/
├── tiles_metadata.json                    # Houdini-ready metadata
├── LHD_FXX_0957_6218_MNT_O_0M50_*.tif    # Downloaded elevation tiles
├── LHD_FXX_0958_6217_MNT_O_0M50_*.tif
└── ...
```

## Houdini Integration

### Step 1: Scene Setup

1. Create new Houdini scene
2. Add a **Geometry** node
3. Inside the Geometry node, add a **Python SOP**

### Step 2: Python SOP Configuration

1. Copy contents of `src/houdini_python.py` into the Python SOP
2. Update the JSON file path:
   ```python
   json_file_path = "F:/your/path/to/tiles_metadata.json"
   ```
3. Execute the node

### Step 3: Verify Import

After execution, you should see:
- **Points**: One per tile, positioned at tile centers
- **Attributes**: Complete tile metadata as point attributes
- **Console Output**: Confirmation of loaded tiles

### Generated Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `tile_index` | int | Sequential tile number | `0, 1, 2...` |
| `url` | string | Original download URL | `"https://data.geopf.fr/..."` |
| `local_name` | string | Tile filename | `"LHD_FXX_0957_6218_*.tif"` |
| `local_path` | string | Absolute file path | `"F:/data/tile.tif"` |
| `minx, miny` | float | Tile bottom-left coords | `956999.75, 6217000.25` |
| `maxx, maxy` | float | Tile top-right coords | `957999.75, 6218000.25` |
| `width_m, height_m` | float | Physical dimensions (m) | `1000.0, 1000.0` |
| `width_px, height_px` | int | Pixel dimensions | `2000, 2000` |
| `crs` | string | Coordinate system | `"EPSG:2154"` |

## Advanced Usage

### Batch Processing Multiple Regions

For large projects spanning multiple regions:

```python
# Create region-specific configs
configs = [
    {"TXT_SOURCE": "region_north.txt", "DOWNLOAD_DIR": "north_tiles"},
    {"TXT_SOURCE": "region_south.txt", "DOWNLOAD_DIR": "south_tiles"},
]

for config in configs:
    # Update CONFIG dictionary
    # Run downloader
```

### Custom Coordinate Systems

The tool automatically detects CRS from tile URLs. Supported formats:
- **EPSG:2154** (Lambert-93) - Default for France
- **EPSG:4326** (WGS84) - Global geographic
- **EPSG:3857** (Web Mercator) - Web mapping

### Memory Optimization

For large datasets (100+ tiles):

```python
# Process in chunks
def process_tiles_in_chunks(tiles, chunk_size=50):
    for i in range(0, len(tiles), chunk_size):
        chunk = tiles[i:i + chunk_size]
        # Process chunk
        yield chunk
```

### Network Optimization

```python
# Parallel downloads (use with caution)
import concurrent.futures

def download_parallel(tiles, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_tile, tile) for tile in tiles]
        # Handle results
```

## Production Tips

### File Organization

```
project_name/
├── raw_data/
│   ├── region_A/
│   │   ├── tiles/           # Downloaded .tif files
│   │   └── metadata.json    # Tile metadata
│   └── region_B/
├── houdini_scenes/
│   ├── import_setup.hip     # Base import scene
│   └── final_terrain.hip    # Final terrain with tiles
└── scripts/
    ├── batch_download.py    # Custom batch scripts
    └── validation.py        # Quality checks
```

### Quality Assurance

1. **Validate Downloads**:
   ```python
   # Check file integrity
   import os
   for tile in tiles:
       if not os.path.exists(tile['local_path']):
           print(f"Missing: {tile['local_name']}")
   ```

2. **Coordinate Verification**:
   ```python
   # Verify coordinate consistency
   for tile in tiles:
       if tile['crs'] != 'EPSG:2154':
           print(f"CRS mismatch: {tile['local_name']}")
   ```

3. **Spatial Coverage**:
   ```python
   # Check for gaps in coverage
   def check_spatial_continuity(tiles):
       # Implement gap detection logic
       pass
   ```

### Performance Optimization

1. **Network Settings**:
   - Adjust `HTTP_TIMEOUT` based on connection speed
   - Increase `HTTP_RETRIES` for unstable connections
   - Use `USER_AGENT` that identifies your studio

2. **Storage Management**:
   - Use SSD storage for faster I/O
   - Implement cleanup routines for temp files
   - Consider compression for archival

3. **Houdini Performance**:
   - Load tiles on-demand in Houdini
   - Use level-of-detail (LOD) systems
   - Implement tile caching strategies

## Troubleshooting

### Common Issues

#### Download Failures
```
Error: HTTP 403 Forbidden
```
**Solution**: Check if IGN service is accessible. Try different User-Agent string.

```
Error: Connection timeout
```
**Solution**: Increase `HTTP_TIMEOUT` value or check network connectivity.

#### JSON Import Issues
```
Error: FileNotFoundError in Houdini
```
**Solution**: Verify JSON file path is absolute and accessible from Houdini.

```
Error: JSON decode error
```
**Solution**: Validate JSON format. Re-run downloader if corrupted.

#### Coordinate Issues
```
Warning: CRS non 2154 détecté
```
**Solution**: Verify tile URLs use correct coordinate system for your region.

### Debug Mode

Enable detailed logging:

```python
CONFIG["VERBOSE"] = True

# Add debug prints in Houdini Python SOP
print(f"Loading JSON from: {json_file_path}")
print(f"Found {len(tiles)} tiles")
for i, tile in enumerate(tiles[:3]):  # First 3 tiles
    print(f"Tile {i}: {tile['local_name']}")
```

### Log Analysis

Check download logs for patterns:

```bash
# Count successful downloads
grep "\[OK\]" download.log | wc -l

# Find failed downloads
grep "\[ERR\]" download.log

# Check for network issues
grep "timeout\|connection" download.log
```

## Support

For production support:
- Check [GitHub Issues](https://github.com/yourusername/IGN_Elevation_Importer/issues)
- Review [IGN Service Status](https://geoservices.ign.fr/)
- Validate your setup with provided examples

---

*This workflow guide is designed for professional VFX and game development teams. Adjust parameters based on your specific production requirements.*