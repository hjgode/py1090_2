# This tests that __all__ is correct, since we use below everything that should
# be imported:
from blessings import *

term = Terminal()
term.clear
print term.move(1, 1) + 'Hi'
print term.move(9, 9) + 'Mom'
