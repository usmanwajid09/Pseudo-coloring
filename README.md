# Image Colorization and Enhancement Application

A GUI application for colorizing grayscale images using deep learning and applying various image enhancements.

## Features

- **Deep Learning Colorization**: Uses pre-trained Caffe model (Zhang et al. 2016) to automatically colorize grayscale images
- **Image Enhancements**: ACE, CLAHE, Gamma Correction, Sharpening, Saturation Boost
- **Pseudocolor Mapping**: Fallback colorization using Jet colormap
- **User-Friendly GUI**: Tkinter-based interface for easy image processing

## Requirements

- Python 3.7 or higher
- Required Python packages (see requirements.txt)

## Installation

### Option 1: Using Virtual Environment (Recommended)

1. **Activate the virtual environment** (if you have one):
   ```bash
   # On Windows (Git Bash/PowerShell)
   source .venv/Scripts/activate
   
   # Or if .venv is in parent directory
   cd ..
   source .venv/Scripts/activate
   cd Dip
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Global Installation

```bash
pip install -r requirements.txt
```

## Running the Application

1. **Make sure you're in the Dip directory**:
   ```bash
   cd Dip
   ```

2. **Run the application**:
   ```bash
   python pseudo_color_app.py
   ```

3. **The GUI window will open**. You can then:
   - Click "Load Image" to select an image file
   - Apply various enhancements or colorization
   - Save the processed image

## Required Model Files

The application requires these files in the same directory:
- `colorization_deploy_v2.prototxt` - Model architecture
- `colorization_release_v2.caffemodel` - Pre-trained weights
- `pts_in_hull.npy` - Color quantization data

If these files are missing, the app will fall back to pseudocolor mapping.

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Troubleshooting

- **If GUI doesn't open**: Make sure Tkinter is installed (usually comes with Python)
- **If model doesn't load**: Check that all three model files are in the same directory as the script
- **Import errors**: Run `pip install -r requirements.txt` to install dependencies

