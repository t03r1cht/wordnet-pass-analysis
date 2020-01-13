import datetime
import shutil
import sys
import unicodedata
import os
import platform
import re


def log_ok(s):
    """
    Print a success log message with timestamp.
    """
    print("[  {0}][+] {1}".format(get_curr_time_str(), s))


def log_err(s):
    """
    Print a error log message with timestamp.
    """
    print("[  {0}][-] {1}".format(get_curr_time_str(), s))


def log_status(s):
    """
    Print a status log message with timestamp.
    """
    print("[  {0}][*] {1}".format(get_curr_time_str(), s))


def remove_control_characters(s):
    """
    Remove control characters from a string. Return the sanitized string.
    """
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def get_curr_time():
    """
    Return the current time in datetime format.
    """
    return datetime.datetime.now()


def get_curr_time_str():
    """
    Return the current time as a string.
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H.%M.%S")


def get_shell_width():
    """
    Return the number of colums in the current shell view.
    """
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def clear_terminal():
    """
    Clear the terminal. This is required to properly display the stats while running.
    """
    os.system("clear") if platform.system(
    ) == "Linux" or platform.system() == "Darwin" else os.system("cls")


def get_txt_files_from_dir(path):
    """
    Return all txt filenames from a given directory.
    """
    dir_content = os.listdir(path)
    dir_txt_content = []
    for f in dir_content:
        if f.endswith(".txt"):
            dir_txt_content.append(f)
    return dir_txt_content


def format_number(n):
    """
    Transform big numbers into dotted numbers for better readability. Returns a string.
    """
    return re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(n))
