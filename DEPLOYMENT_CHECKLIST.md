# Deployment Checklist for Another PC

## ✅ Pre-Deployment Checklist

### Files to Copy (All Required):
- [ ] `pseudo_color_app_enhanced.py` - **Enhanced version (recommended)**
- [ ] `pseudo_color_app.py` - Original version (optional)
- [ ] `colorization_deploy_v2.prototxt`
- [ ] `colorization_release_v2.caffemodel` (123 MB - largest file!)
- [ ] `pts_in_hull.npy`
- [ ] `requirements.txt`
- [ ] `setup.bat` (Windows) or `setup.sh` (Linux/Mac) - Optional but helpful

## 📋 Setup Steps on New PC

### 1. Install Python
- [ ] Download Python 3.7+ from [python.org](https://www.python.org/downloads/)
- [ ] ✅ Check "Add Python to PATH" during installation
- [ ] Verify: Open terminal and type `python --version`

### 2. Copy Files
- [ ] Copy entire `Dip` folder to new PC
- [ ] Verify all files are in the same directory

### 3. Install Dependencies
- [ ] Open terminal in the `Dip` folder
- [ ] Run: `pip install -r requirements.txt`
- [ ] Or use: `setup.bat` (Windows) / `setup.sh` (Linux/Mac)

### 4. Test Run
- [ ] Run: `python pseudo_color_app_enhanced.py` (enhanced version)
- [ ] OR: `python pseudo_color_app.py` (original version)
- [ ] GUI window should open
- [ ] Try loading an image to test

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "python is not recognized" | Reinstall Python, check "Add to PATH" |
| "No module named 'cv2'" | Run `pip install opencv-python numpy Pillow` |
| GUI doesn't open | Install tkinter: `sudo apt-get install python3-tk` (Linux) |
| Model not loading | Check all 3 model files are present |

## 📦 Quick Transfer Methods

1. **USB Drive**: Copy entire `Dip` folder
2. **Cloud Storage**: Upload folder (note: 123 MB model file)
3. **Network Share**: Copy over local network
4. **Compressed**: Zip folder first to reduce transfer time

## ⚡ Quick Start (After Setup)

```bash
cd Dip
python pseudo_color_app_enhanced.py
```

That's it! The GUI will open and you can start colorizing images.

**Note**: Use `pseudo_color_app_enhanced.py` for the enhanced version with sliders, before/after comparison, and more features!


