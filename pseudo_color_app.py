#!/usr/bin/env python3
"""
pseudo_color_app.py
Combined single-file application:
- Pretrained OpenCV colorization model (if model files present)
- Enhancement functions (ACE, CLAHE, Gamma, Sharpen, Saturation)
- Pseudocolor mapping
- Tkinter GUI to load image, apply enhancements, colorize, and save output
This script handles missing model files gracefully (falls back to pseudocolor).
"""

import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Optional pretrained model files for Zhang2016-based colorizer (OpenCV): place these files in same folder
PROTO_FILE = "colorization_deploy_v2.prototxt"
MODEL_FILE = "colorization_release_v2.caffemodel"
PTS_FILE = "pts_in_hull.npy"

net = None
if os.path.exists(PROTO_FILE) and os.path.exists(MODEL_FILE) and os.path.exists(PTS_FILE):
    try:
        pts = np.load(PTS_FILE)
        net = cv2.dnn.readNetFromCaffe(PROTO_FILE, MODEL_FILE)
        pts2 = pts.transpose().reshape(2, 313, 1, 1)
        net.getLayer(net.getLayerId("class8_ab")).blobs = [pts2.astype(np.float32)]
        net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [np.full([1,313], 2.606, dtype="float32")]
        print(" Pretrained colorization model loaded.")
    except Exception as e:
        print(" Failed to load colorizer model:", e)
        net = None
else:
    print("ℹ Pretrained model files not found. Colorization will use pseudocolor fallback (Jet).")

# ---------------------------
# Utilities & model helper
# ---------------------------
def prepare_lab_image(gray_img):
    """Return original L and scaled L for model (224x224)"""
    img_lab = cv2.cvtColor(cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2LAB)
    L = img_lab[:,:,0]
    L_rs = cv2.resize(L, (224,224)).astype("float32") - 50
    return L, L_rs

# ---------------------------
# Enhancements
# ---------------------------
def ace_enhancement(gray):
    g = gray.astype(np.float32) / 255.0
    local_mean = cv2.GaussianBlur(g, (31,31), 5)
    diff = g - local_mean
    enhanced = local_mean + 2.0 * diff
    enhanced = np.clip(enhanced, 0, 1.0)
    return (enhanced * 255).astype(np.uint8)

def clahe_enhancement(img_bgr):
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L,A,B = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8,8))
    L2 = clahe.apply(L)
    enhanced = cv2.merge([L2,A,B])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

