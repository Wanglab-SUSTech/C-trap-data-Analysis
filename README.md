# Kymograph Sorter

A Tkinter + ttkbootstrap GUI tool for organizing, viewing, and exporting C-Trap kymographs and scan images — sort files into categories, stitch kymos, subtract background, and export publication-ready figures, all in one place.

## Features

- **File sorting** — batch import images (`.png` `.jpg` `.tif` `.bmp` `.gif`) and C-Trap `.h5` kymographs, then copy or move them into user-defined category folders; supports linking existing folders, filtering, and a removable file list
- **Kymograph stitching** — concatenate multiple `.h5` kymographs into one continuous image (left = early, right = late)
- **Image viewer** — adjustable gain & offset, 1:1 aspect mode, annotation tools
- **Crop & scale** — two-point ROI cropping with automatic scale ticks and bp conversion (1 bp = 0.34 nm)
- **Background subtraction** — four modes: zero frame, temporal (percentile over time), spatial (side columns), and draggable ROI; median or mean statistics with optional row smoothing
- **Scan mode** — frame-by-frame viewing of multi-frame scans (X/Y position plots)
- **Force export** — export force & distance channels from `.h5` to CSV with downsampling
- **High-resolution export** — save current image as 300 dpi PNG
- **Bilingual UI** — one-click Chinese / English switch

## Requirements

- Python 3.8
- Dependencies:

```bash
pip install pylake==0.8.1 ttkbootstrap pillow numpy pandas matplotlib
```

> Note: `pylake` is optional — without it the tool still works on plain images; `.h5` support is disabled.

## Usage

```bash
python kymograph_sorter.py
```

1. **Add Single / Batch Import** to load kymographs or images
2. Review files in the viewer (adjust gain/offset, crop, subtract background)
3. Sort into category folders with **Copy** or **Move** mode
4. Use **Stitch** to merge consecutive kymographs, or **Save** to export a 300 dpi PNG

## Notes

- `.h5` files must be exported by a Lumicks C-Trap (read via pylake)
- Version history is kept as separate files (`kymograph_sorter*.py`) following the author's one-file-per-version convention

## License

For internal laboratory research use only.
