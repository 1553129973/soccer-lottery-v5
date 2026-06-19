# -*- coding: utf-8 -*-
"""Build V5 project files"""
import os, json

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE, "history"), exist_ok=True)

# Write app.py
with open(os.path.join(BASE, "app.py"), "w", encoding="utf-8") as f:
    f.write(open(os.path.join(BASE, "_app.py.txt"), "r", encoding="utf-8").read())

print("Build complete!")
