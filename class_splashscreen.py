import ttkbootstrap as ttk
from PIL import ImageTk, Image
import os

class SplashScreen(ttk.Toplevel):
    def __init__(self, parent, version_text):
        ttk.Toplevel.__init__(self, parent)
        self.title("")
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Set splash dimensions
        width = 422
        height = 370
        
        # Load and display splash image
        splash_image = Image.open(os.path.join('ico', 'splash.png'))
        #splash_image = splash_image.resize((width, height-30), Image.Resampling.LANCZOS)
        self.splash_photo = ImageTk.PhotoImage(splash_image)
        
        # Create and pack image label
        self.image_label = ttk.Label(self, image=self.splash_photo)
        self.image_label.pack(pady=0)
        
        # Add version number
        self.version_label = ttk.Label(self, text=version_text, font=('TkDefaultFont', 12, 'bold'))
        self.version_label.pack(pady=5)
        
        # Center the splash screen relative to parent window
        self.center_relative_to_parent()
        
        # Bring window to front
        self.lift()
        self.focus_force()
        
        # Update the window
        self.update()
        
    def center_relative_to_parent(self):
        # Wait for parent window to be ready
        self.master.update_idletasks()
        
        # Get parent window position and dimensions
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        # Calculate position
        width = 422
        height = 370
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Set window position
        self.geometry(f"{width}x{height}+{x}+{y}")