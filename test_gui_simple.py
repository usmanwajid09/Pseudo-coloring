import tkinter as tk
import sys

print("Testing Tkinter...")
try:
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")
    
    label = tk.Label(root, text="If you see this window, Tkinter is working!", 
                     font=("Arial", 14), padx=20, pady=20)
    label.pack()
    
    button = tk.Button(root, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("Window created. It should be visible now.")
    print("If you don't see it, check if it's behind other windows.")
    print("Press Alt+Tab to find it.")
    
    root.mainloop()
    print("Window closed.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")

