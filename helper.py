import platform
import shutil
import os
import datetime


def sigint_handler(sig, frame):
    """
    Register the handler for the SIGINT signal.

    This is absolutely necessary to exit the program with Ctrl+C because a user easily misconfigure the
    programe (i.e. -d > 4) for it to result in a combinatorial explosion because of its recursion.
    """
    print()
    print("Caught Ctrl+C, shutting down...")
    cleanup()
    sys.exit(0)


def get_shell_width():
    """
    Return the number of colums in the current shell view.
    """
    cols, _ = shutil.get_terminal_size((80, 20))
    return cols


def get_curr_time():
    """
    Return the current time as a string.
    """
    return datetime.datetime.now().strftime("%Y%m%d_%H.%M.%S")


def clear_terminal():
    """
    Clear the terminal. This is required to properly display the stats while running.
    """
    os.system("clear") if platform.system(
    ) == "Linux" or platform.system() == "Darwin" else os.system("cls")


def update_stats(current, finished):
    """
    Print out the stats while the program is running.
    """
    if not args.subsume_for_classes:
        clear_terminal()
        print()
        print()
        c_t = get_curr_time()
        print("  WordNet Password Analysis // Time: %s" % c_t)
        print()
        global started
        print("  Started: \t%s" % started)
        print("  Processing: \t%s" % current)
        print("  Done: \t%d" % finished)
        print()


def inc_total_processed():
    """
    Increment the global variable to track the overall progress of processed lemmas.
    """
    global total_processed
    total_processed += 1


def inc_total_found():
    """
    Increment the global variable to track the passwords which could be found.
    """
    global total_found
    total_found += 1


def inc_total_not_found():
    """
    Increment the global variable to track the the passwords which could not be found.
    """
    global total_not_found
    total_not_found += 1
