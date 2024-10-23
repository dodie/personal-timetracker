#!/usr/bin/python3

# Each line is a time record or a command. Time records for the same label are aggregated.
# Time record is expected in the format of `hh:mm-hh:mm label`.
# Time records are accepted until EOF when a summary is printed.
#
# Can be used as a standalone script (reading from stdin) or as a module (calling calculate_total_grouped_by_labels).

from decimal import *

def parse_time(time_str):
    """Parses a time string in HH:MM format and returns the total minutes."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def calculate_time_diff(start, end):
    """Calculates the difference between two time strings in minutes."""
    return parse_time(end) - parse_time(start)

def convert_minutes_to_hours_decimal(minutes):
    """Converts minutes to hours in decimal format."""
    return round(Decimal(minutes) / 60, 2)

def format_time_to_hhmm(minutes):
    """Converts minutes to HH:MM format."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{int(hours):02d}:{int(mins):02d}"

def format_presence_time(total_hours):
    """Formats the presence time based on total time."""
    total_minutes = total_hours * 60
    start_morning = 8 * 60     # 08:00 in minutes
    end_morning = 12 * 60      # 12:00 in minutes
    start_afternoon = 13 * 60  # 13:00 in minutes

    if total_minutes <= 4 * 60:
        # If total time is less than or equal to 4 hours
        end_time = start_morning + total_minutes
        return f"08:00-{format_time_to_hhmm(end_time)}"
    else:
        # If total time is more than 4 hours
        remaining_minutes = total_minutes - (end_morning - start_morning)
        end_time = start_afternoon + remaining_minutes
        return f"08:00-12:00, 13:00-{format_time_to_hhmm(end_time)}"

def correct_rounding_error(data):
    """
    The total time should be representable exactly in whole minutes, and in hours of d.dd format.
    If this is not the case, add a few minutes to fix it.
    """
    total_time = Decimal(0)
    for label, time in data.items():
        total_time = total_time + Decimal(time)
    if not (total_time * 60) % 1 == 0:
        first_label = list(data.keys())[0]
        data[first_label] = Decimal(data[first_label]) + Decimal("0.01")
        correct_rounding_error(data)


def aggregate(data):
    """
    Aggregates the time records, performs rounding and returns the summary.
    """
    value = ""
    for label in data:
        data[label] = convert_minutes_to_hours_decimal(data[label])

    correct_rounding_error(data)

    total_time = 0
    for label, time in data.items():
        total_time = total_time + time

    sorted_data = {k: data[k] for k in sorted(data)}

    for label, time in sorted_data.items():
        value = value + (f"{label} {time} hours") + "\n"

    value = value + (f"---") + "\n"
    value = value + (f"TOTAL: {total_time} hours") + "\n"
    value = value + (f"Presence time: {format_presence_time(total_time)}") + "\n"
    return value


def record_time(command, data):
    try:
        parts = command.split(' ')
        times = parts[0]
        start, end = times.split('-')
        time_diff = calculate_time_diff(start, end)
        if not time_diff > 0:
            raise ValueError("Non-positive time diff.")
        label = ' '.join(parts[1:])

        if label in data:
            data[label] += time_diff
        else:
            data[label] = time_diff

    except ValueError:
        raise ValueError("Invalid format.")


def calculate_total_grouped_by_labels(input_string):
    data = {}
    lines = input_string.split('\n')
    error_lines = []
    for index, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        else:
            try:
                record_time(line, data)
            except ValueError:
                line_number = index + 1
                error_lines.append(line_number)
    if error_lines:
        raise InvalidFormatError("Invalid format.", error_lines)
    return aggregate(data)

class InvalidFormatError(Exception):
    def __init__(self, message, line_numbers):
        super().__init__(message)
        self.line_numbers = line_numbers


def main():
    data = {}
    try:
        while True:
            line = input().strip()
            if not line:
                continue
            else:
                record_time(line, data)
    except EOFError:
        print("------------")
    print(aggregate(data))


if __name__ == "__main__":
    main()
