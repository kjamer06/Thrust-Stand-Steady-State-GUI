import dearpygui.dearpygui as dpg
from config.settings import THRUST_MAX, POWER_MAX
from gui.callbacks import drone_specifications_callback, takeoff_button_callback, hover_button_callback, cruise_button_callback, land_button_callback, add_button_callback, undo_button_callback, clear_button_callback, start_button_callback
from gui.helpers import load_texture, add_scaled_image
from core.state import state     
import random   

def initialize_GUI():
    dpg.create_context()

    load_texture("assets/cat.png", "cat_image")
    load_texture("assets/auburn_logo.png", "auburn_logo_image")

######################################################
# POPUP WINDOW FOR DRONE SPECIFICATIONS INPUT
######################################################

    with dpg.window(tag="Drone Specifications",modal=True,height=200,width=350,pos=(470, 250),label="Drone Specifications",no_close=True,no_move=True,no_resize=True):
            dpg.add_text("Input drone specifications here")
            dpg.add_input_float(label="Max Thrust (N)", tag="max_thrust_input", default_value=THRUST_MAX, format="%.2f")
            dpg.add_input_float(label="Max Power (W)",tag="max_power_input",default_value=POWER_MAX,format="%.2f")
            dpg.add_input_float(label="Mass (kg)", tag="mass_input", default_value=0, format="%.2f")

            dpg.add_button(label="Submit", callback= drone_specifications_callback, tag="submit_specs_button")

#######################################################
# MAIN WINDOW
#######################################################
    with dpg.window(tag="main_window", label="TYTO Series 1585 Thrust Stand Control Application", pos=(0, 0), width=1310, height=725, no_move=True, no_resize=True, no_collapse=True, no_close=True):

        #######################################################
        # INPUT SECTION
        #######################################################
        with dpg.child_window(tag="input_section", width=1300, height=190, border=True):
            
            with dpg.group(tag="upper_screen"):
                with dpg.group(tag="dynamic_event_inputs"):
                    dpg.add_text("To get started, build a sequence of missions in the mission builder window")

            with dpg.group(tag="select_event_menu", horizontal=True):
                dpg.add_button(label="Takeoff", height=50, width=70, callback=takeoff_button_callback, tag="takeoff_button")
                dpg.add_button(label="Hover", height=50, width=70, callback=hover_button_callback, tag="hover_button")
                dpg.add_button(label="Cruise",height=50,width=70,callback=cruise_button_callback,tag="cruise_button")
                dpg.add_button(label="Land", height=50, width=70, callback=land_button_callback, tag="land_button")

                dpg.add_spacer(width=50)

                dpg.add_button(label="Add", height=50, width=70, callback=add_button_callback, tag="add_button")
                dpg.add_button(label="Undo",height=50,width=70,callback=undo_button_callback,tag="undo_button")
                dpg.add_button(label="Clear",height=50,width=70,callback=clear_button_callback,tag="clear_button")
                dpg.add_button(label="Start", height=50, width=70, callback=start_button_callback, tag="start_button")
                """
                with dpg.child_window(width=195, height=170):
                    chance = random.randint(1,100)
                    if (chance <= 10):
                        add_scaled_image("cat_image", desired_width = 150)
                    else:
                        add_scaled_image("auburn_logo_image", desired_width=175)                
                """

        #######################################################
        # CONSOLE LOG
        #######################################################
        with dpg.group(tag="lower_section", horizontal=True):
            with dpg.child_window(tag="console_section", width=1000, height=500, border=True):
                dpg.add_text("Console")
        #######################################################
        # EVENTS SECTION
        #######################################################
            with dpg.child_window(tag="events_section", width=292, height=500, border=True):
                dpg.add_text("Select a mission objective to add into\n""the mission sequence")

                with dpg.child_window(width=275, height=420, tag="mission_window", border=True):
                    with dpg.group(tag="mission_window_display"):
                        dpg.add_text("Add an event to get started")

#########################################################
# VIEWPORT
#########################################################
    dpg.create_viewport(title='TYTO Series 1585 Thrust Stand Control Script', width=1330, height=750, resizable=False)

    dpg.setup_dearpygui()
    dpg.set_primary_window("main_window", True)

    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()