# Setup Guide for Running on Another PC

## Files You Need to Copy

Copy the entire `Dip` folder with these essential files:

### Required Files:
1. **`pseudo_color_app.py`** - Main application script
2. **`colorization_deploy_v2.prototxt`** - Model architecture (9.7 KB)
3. **`colorization_release_v2.caffemodel`** - Pre-trained model weights (123 MB) ⚠️ Large file!
4. **`pts_in_hull.npy`** - Color quantization data (5 KB)
5. **`requirements.txt`** - Python dependencies list

### Optional Files:
- `test_gui.py` - Test script for Tkinter
- `README.md` - Documentation

## Setup Steps on New PC

### Step 1: Install Python
- Download and install **Python 3.7 or higher** from [python.org](https://www.python.org/downloads/)
- ⚠️ **Important**: During installation, check "Add Python to PATH"

### Step 2: Copy Project Files
- Copy the entire `Dip` folder to the new PC
- Make sure all files are in the same directory

### Step 3: Open Terminal/Command Prompt
- Navigate to the `Dip` folder:
  ```bash
  cd path/to/Dip
  ```

### Step 4: Install Dependencies

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows (CMD):
.venv\Scripts\activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Git Bash):
source .venv/Scripts/activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Global Installation (Simpler)**
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python pseudo_color_app.py
```

## Quick Setup Script (Windows)

Create a file `setup.bat` in the Dip folder:
```batch
@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Setup complete! Run: python pseudo_color_app.py
pause
```

## Troubleshooting

### Issue: "python is not recognized"
- **Solution**: Python is not in PATH. Reinstall Python and check "Add Python to PATH"

### Issue: "pip is not recognized"
- **Solution**: Use `python -m pip install -r requirements.txt` instead

### Issue: "No module named 'cv2'"
- **Solution**: Run `pip install opencv-python numpy Pillow`

### Issue: GUI doesn't open
- **Solution**: Tkinter might not be installed. On Linux, install: `sudo apt-get install python3-tk`

### Issue: Model files not found
- **Solution**: Make sure all 3 model files are in the same folder as `pseudo_color_app.py`
- The app will still work but will use pseudocolor fallback

## Minimum System Requirements

- **OS**: Windows 7+, Linux, or macOS
- **Python**: 3.7 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: ~150 MB (for model files + dependencies)
- **Display**: GUI requires a display (won't work headless without X11)

## File Size Summary

- `pseudo_color_app.py`: ~8 KB
- `colorization_deploy_v2.prototxt`: ~10 KB
- `colorization_release_v2.caffemodel`: **123 MB** (largest file)
- `pts_in_hull.npy`: ~5 KB
- **Total**: ~123 MB

## Network Transfer Tips

If transferring over network:
- The `.caffemodel` file is 123 MB - may take time on slow connections
- Consider compressing the folder before transfer
- Use USB drive for faster transfer


