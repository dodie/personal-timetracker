import tkinter as tk

class TextEditingBasics:
    def __init__(self, scrolled_text):
        self.scrolled_text = scrolled_text

    def enable(self):
        self.scrolled_text.bind("<Control-a>", select_all)
        self.scrolled_text.bind("<Control-BackSpace>", delete_previous_word)

def select_all(event):
    event.widget.tag_add(tk.SEL, "1.0", tk.END)
    event.widget.mark_set(tk.INSERT, "1.0")
    event.widget.see(tk.INSERT)
    return 'break'

def delete_previous_word(event):
    insert_index = event.widget.index(tk.INSERT)
    
    row, col = map(int, insert_index.split('.'))
    line_text = event.widget.get(f"{row}.0", insert_index)
    last_space = line_text.rfind(' ')
    
    if last_space == -1:
        # If no space found, delete from the start of the line
        word_start_index = f"{row}.0"
    else:
        # Adjust index to delete the space as well
        word_start_index = f"{row}.{last_space}"
    
    event.widget.delete(word_start_index, insert_index)
    return "break"
