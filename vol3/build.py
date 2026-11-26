"""Build the English translation of Picross NP Vol. 2.  usage: python build.py [path/to/ROM]"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import npbuild

if __name__ == "__main__":
    npbuild.main(os.path.dirname(os.path.abspath(__file__)))
