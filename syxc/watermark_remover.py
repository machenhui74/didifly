#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from watermark_ui import WatermarkRemoverUI

def main():
    """程序入口点"""
    root = tk.Tk()
    app = WatermarkRemoverUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 