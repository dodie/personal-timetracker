class TextDecorator:

    error_marker_name = "underline"

    def __init__(self, scrolled_text):
        self.scrolled_text = scrolled_text
        self.scrolled_text.tag_configure(TextDecorator.error_marker_name, underline=True, foreground="red")


    def clear_errors(self):
        self.scrolled_text.edit_modified(0)
        self.scrolled_text.tag_remove(TextDecorator.error_marker_name, "1.0", "end")

    def show_error(self, line_number):
        self._ensure_in_range(line_number)
        self._add_line_marker(TextDecorator.error_marker_name, line_number)

    def _ensure_in_range(self, line_number):
        lines = self.scrolled_text.get("1.0", "end-1c").split("\n")
        if len(lines) < line_number:
            raise ValueError(f"Line number {line_number} is out of range")

    def _add_line_marker(self, marker_name, line_number):
        start_idx = f"{line_number}.0"
        end_idx = f"{line_number}.end"
        self.scrolled_text.tag_add(marker_name, start_idx, end_idx)

