#!/usr/bin/env python3
"""
pseudo_color_app_enhanced.py
Enhanced version with improved GUI:
- Adjustable parameters with sliders
- Before/After comparison view
- Undo/Redo functionality
- Status bar with image info
- Keyboard shortcuts
- Progress indicators
- Multiple colormap options
- Better layout and organization
"""

import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading

# Optional pretrained model files
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
        print("[OK] Pretrained colorization model loaded.")
    except Exception as e:
        print("[ERROR] Failed to load colorizer model:", e)
        net = None
else:
    print("ℹ Pretrained model files not found. Colorization will use pseudocolor fallback.")

# ---------------------------
# Enhancement Functions
# ---------------------------
def ace_enhancement(gray, strength=2.0):
    g = gray.astype(np.float32) / 255.0
    local_mean = cv2.GaussianBlur(g, (31,31), 5)
    diff = g - local_mean
    enhanced = local_mean + strength * diff
    enhanced = np.clip(enhanced, 0, 1.0)
    return (enhanced * 255).astype(np.uint8)

def clahe_enhancement(img_bgr, clip_limit=2.5):
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L,A,B = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8,8))
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

def pseudocolor(gray, colormap=cv2.COLORMAP_JET):
    return cv2.applyColorMap(gray, colormap)

def prepare_lab_image(gray_img):
    img_lab = cv2.cvtColor(cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR), cv2.COLOR_BGR2LAB)
    L = img_lab[:,:,0]
    L_rs = cv2.resize(L, (224,224)).astype("float32") - 50
    return L, L_rs

def deep_colorize(gray_img):
    global net
    if net is None:
        return pseudocolor(gray_img)
    L, L_rs = prepare_lab_image(gray_img)
    net.setInput(cv2.dnn.blobFromImage(L_rs))
    ab = net.forward()[0,:,:,:].transpose((1,2,0))
    ab = cv2.resize(ab, (gray_img.shape[1], gray_img.shape[0]))
    lab_full = np.zeros((gray_img.shape[0], gray_img.shape[1], 3), dtype=np.uint8)
    lab_full[:,:,0] = L
    ab_255 = np.clip(ab + 128.0, 0, 255).astype(np.uint8)
    lab_full[:,:,1:] = ab_255
    colorized = cv2.cvtColor(lab_full, cv2.COLOR_LAB2BGR)
    return colorized

