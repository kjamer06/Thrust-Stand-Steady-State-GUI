from operator import pos

import dearpygui.dearpygui as dpg

class RecursiveButton:
    def __init__(self, name, pos=(0,0), height=50, width=50, parent=None):
        self.name = name
        self.pos = pos
        self.height = height
        self.width = width
        self.parent = parent

    def create_button(self):
        create_button = dpg.add_button(pos=self.pos, height=self.height, width=self.width, parent=self.parent, tag=self.name)