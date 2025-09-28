import tkinter as tk

class TextEditingBasics:
    def __init__(self, scrolled_text):
        self.scrolled_text = scrolled_text

    def enable(self):
        self.scrolled_text.bind("<Control-a>", select_all)
        self.scrolled_text.bind("<Control-BackSpace>", delete_previous_word)
        self.scrolled_text.bind("<Control-x>", delete_current_line)

def select_all(event):
    event.widget.tag_add(tk.SEL, "1.0", tk.END)
    event.widget.mark_set(tk.INSERT, "1.0")
    event.widget.see(tk.INSERT)
    return 'break'

def delete_previous_word(event):
    insert_index = event.widget.index(tk.INSERT)
    
    row, col = map(int, insert_index.split('.'))
    line_text = event.widget.get(f"{row}.0", insert_index)
    
    # Find last separator, excluding separators immediately before the cursor
    separators = [' ', ':', '-', '_', '.', ',', ';', '!', '/', '\\', '|', '(', ')', '[', ']', '{', '}', '"', "'"]
    search_text = line_text.rstrip(''.join(separators))
    separator_positions = [search_text.rfind(sep) for sep in separators]
    last_space = max(separator_positions)
    
    if last_space == -1:
        # If no space found, delete from the start of the line
        word_start_index = f"{row}.0"
    else:
        # Adjust index to delete the space as well
        word_start_index = f"{row}.{last_space + 1}"
    
    event.widget.delete(word_start_index, insert_index)
    return "break"

def delete_current_line(event):
    insert_index = event.widget.index(tk.INSERT)
    row, col = map(int, insert_index.split('.'))
    
    # Get the start and end of the current line
    line_start = f"{row}.0"
    line_end = f"{row}.end"
    
    # Check if this is the last line in the document
    last_line = int(event.widget.index("end-1c").split('.')[0])
    
    if row < last_line:
        # Not the last line, delete including the newline character
        line_end = f"{row + 1}.0"
    elif row > 1:
        # Last line but not the only line, delete including the preceding newline
        line_start = f"{row - 1}.end"
    
    event.widget.delete(line_start, line_end)
    return "break"
