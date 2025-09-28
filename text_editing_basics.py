import tkinter as tk
import tkinter.font as tkFont

class TextEditingBasics:
    def __init__(self, scrolled_text):
        self.scrolled_text = scrolled_text
        self.default_font_size = 10
        self.current_font_size = self.default_font_size
        self.font_family = "Consolas"  # Default monospace font
        self._setup_font()

    def _setup_font(self):
        self.font = tkFont.Font(family=self.font_family, size=self.current_font_size)
        self.scrolled_text.configure(font=self.font)

    def enable(self):
        self.scrolled_text.bind("<Control-a>", select_all)
        self.scrolled_text.bind("<Control-BackSpace>", delete_previous_word)
        self.scrolled_text.bind("<Control-x>", delete_current_line)
        self.scrolled_text.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self.scrolled_text.bind("<Control-Key-0>", self._on_ctrl_zero)
        self.scrolled_text.bind("<Control-plus>", self._on_ctrl_plus)
        self.scrolled_text.bind("<Control-equal>", self._on_ctrl_plus)  # Handles Ctrl+= (shift+plus on US keyboards)
        self.scrolled_text.bind("<Control-minus>", self._on_ctrl_minus)

    def _on_ctrl_zero(self, event):
        self.reset_font_size()
        return "break"

    def _on_ctrl_plus(self, event):
        self.increase_font_size()
        return "break"

    def _on_ctrl_minus(self, event):
        self.decrease_font_size()
        return "break"

    def _on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.increase_font_size()
        else:
            self.decrease_font_size()
        return "break"

    def increase_font_size(self):
        if self.current_font_size < 24:
            self.current_font_size += 1
            self._update_font()

    def decrease_font_size(self):
        if self.current_font_size > 6:
            self.current_font_size -= 1
            self._update_font()

    def _update_font(self):
        self.font.configure(size=self.current_font_size)

    def reset_font_size(self):
        self.current_font_size = self.default_font_size
        self._update_font()

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
