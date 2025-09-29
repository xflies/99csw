import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from tkinterdnd2 import DND_FILES, TkinterDnD
from utils import PageList, Progress
from handlers import SynthesizeHandler

class FileProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor")
        # self.root.geometry("600x400")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.dropped_files = []
        self.synthesize_var = tk.StringVar(value="Synthesize")
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for drag-drop and radio buttons
        top_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        # NW: Drag-drop area
        self.setup_drag_drop_area(top_frame)
        
        # NE: Radio button group
        self.setup_radio_buttons(top_frame)
        
        # S: Process button
        self.setup_process_button(main_frame)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(10, 2))

        # Information bar
        self.info_var = tk.StringVar(value="Ready.")
        self.info_label = tk.Label(
            main_frame,
            textvariable=self.info_var,
            bg='#f0f0f0',
            fg='#333333',
            anchor='w',
            font=('Arial', 10)
        )
        self.info_label.pack(fill=tk.X, pady=(0, 5))
    
    def setup_drag_drop_area(self, parent):
        # Drag-drop frame (NW)
        drag_frame = tk.Frame(parent, bg='#e8e8e8', relief=tk.RAISED, bd=2)
        drag_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Drag-drop label
        drag_label = tk.Label(
            drag_frame, 
            text="Drag & Drop Files or Folders Here\n\nSupported: Files and Folders",
            bg='#e8e8e8',
            font=('Arial', 12),
            fg='#666666'
        )
        drag_label.pack(expand=True)
        
        # File list display
        self.file_listbox = tk.Listbox(
            drag_frame,
            bg='white',
            font=('Arial', 10),
            selectmode=tk.MULTIPLE
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Clear button
        clear_btn = tk.Button(
            drag_frame,
            text="Clear List",
            command=self.clear_files,
            bg='#ff6b6b',
            fg='white',
            font=('Arial', 10)
        )
        clear_btn.pack(pady=5)
        
        # Enable drag and drop
        self.file_listbox.drop_target_register(DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
    
    def setup_radio_buttons(self, parent):
        # Radio button frame (NE)
        radio_frame = tk.LabelFrame(
            parent, 
            text="Options", 
            bg='#f0f0f0',
            font=('Arial', 12, 'bold'),
            fg='#333333'
        )
        radio_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Radio button
        radio_btn = tk.Radiobutton(
            radio_frame,
            text="Synthesize",
            variable=self.synthesize_var,
            value="Synthesize",
            bg='#f0f0f0',
            font=('Arial', 11),
            fg='#333333'
        )
        radio_btn.pack(anchor=tk.W, padx=10, pady=10)
        
        # Add some padding to make it look better
        tk.Frame(radio_frame, height=20, bg='#f0f0f0').pack()
    
    def setup_process_button(self, parent):
        # Process button frame (S)
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Process button
        self.process_btn = tk.Button(
            button_frame,
            text="Process",
            command=self.process_files,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        self.process_btn.pack(fill=tk.X)
    
    def on_drop(self, event):
        """Handle file drop event"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            if file_path not in self.dropped_files:
                self.dropped_files.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
    
    def clear_files(self):
        """Clear the file list"""
        self.dropped_files.clear()
        self.file_listbox.delete(0, tk.END)
        # Reset progress bar and info label
        progress = Progress(self.progress_bar, self.info_label)
        progress.update_bar(0)
        progress.update_info("Ready.")
        
    def process_files(self):
        """Process the dropped files"""
        if not self.dropped_files:
            messagebox.showwarning("Warning", "Please drop some files or folders first!")
            return
        
        selected_option = self.synthesize_var.get()
        
        # 1. Create a handler by the selected_option
        if selected_option == "Synthesize":
            handler = SynthesizeHandler()
        else:
            messagebox.showerror("Error", f"Unknown option: {selected_option}")
            return
        
        # 2. Create a PageList and append all the dropped_files
        page_list = PageList()
        for file_path in self.dropped_files:
            try:
                page_list.append(file_path)
            except ValueError as e:
                messagebox.showwarning("Warning", f"Error adding {file_path}: {str(e)}")
                continue
        
        if not page_list:
            messagebox.showwarning("Warning", "No HTML files found to process!")
            return
        
        # 3. Create a Progress to bind the progress bar and the info label
        progress = Progress(self.progress_bar, self.info_label)
        
        # Set up progress tracking
        total_files = len(page_list)
        progress.set_maximum(total_files)
        progress.update_info(f"Starting to process {total_files} HTML files...")
        
        # 4. Call the handler to process each file
        processed_count = 0
        for file_path in page_list:
            # Update info label with filename
            filename = os.path.basename(file_path)
            progress.update_info(f"Processing: {filename}")
            self.root.update()  # Update GUI to show current status
            
            # Process the file
            success = handler(file_path)
            processed_count += 1
            
            # Update progress bar based on file count
            progress.update_bar(processed_count)
            
            # Update info with result
            if success:
                progress.update_info(f"Completed: {filename} ({processed_count}/{total_files})")
            else:
                progress.update_info(f"Failed: {filename} ({processed_count}/{total_files})")
            
            self.root.update()  # Update GUI
        
        # Final status
        progress.update_info(f"Processing complete! {processed_count} files processed successfully.")


def main():
    # Create the main window with drag and drop support
    root = TkinterDnD.Tk()
    app = FileProcessorGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
