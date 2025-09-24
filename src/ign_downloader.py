# -*- coding: utf-8 -*-
"""
IGN LiDAR MNT Downloader - Standalone Version
----------------------------------------------

Standalone Python script to download IGN LiDAR tiles from a .txt file
and generate a JSON metadata file for Houdini.

USAGE
-----
python ign_downloader.py

Modify the config below before use.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse

# =========================
# ======== CONFIG =========
# =========================

CONFIG = {
    # Path to .txt file containing the URLs
    "TXT_SOURCE": "2f79f8c7-6b76-446a-a213-63e335883b6b.txt",
    
    # Destination folder for downloads
    "DOWNLOAD_DIR": "ign_mnt_tiles",
    
    # JSON metadata file for Houdini
    "METADATA_FILE": "tiles_metadata.json",
    
    # Timeout and retries for downloads
    "HTTP_TIMEOUT": 60,
    "HTTP_RETRIES": 2,
    
    # HTTP User-Agent
    "USER_AGENT": "IGN-MNT-Downloader/1.0 (Python urllib)",
    
    # Verbose mode
    "VERBOSE": True,
}

# ==============================
# ===== UTILS: DOWNLOAD =========
# ==============================

def log(msg):
    """Conditional display based on VERBOSE setting."""
    if CONFIG["VERBOSE"]:
        print(msg)

def expand_path(path):
    """Expand ~, environment variables, etc."""
    path = os.path.expandvars(os.path.expanduser(path))
    return os.path.normpath(path)

def read_text_source(txt_source):
    """Reads the content of the .txt file and returns a list of non-empty lines."""
    parsed = urllib.parse.urlparse(txt_source)
    lines = []
    
    if parsed.scheme in ("http", "https"):
        req = urllib.request.Request(txt_source, headers={"User-Agent": CONFIG["USER_AGENT"]})
        with urllib.request.urlopen(req, timeout=CONFIG["HTTP_TIMEOUT"]) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        lines = [ln.strip() for ln in data.splitlines() if ln.strip()]
    else:
        # local file
        with open(expand_path(txt_source), "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    
    return lines

def url_filename_from_query(url):
    """Retrieves the FILENAME=xxx parameter from the URL; otherwise infers a name."""
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if "FILENAME" in qs and qs["FILENAME"]:
        return qs["FILENAME"][0]
    
    # fallback: last segment + timestamp if needed
    name = os.path.basename(urllib.parse.urlparse(url).path)
    if not name or not name.lower().endswith(".tif"):
        name = f"tile_{int(time.time())}.tif"
    return name

def download_with_retries(url, out_path):
    """Downloads a binary file with retry logic."""
    tmp_path = out_path + ".part"
    last_err = None
    
    for attempt in range(1, CONFIG["HTTP_RETRIES"] + 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": CONFIG["USER_AGENT"]})
            with urllib.request.urlopen(req, timeout=CONFIG["HTTP_TIMEOUT"]) as resp:
                with open(tmp_path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
            
            os.replace(tmp_path, out_path)
            return out_path
            
        except Exception as e:
            last_err = e
            if attempt <= CONFIG["HTTP_RETRIES"]:
                log(f"[RETRY] Attempt {attempt} failed for {os.path.basename(out_path)}: {e}")
                time.sleep(1.0 * attempt)
            
    raise last_err

# =================================
# ===== PARSING: URL -> TILE ======
# =================================

def parse_bbox_from_url(url):
    """
    Extracts minx, miny, maxx, maxy, width_px, height_px, crs from WMS URL.
    Returns dict or raises ValueError.
    """
    up = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(up.query)
    
    def grab_one(name, cast=None):
        if name not in qs or not qs[name]:
            return None
        val = qs[name][0]
        return cast(val) if cast else val
    
    bbox_str = grab_one("BBOX")
    if not bbox_str:
        raise ValueError(f"URL without BBOX=... : {url}")
    
    try:
        minx, miny, maxx, maxy = [float(v) for v in bbox_str.split(",")]
    except Exception:
        raise ValueError(f"Invalid BBOX (expected minx,miny,maxx,maxy) : {bbox_str!r}")
    
    width_px = grab_one("WIDTH", cast=int)
    height_px = grab_one("HEIGHT", cast=int)
    crs = grab_one("CRS") or grab_one("SRS") or ""
    
    tile_w_m = maxx - minx
    tile_h_m = maxy - miny
    
    return {
        "minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy,
        "w_m": tile_w_m, "h_m": tile_h_m,
        "width_px": width_px, "height_px": height_px,
        "crs": crs,
    }

def load_tiles_from_lines(lines):
    """
    Parse all lines from the .txt file.
    Returns:
      tiles: list of dict {url, local_name, minx,..., w_m,...}
      bbox_minx, bbox_miny : global min
    """
    tiles = []
    minx_all = float("+inf")
    miny_all = float("+inf")
    
    for line in lines:
        if line.startswith("#"):
            continue
        url = line.strip()
        if not url:
            continue
        
        try:
            meta = parse_bbox_from_url(url)
            local_name = url_filename_from_query(url)
            
            tile = {"url": url, "local_name": local_name}
            tile.update(meta)
            tiles.append(tile)
            
            minx_all = min(minx_all, meta["minx"])
            miny_all = min(miny_all, meta["miny"])
            
            # Sanity check
            if meta["crs"] and "2154" not in meta["crs"]:
                log(f"[WARN] Non-2154 CRS detected for {local_name}: {meta['crs']}")
                
        except Exception as e:
            log(f"[ERROR] Cannot parse URL: {url} - {e}")
            continue
    
    if not tiles:
        raise RuntimeError("No valid tiles found in the .txt file")
    
    return tiles, minx_all, miny_all

# ============================
# ======== MAIN RUN ==========
# ============================

def main():
    """Launches the download and generates metadata."""
    
    # Prepare paths
    out_dir = expand_path(CONFIG["DOWNLOAD_DIR"])
    metadata_path = os.path.join(out_dir, CONFIG["METADATA_FILE"])
    
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        log(f"[INFO] Directory created: {out_dir}")
    
    # Get URLs from the .txt file
    try:
        lines = read_text_source(CONFIG["TXT_SOURCE"])
        tiles, minx_all, miny_all = load_tiles_from_lines(lines)
        log(f"[INFO] {len(tiles)} tiles found in source file")
    except Exception as e:
        print(f"[ERROR] Cannot read source file: {e}")
        return 1
    
    # Downloads
    log(f"[INFO] Downloading tiles to: {out_dir}")
    successful_downloads = 0
    failed_downloads = 0
    
    for i, tile in enumerate(tiles, 1):
        local_name = tile["local_name"]
        local_path = os.path.join(out_dir, local_name)
        # Ensure the path is absolute for metadata
        tile["local_path"] = os.path.abspath(local_path)
        
        if os.path.isfile(local_path):
            log(f"  [{i:3d}/{len(tiles)}] [OK] Present: {local_name}")
            successful_downloads += 1
            continue
        
        try:
            log(f"  [{i:3d}/{len(tiles)}] [DL] {local_name}...")
            download_with_retries(tile["url"], local_path)
            successful_downloads += 1
            log(f"  [{i:3d}/{len(tiles)}] [OK] Downloaded: {local_name}")
        except Exception as e:
            log(f"  [{i:3d}/{len(tiles)}] [ERR] Failed: {local_name} - {e}")
            failed_downloads += 1
    
    # Generate metadata for Houdini
    metadata = {
        "tiles": tiles,
        "global_bbox": {
            "minx": minx_all,
            "miny": miny_all
        },
        "stats": {
            "total_tiles": len(tiles),
            "successful_downloads": successful_downloads,
            "failed_downloads": failed_downloads
        },
        "download_dir": out_dir,
        "generated_at": time.time()
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    log(f"[INFO] Metadata saved: {metadata_path}")
    log(f"[DONE] {successful_downloads} successful downloads, {failed_downloads} failures")
    
    return 0 if failed_downloads == 0 else 1

if __name__ == "__main__":
    sys.exit(main())