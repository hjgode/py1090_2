from curses import wrapper
import time

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # This raises ZeroDivisionError when i == 10.
    for i in range(0, 9):
        v = i-10
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))
        stdscr.refresh()
        time.sleep(2)

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