def gamma_correction(img, gamma=1.5):
    inv = 1.0 / gamma
    table = np.array([((i/255.0) ** inv) * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(img, table)

def sharpen(img):
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    return cv2.filter2D(img, -1, kernel)

def saturation_boost(img, factor=1.3):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.split(hsv)
    s = np.clip(s.astype(np.float32) * factor, 0, 255).astype(np.uint8)
    boosted = cv2.merge([h,s,v])
    return cv2.cvtColor(boosted, cv2.COLOR_HSV2BGR)

def pseudocolor(gray):
    return cv2.applyColorMap(gray, cv2.COLORMAP_JET)

def deep_colorize(gray_img):
    global net
    if net is None:
        # fallback: pseudocolor
        return pseudocolor(gray_img)
    L, L_rs = prepare_lab_image(gray_img)
    net.setInput(cv2.dnn.blobFromImage(L_rs))
    ab = net.forward()[0,:,:,:].transpose((1,2,0))
    ab = cv2.resize(ab, (gray_img.shape[1], gray_img.shape[0]))
    # combine L + ab to LAB image (OpenCV expects L in 0-255, ab in 0-255 typically)
    lab_full = np.zeros((gray_img.shape[0], gray_img.shape[1], 3), dtype=np.uint8)
    lab_full[:,:,0] = L
    # ab values returned by network are in (-128,127) range around 0; some implementations expect direct mapping — using returned values shifted:
    ab_255 = np.clip(ab + 128.0, 0, 255).astype(np.uint8)
    lab_full[:,:,1:] = ab_255
    colorized = cv2.cvtColor(lab_full, cv2.COLOR_LAB2BGR)
    return colorized

# ---------------------------
# GUI App
# ---------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("CPUP — Pseudo-Colorization (pretrained + enhancements)")
        self.img_bgr = None
        self.img_gray = None
        self.img_output = None
        self.panel = tk.Label(root)
        self.panel.pack(padx=10, pady=10)
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Load Image", command=self.load_image, width=16).grid(row=0,column=0,padx=6,pady=6)
        tk.Button(btn_frame, text="ACE Enhance", command=self.do_ace, width=16).grid(row=0,column=1,padx=6,pady=6)
        tk.Button(btn_frame, text="CLAHE", command=self.do_clahe, width=16).grid(row=0,column=2,padx=6,pady=6)
        tk.Button(btn_frame, text="Gamma", command=self.do_gamma, width=16).grid(row=0,column=3,padx=6,pady=6)
        tk.Button(btn_frame, text="Sharpen", command=self.do_sharpen, width=16).grid(row=1,column=0,padx=6,pady=6)
        tk.Button(btn_frame, text="Saturate", command=self.do_sat, width=16).grid(row=1,column=1,padx=6,pady=6)
        tk.Button(btn_frame, text="Pseudocolor", command=self.do_pseudocolor, width=16).grid(row=1,column=2,padx=6,pady=6)
        tk.Button(btn_frame, text="Deep Colorize", command=self.do_deep, width=16).grid(row=1,column=3,padx=6,pady=6)
        tk.Button(btn_frame, text="Save Output", command=self.save_output, width=16).grid(row=2,column=1,padx=6,pady=6)
        tk.Button(btn_frame, text="Reset View", command=self.reset_view, width=16).grid(row=2,column=2,padx=6,pady=6)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images","*.jpg *.png *.jpeg *.bmp *.tiff")])
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error","Unable to read image")
            return
        self.img_bgr = img
        self.img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.img_output = img.copy()
        self.show_image(self.img_output)

    def show_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb).resize((600,600), Image.BICUBIC)
        self.tkimg = ImageTk.PhotoImage(img_pil)
        self.panel.config(image=self.tkimg)

    def do_ace(self):
        if self.img_gray is None: return
        out = ace_enhancement(self.img_gray)
        self.img_output = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        self.show_image(self.img_output)

    def do_clahe(self):
        if self.img_bgr is None: return
        out = clahe_enhancement(self.img_bgr)
        self.img_output = out
        self.show_image(self.img_output)

    def do_gamma(self):
        if self.img_bgr is None: return
        out = gamma_correction(self.img_bgr, gamma=1.5)
        self.img_output = out
        self.show_image(self.img_output)

    def do_sharpen(self):
        if self.img_bgr is None: return
        out = sharpen(self.img_bgr)
        self.img_output = out
        self.show_image(self.img_output)

    def do_sat(self):
        if self.img_bgr is None: return
        out = saturation_boost(self.img_bgr, factor=1.4)
        self.img_output = out
        self.show_image(self.img_output)

    def do_pseudocolor(self):
        if self.img_gray is None: return
        out = pseudocolor(self.img_gray)
        self.img_output = out
        self.show_image(self.img_output)

    def do_deep(self):
        if self.img_gray is None: return
        out = deep_colorize(self.img_gray)
        self.img_output = out
        self.show_image(self.img_output)

    def save_output(self):
        if self.img_output is None:
            messagebox.showwarning("Warning","No output to save")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG",".png"),("JPEG",".jpg")])
        if not path: return
        cv2.imwrite(path, self.img_output)
        messagebox.showinfo("Saved",f"Saved to {path}")

    def reset_view(self):
        if self.img_bgr is not None:
            self.img_output = self.img_bgr.copy()
            self.show_image(self.img_output)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()