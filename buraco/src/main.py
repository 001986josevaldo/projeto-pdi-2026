import os
import sys
import tkinter as tk

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from buraco.src.ui.ui import SmartCityUI


def main():
    root = tk.Tk()
    SmartCityUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()