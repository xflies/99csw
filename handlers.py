import os
import re
from typing import Optional, Dict


class SynthesizeHandler:
    """
    A handler class that processes HTML files with dictionary-based replacements.
    
    Features:
    1. Reads dictionary.csv for replacement rules
    2. For index.html: applies dictionary replacements to each line
    3. For other HTML files:
       - Reads corresponding .txt file and wraps each line in <div> tags
       - Replaces content between <main> tags with the wrapped content
       - Applies dictionary replacements
       - Saves as XXXX_2.html
    """
    
    def __init__(self):
        """Initialize the SynthesizeHandler."""
        self.dictionary: Dict[str, str] = {}
    
    def load_dictionary(self) -> None:
        """
        Load replacement dictionary from dictionary.csv file.
        Each line should be in format: A,B (replace A with B)
        """
        try:
            self.dictionary = {}
            # Look for dictionary.csv in the current working directory
            dict_path = os.path.join(self.folder_path, "dictionary.csv")
            if os.path.exists(dict_path):
                with open(dict_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ',' in line:
                            parts = line.split(',', 1)  # Split only on first comma
                            if len(parts) == 2:
                                key = parts[0].strip()
                                value = parts[1].strip()
                                if value == "index.html":
                                    value = "index_2.html"
                                self.dictionary[key] = value
                # Sort self.dictionary by key length descending
                self.dictionary = dict(sorted(self.dictionary.items(), key=lambda item: len(item[0]), reverse=True))
                print(f"Loaded {len(self.dictionary)} dictionary entries")
            else:
                print("Warning: dictionary.csv not found, no replacements will be applied")
        except Exception as e:
            print(f"Error loading dictionary: {e}")
    
    def apply_dictionary_replacements(self, content: str) -> str:
        """
        Apply dictionary replacements to content.
        
        Args:
            content: The content to process
            
        Returns:
            str: Content with dictionary replacements applied
        """
        for old_text, new_text in self.dictionary.items():
            content = content.replace(old_text, new_text)
        return content
    
    def process_index_html(self, file_path: str) -> bool:
        """
        Process index.html file by applying dictionary replacements to each line.
        
        Args:
            file_path: Path to the index.html file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply dictionary replacements to each line
            processed_lines = []
            for line in lines:
                processed_line = self.apply_dictionary_replacements(line)
                processed_lines.append(processed_line)
            
            # Write the processed lines to index_2.html instead of overwriting the original file
            output_path = os.path.join(os.path.dirname(file_path), "index_2.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(processed_lines)
            
            return True
        except Exception as e:
            print(f"Error processing index.html {file_path}: {e}")
            return False
    
    def process_other_html(self, file_path: str) -> bool:
        """
        Process other HTML files by:
        1. Reading corresponding .txt file and wrapping each line in <div> tags
        2. Replacing content between <main> tags
        3. Applying dictionary replacements
        4. Saving as XXXX_2.html
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the base name without extension
            base_name = os.path.splitext(file_path)[0]
            txt_file_path = base_name + '.txt'
            
            # Check if corresponding .txt file exists
            if not os.path.exists(txt_file_path):
                print(f"Warning: {txt_file_path} not found, skipping {file_path}")
                return False
            
            skip_line_index = 0
            txt_lines = []
            # Read the .txt file and wrap each line in <div> tags
            with open(txt_file_path, 'r', encoding='utf-8') as f:
                for i in range(8):
                    line = next(f)
                    txt_lines.append(line)
                    current_line = line.strip()
                    if current_line == "手機掃碼閱讀":
                        skip_line_index = i
                    if '章' in current_line:
                        skip_line_index = i
                txt_lines.extend(f.readlines())
            
            # Wrap each line in <div> tags
            wrapped_content = ""
            for i, line in enumerate(txt_lines):
                if(skip_line_index >= i):
                    continue
                line = line.strip()
                if line:  # Only process non-empty lines
                    if wrapped_content == "":
                        wrapped_content += f'<h2>{line}</h2>\n'
                    else:
                        wrapped_content += f'<div style="margin-bottom:20px;">{line}</div>\n'                        
            
            # Read the HTML file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace content between <main> tags
            # Use regex to find and replace content between <main> and </main>
            main_pattern = r'<main[^>]*>.*?</main>'
            main_replacement = f'<article id="content" style="line-height: 2.4; outline: 0px; font-size: x-large; padding-left: 10%; padding-right: 10%;" class="scrollbox" tabindex="1"><main>\n{wrapped_content}</main></article>'
            
            # Find the main tag pattern
            match = re.search(main_pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                # Replace the content between main tags
                html_content = re.sub(main_pattern, main_replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
            else:
                # If no main tag found, append the content at the end
                html_content += f"\n<main>\n{wrapped_content}</main>"
            
            # Apply dictionary replacements
            html_content = self.apply_dictionary_replacements(html_content)
            
            # Generate output filename (XXXX_2.html)
            output_path = base_name + '_2.html'
            
            # Write the processed content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error processing HTML file {file_path}: {e}")
            return False
    
    def __call__(self, file_path: str) -> bool:
        """
        Process a single HTML file.
        
        Args:
            file_path: Path to the HTML file to process
            
        Returns:
            bool: True if successful, False otherwise
        """
        filename = os.path.basename(file_path).lower()
        # Get the folder path and store it to self
        folder_path = os.path.dirname(os.path.abspath(file_path))
        if not hasattr(self, 'folder_path') or self.folder_path != folder_path:
            self.folder_path = folder_path
            self.load_dictionary()
        
        if filename == 'index.html':
            return self.process_index_html(file_path)
        else:
            return self.process_other_html(file_path)