# ---------------------------
# Enhanced GUI App
# ---------------------------
class EnhancedApp:
    def __init__(self, root):
        self.root = root
        root.title("Image Colorization & Enhancement Tool")
        root.geometry("1200x800")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Ensure window stays on top initially
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(lambda: root.attributes('-topmost', False))
        
        # State variables
        self.img_bgr = None
        self.img_gray = None
        self.img_output = None
        self.img_original = None
        self.history = []
        self.history_index = -1
        self.current_file_path = None
        self.processing = False
        
        # Colormap options
        self.colormaps = {
            "Jet": cv2.COLORMAP_JET,
            "Viridis": cv2.COLORMAP_VIRIDIS,
            "Plasma": cv2.COLORMAP_PLASMA,
            "Hot": cv2.COLORMAP_HOT,
            "Cool": cv2.COLORMAP_COOL,
            "Rainbow": cv2.COLORMAP_RAINBOW,
            "Turbo": cv2.COLORMAP_TURBO
        }
        
        try:
            self.setup_ui()
            self.setup_keyboard_shortcuts()
        except Exception as e:
            print(f"Error setting up UI: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def setup_ui(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image...", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Output...", command=self.save_output, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z", state="disabled")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y", state="disabled")
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset", command=self.reset_view, accelerator="Ctrl+R")
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        self.comparison_var = tk.BooleanVar()
        view_menu.add_checkbutton(label="Before/After Comparison", variable=self.comparison_var, command=self.toggle_comparison)
        
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5))
        left_panel.pack_propagate(False)
        
        # File operations
        file_frame = tk.LabelFrame(left_panel, text="File Operations", padx=5, pady=5)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Button(file_frame, text="Load Image", command=self.load_image, width=20).pack(pady=2)
        tk.Button(file_frame, text="Save Output", command=self.save_output, width=20).pack(pady=2)
        
        # Enhancement controls
        enhance_frame = tk.LabelFrame(left_panel, text="Enhancements", padx=5, pady=5)
        enhance_frame.pack(fill=tk.X, pady=5)
        
        # Live preview checkbox
        self.live_preview_var = tk.BooleanVar(value=True)
        live_preview_cb = tk.Checkbutton(enhance_frame, text="Live Preview", 
                                        variable=self.live_preview_var)
        live_preview_cb.pack(pady=2)
        
        tk.Button(enhance_frame, text="ACE Enhance", command=self.do_ace, width=20).pack(pady=2)
        self.ace_slider, self.ace_label = self.create_slider(
            enhance_frame, "ACE Strength:", 0.5, 5.0, 2.0, 
            callback=self.on_ace_slider_change)
        
        tk.Button(enhance_frame, text="CLAHE", command=self.do_clahe, width=20).pack(pady=2)
        self.clahe_slider, self.clahe_label = self.create_slider(
            enhance_frame, "CLAHE Clip:", 1.0, 8.0, 2.5,
            callback=self.on_clahe_slider_change)
        
        tk.Button(enhance_frame, text="Gamma Correction", command=self.do_gamma, width=20).pack(pady=2)
        self.gamma_slider, self.gamma_label = self.create_slider(
            enhance_frame, "Gamma:", 0.1, 3.0, 1.5,
            callback=self.on_gamma_slider_change)
        
        tk.Button(enhance_frame, text="Sharpen", command=self.do_sharpen, width=20).pack(pady=2)
        tk.Button(enhance_frame, text="Saturation Boost", command=self.do_sat, width=20).pack(pady=2)
        self.sat_slider, self.sat_label = self.create_slider(
            enhance_frame, "Saturation:", 0.0, 3.0, 1.4,
            callback=self.on_sat_slider_change)
        
        # Colorization controls
        color_frame = tk.LabelFrame(left_panel, text="Colorization", padx=5, pady=5)
        color_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(color_frame, text="Deep Colorize", command=self.do_deep, width=20).pack(pady=2)
        tk.Button(color_frame, text="Pseudocolor", command=self.do_pseudocolor, width=20).pack(pady=2)
        
        # Colormap selection
        colormap_frame = tk.Frame(color_frame)
        colormap_frame.pack(fill=tk.X, pady=2)
        tk.Label(colormap_frame, text="Colormap:").pack(side=tk.LEFT)
        self.colormap_var = tk.StringVar(value="Jet")
        colormap_combo = ttk.Combobox(colormap_frame, textvariable=self.colormap_var, 
                                     values=list(self.colormaps.keys()), state="readonly", width=12)
        colormap_combo.pack(side=tk.LEFT, padx=5)
        
        # Undo/Redo buttons
        undo_frame = tk.Frame(left_panel)
        undo_frame.pack(fill=tk.X, pady=5)
        self.undo_btn = tk.Button(undo_frame, text="Undo", command=self.undo, width=10, state="disabled")
        self.undo_btn.pack(side=tk.LEFT, padx=2)
        self.redo_btn = tk.Button(undo_frame, text="Redo", command=self.redo, width=10, state="disabled")
        self.redo_btn.pack(side=tk.LEFT, padx=2)
        tk.Button(undo_frame, text="Reset", command=self.reset_view, width=10).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Image display
        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Image display frame
        self.display_frame = tk.Frame(right_panel)
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create frame for original image with label
        self.original_frame = tk.Frame(self.display_frame)
        tk.Label(self.original_frame, text="BEFORE", font=("Arial", 10, "bold"), bg="lightblue").pack()
        self.panel_original = tk.Label(self.original_frame, text="No image loaded", bg="gray90")
        self.panel_original.pack(fill=tk.BOTH, expand=True)
        # Don't pack original frame initially - only show when comparison is enabled
        
        # Create frame for output image with label
        self.output_frame = tk.Frame(self.display_frame)
        tk.Label(self.output_frame, text="AFTER", font=("Arial", 10, "bold"), bg="lightgreen").pack()
        self.panel_output = tk.Label(self.output_frame, text="No image loaded", bg="gray90")
        self.panel_output.pack(fill=tk.BOTH, expand=True)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=2)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready | No image loaded", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        
    def create_slider(self, parent, label, min_val, max_val, default, callback=None):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=label, width=12, anchor="w").pack(side=tk.LEFT)
        var = tk.DoubleVar(value=default)
        scale = tk.Scale(frame, from_=min_val, to=max_val, resolution=0.1, 
                        orient=tk.HORIZONTAL, variable=var, length=120,
                        command=callback if callback else None)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Show current value
        value_label = tk.Label(frame, text=f"{default:.1f}", width=5)
        value_label.pack(side=tk.LEFT, padx=2)
        
        # Update label when slider moves
        def update_label(val):
            value_label.config(text=f"{float(val):.1f}")
            if callback:
                callback(val)
        
        scale.config(command=update_label)
        return var, value_label
    
    def setup_keyboard_shortcuts(self):
        self.root.bind('<Control-o>', lambda e: self.load_image())
        self.root.bind('<Control-s>', lambda e: self.save_output())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-r>', lambda e: self.reset_view())
        self.root.bind('<Escape>', lambda e: self.cancel_operation())
    
    def update_status(self, message):
        if self.img_bgr is not None:
            h, w = self.img_bgr.shape[:2]
            size_mb = os.path.getsize(self.current_file_path) / (1024*1024) if self.current_file_path else 0
            info = f"Image: {w}x{h} | Size: {size_mb:.2f} MB | {message}"
        else:
            info = message
        self.status_bar.config(text=info)
        self.root.update_idletasks()
    
    def toggle_comparison(self):
        if self.comparison_var.get():
            # Show both panels side by side
            self.output_frame.pack_forget()
            self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
            self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)
            # Update images if they exist
            if self.img_original is not None:
                self.show_image(self.img_original, self.panel_original)
            if self.img_output is not None:
                self.show_image(self.img_output, self.panel_output)
            self.update_status("Comparison view enabled - showing Before/After")
        else:
            # Show only output panel
            self.original_frame.pack_forget()
            self.output_frame.pack_forget()
            self.output_frame.pack(fill=tk.BOTH, expand=True, padx=2)
            if self.img_output is not None:
                self.show_image(self.img_output, self.panel_output)
            self.update_status("Single view - showing output only")
    
    def show_image(self, img, panel=None):
        if panel is None:
            panel = self.panel_output
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Get panel size for proper scaling
        panel.update_idletasks()
        # Get the frame that contains the panel for size calculation
        frame = panel.master
        frame.update_idletasks()
        frame_width = frame.winfo_width() if frame.winfo_width() > 1 else 400
        frame_height = frame.winfo_height() if frame.winfo_height() > 1 else 400
        
        # Maintain aspect ratio
        h, w = img_rgb.shape[:2]
        scale = min(frame_width/w, frame_height/h, 1.0)
        new_w, new_h = int(w*scale), int(h*scale)
        
        img_pil = Image.fromarray(img_rgb).resize((new_w, new_h), Image.BICUBIC)
        tkimg = ImageTk.PhotoImage(img_pil)
        panel.config(image=tkimg, text="")
        # Keep reference to prevent garbage collection
        panel.image = tkimg
    
    def save_to_history(self):
        if self.img_output is not None:
            # Remove any future history if we're not at the end
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(self.img_output.copy())
            self.history_index = len(self.history) - 1
            # Limit history size
            if len(self.history) > 20:
                self.history.pop(0)
                self.history_index -= 1
            self.update_undo_redo_buttons()
    
    def update_undo_redo_buttons(self):
        can_undo = self.history_index > 0
        can_redo = self.history_index < len(self.history) - 1
        self.undo_btn.config(state="normal" if can_undo else "disabled")
        self.redo_btn.config(state="normal" if can_redo else "disabled")
    
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.img_output = self.history[self.history_index].copy()
            self.show_image(self.img_output)
            self.update_undo_redo_buttons()
    
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.img_output = self.history[self.history_index].copy()
            self.show_image(self.img_output)
            self.update_undo_redo_buttons()
    
    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp *.tiff"), ("All files", "*.*")]
        )
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Error", "Unable to read image")
            return
        
        self.current_file_path = path
        self.img_bgr = img
        self.img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.img_original = img.copy()
        self.img_output = img.copy()
        self.history = [img.copy()]
        self.history_index = 0
        self.update_undo_redo_buttons()
        
        # Update display based on comparison mode
        if self.comparison_var.get():
            # Show both images in comparison mode
            self.show_image(self.img_original, self.panel_original)
            self.show_image(self.img_output, self.panel_output)
        else:
            # Show only output
            self.show_image(self.img_output, self.panel_output)
        self.update_status("Image loaded successfully")
    
    def process_with_progress(self, func, *args):
        if self.processing:
            return
        self.processing = True
        self.progress.pack(fill=tk.X, pady=2)
        self.progress.start()
        self.update_status("Processing...")
        
        def worker():
            try:
                result = func(*args)
                self.root.after(0, lambda: self.on_processing_done(result))
            except Exception as e:
                self.root.after(0, lambda: self.on_processing_error(str(e)))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def on_processing_done(self, result):
        self.progress.stop()
        self.progress.pack_forget()
        self.processing = False
        self.img_output = result
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status("Processing complete")
    
    def on_processing_error(self, error):
        self.progress.stop()
        self.progress.pack_forget()
        self.processing = False
        messagebox.showerror("Error", f"Processing failed: {error}")
        self.update_status("Error occurred")
    
    def on_ace_slider_change(self, val):
        if self.img_gray is None:
            return
        if not self.live_preview_var.get():
            return
        strength = float(val)
        out = ace_enhancement(self.img_gray, strength)
        self.img_output = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"ACE Strength: {strength:.2f}")
    
    def do_ace(self):
        if self.img_gray is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        strength = self.ace_slider.get()
        out = ace_enhancement(self.img_gray, strength)
        self.img_output = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status("ACE enhancement applied")
    
    def on_clahe_slider_change(self, val):
        if self.img_bgr is None or not self.live_preview_var.get():
            return
        clip_limit = float(val)
        out = clahe_enhancement(self.img_bgr, clip_limit)
        self.img_output = out
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"CLAHE Clip: {clip_limit:.2f}")
    
    def do_clahe(self):
        if self.img_bgr is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        clip_limit = self.clahe_slider.get()
        out = clahe_enhancement(self.img_bgr, clip_limit)
        self.img_output = out
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status("CLAHE enhancement applied")
    
    def on_gamma_slider_change(self, val):
        if self.img_bgr is None or not self.live_preview_var.get():
            return
        gamma = float(val)
        out = gamma_correction(self.img_bgr, gamma)
        self.img_output = out
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"Gamma: {gamma:.2f}")
    
    def do_gamma(self):
        if self.img_bgr is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        gamma = self.gamma_slider.get()
        out = gamma_correction(self.img_bgr, gamma)
        self.img_output = out
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"Gamma correction applied (γ={gamma:.2f})")
    
    def do_sharpen(self):
        if self.img_bgr is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        out = sharpen(self.img_bgr)
        self.img_output = out
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status("Sharpening applied")
    
    def on_sat_slider_change(self, val):
        if self.img_bgr is None or not self.live_preview_var.get():
            return
        factor = float(val)
        out = saturation_boost(self.img_bgr, factor)
        self.img_output = out
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"Saturation: {factor:.2f}")
    
    def do_sat(self):
        if self.img_bgr is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        factor = self.sat_slider.get()
        out = saturation_boost(self.img_bgr, factor)
        self.img_output = out
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"Saturation boost applied (factor={factor:.2f})")
    
    def do_pseudocolor(self):
        if self.img_gray is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        colormap_name = self.colormap_var.get()
        colormap = self.colormaps[colormap_name]
        out = pseudocolor(self.img_gray, colormap)
        self.img_output = out
        self.save_to_history()
        self.show_image(self.img_output, self.panel_output)
        self.update_status(f"Pseudocolor applied ({colormap_name})")
    
    def do_deep(self):
        if self.img_gray is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        self.process_with_progress(deep_colorize, self.img_gray)
    
    def save_output(self):
        if self.img_output is None:
            messagebox.showwarning("Warning", "No output to save")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", ".png"), ("JPEG", ".jpg"), ("All files", "*.*")]
        )
        if not path:
            return
        cv2.imwrite(path, self.img_output)
        messagebox.showinfo("Saved", f"Image saved to:\n{path}")
        self.update_status(f"Saved to {os.path.basename(path)}")
    
    def reset_view(self):
        if self.img_bgr is not None:
            self.img_output = self.img_bgr.copy()
            self.history = [self.img_bgr.copy()]
            self.history_index = 0
            self.update_undo_redo_buttons()
            self.show_image(self.img_output, self.panel_output)
            self.update_status("View reset")
    
    def cancel_operation(self):
        if self.processing:
            self.progress.stop()
            self.progress.pack_forget()
            self.processing = False
            self.update_status("Operation cancelled")
    
    def on_closing(self):
        print("Window closing...")
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    try:
        print("Initializing GUI...")
        root = tk.Tk()
        print("Root window created, setting up app...")
        app = EnhancedApp(root)
        print("App initialized, starting mainloop...")
        print("GUI window should be visible now. Close the window to exit.")
        root.mainloop()
        print("Mainloop ended.")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

