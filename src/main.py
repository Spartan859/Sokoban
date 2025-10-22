
import sys
import argparse
import tkinter as tk
from SokobanSolver import SokobanSolver
from SokobanGUI import SokobanGUI



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sokoban Solver GUI")
    parser.add_argument('--debug', action='store_true', help='启用A*调试输出')
    args = parser.parse_args()

    Sokoban_default = '''
######
##  .#
# $ ##
#@#  #
#    #
######'''.splitlines()[1:]
    root = tk.Tk()
    app = SokobanGUI(root, Sokoban_default, debug=args.debug)
    root.mainloop()