import os
import glob
from typing import List, Callable, Union, Optional
import tkinter as tk


class PageList:
    """
    A class to manage a list of HTML file names with methods to append files/folders
    and iterate through them with a handler function.
    """
    
    def __init__(self):
        """Initialize an empty PageList."""
        self.file_names: List[str] = []
    
    def append(self, path: Union[str, os.PathLike]) -> None:
        """
        Append HTML files to the list.
        
        Args:
            path: A file path (must be *.html) or folder path
                 For files: only accepts *.html files
                 For folders: scans and appends all *.html files in the first level
        """
        path = str(path)
        
        if os.path.isfile(path):
            # Handle single file
            if path.lower().endswith('.html') and "_2" not in path:
                if path not in self.file_names:
                    self.file_names.append(path)
            else:
                raise ValueError(f"File must be *.html, got: {path}")
                
        elif os.path.isdir(path):
            # Handle folder - scan first level only
            html_pattern = os.path.join(path, "*.html")
            html_files = glob.glob(html_pattern)
            
            for html_file in html_files:
                if html_file not in self.file_names and "_2" not in html_file:
                    self.file_names.append(html_file)
        else:
            raise ValueError(f"Path does not exist: {path}")
    
    def foreach(self, handler: Callable[[str], None]) -> None:
        """
        Apply a handler function to each file in the list.
        
        Args:
            handler: A function that takes a file path (str) as argument
        """
        for file_name in self.file_names:
            handler(file_name)
    
    def clear(self) -> None:
        """Clear all files from the list."""
        self.file_names.clear()
    
    def __len__(self) -> int:
        """Return the number of files in the list."""
        return len(self.file_names)
    
    def __iter__(self):
        """Make the class iterable."""
        return iter(self.file_names)
    
    def __str__(self) -> str:
        """Return a string representation of the PageList."""
        return f"PageList({len(self.file_names)} files): {self.file_names}"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the PageList."""
        return f"PageList(file_names={self.file_names})"


class Progress:
    """
    A class to manage progress bar and info label updates in a Tkinter GUI.
    """
    
    def __init__(self, progress_bar: tk.Widget, info_label: tk.Widget):
        """
        Initialize the Progress manager.
        
        Args:
            progress_bar: A Tkinter progress bar widget (ttk.Progressbar)
            info_label: A Tkinter label widget for displaying information
        """
        self.progress_bar = progress_bar
        self.info_label = info_label
        
        # Get the progress bar's variable for value updates
        if hasattr(progress_bar, 'variable') and progress_bar.variable:
            self.progress_var = progress_bar.variable
        else:
            # Create a new variable if none exists
            self.progress_var = tk.DoubleVar(value=0)
            progress_bar.configure(variable=self.progress_var)
        
        # Get the info label's text variable
        if hasattr(info_label, 'textvariable') and info_label.textvariable:
            self.info_var = info_label.textvariable
        else:
            # Create a new variable if none exists
            self.info_var = tk.StringVar(value="Ready.")
            info_label.configure(textvariable=self.info_var)
    
    def update_info(self, message: str) -> None:
        """
        Update the information label with a new message.
        
        Args:
            message: The message to display in the info label
        """
        if self.info_var:
            self.info_var.set(message)
        else:
            # Fallback to direct text update if no variable
            self.info_label.configure(text=message)
    
    def update_bar(self, value: float, maximum: Optional[float] = None) -> None:
        """
        Update the progress bar value.
        
        Args:
            value: The current progress value (0-100 by default)
            maximum: Optional maximum value (if different from 100)
        """
        if maximum is not None:
            # Update the maximum value if provided
            self.progress_bar.configure(maximum=maximum)
        
        if self.progress_var:
            self.progress_var.set(value)
        else:
            # Fallback to direct value update if no variable
            self.progress_bar.configure(value=value)
    
    def reset(self) -> None:
        """Reset the progress bar to 0 and set info to 'Ready.'"""
        self.update_bar(0)
        self.update_info("Ready.")
    
    def set_maximum(self, maximum: float) -> None:
        """
        Set the maximum value for the progress bar.
        
        Args:
            maximum: The maximum value for the progress bar
        """
        self.progress_bar.configure(maximum=maximum)
    
    def get_value(self) -> float:
        """
        Get the current progress bar value.
        
        Returns:
            float: The current progress value
        """
        if self.progress_var:
            return self.progress_var.get()
        else:
            return self.progress_bar.cget('value')
    
    def get_info(self) -> str:
        """
        Get the current info label text.
        
        Returns:
            str: The current info message
        """
        if self.info_var:
            return self.info_var.get()
        else:
            return self.info_label.cget('text')

