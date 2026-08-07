import dearpygui.dearpygui as dpg
from config.settings import THRUST_MAX, POWER_MAX
from gui.callbacks import drone_specifications_callback, takeoff_button_callback, hover_button_callback, cruise_button_callback
from gui.callbacks import land_button_callback, add_button_callback, undo_button_callback, clear_button_callback, start_button_callback, update_button_callback, pid_menu_callback, pid_submit_callback
from gui.helpers import load_texture, add_scaled_image
from core.state import state

def show_drone_specs():
    dpg.configure_item("Drone Specifications", show=True)

def initialize_GUI():
    dpg.create_context()
    load_texture("assets/cat_2.jpg", "auburn_logo_image")

######################################################
# POPUP WINDOWS
######################################################

    with dpg.window(tag="Drone Specifications",modal=True,height=200,width=350,pos=(470, 250),label="Drone Specifications",no_close=True,no_move=True,no_resize=True):
            dpg.add_text("Input drone specifications here")
            dpg.add_input_float(label="Max Thrust (N)", tag="max_thrust_input", default_value=THRUST_MAX, format="%.2f")
            dpg.add_input_float(label="Max Power (W)",tag="max_power_input", default_value=POWER_MAX,format="%.2f")
            dpg.add_input_float(label="Mass (kg)", tag="mass_input", default_value=0, format="%.2f")

            dpg.add_button(label="Submit", callback= drone_specifications_callback, tag="submit_specs_button")

    with dpg.window(tag="PID Config",modal=True,height=200,width=350,pos=(470, 250),label="PID Config",no_move=True,no_resize=True, show=False):
                dpg.add_text("Takeoff PID")
                dpg.add_input_float(label="P", tag="takeoff_p", default_value=state.takeoff_PID[0], format="%.2f")
                dpg.add_input_float(label="I", tag="takeoff_i", default_value=state.takeoff_PID[1], format="%.2f")
                dpg.add_input_float(label="D", tag="takeoff_d", default_value=state.takeoff_PID[2], format="%.2f")

                dpg.add_text("Hover PID")
                dpg.add_input_float(label="P", tag="hover_p", default_value=state.hover_PID[0], format="%.2f")
                dpg.add_input_float(label="I", tag="hover_i", default_value=state.hover_PID[1], format="%.2f")
                dpg.add_input_float(label="D", tag="hover_d", default_value=state.hover_PID[2], format="%.2f")

                dpg.add_text("Cruise Alt PID")
                dpg.add_input_float(label="P", tag="cruise_alt_p", default_value=state.cruise_alt_PID[0], format="%.2f")
                dpg.add_input_float(label="I", tag="cruise_alt_i", default_value=state.cruise_alt_PID[1], format="%.2f")
                dpg.add_input_float(label="D", tag="cruise_alt_d", default_value=state.cruise_alt_PID[2], format="%.2f")

                dpg.add_text("Cruise Vel PID")
                dpg.add_input_float(label="P", tag="cruise_vel_p", default_value=state.cruise_vel_PID[0], format="%.2f")
                dpg.add_input_float(label="I", tag="cruise_vel_i", default_value=state.cruise_vel_PID[1], format="%.2f")
                dpg.add_input_float(label="D", tag="cruise_vel_d", default_value=state.cruise_vel_PID[2], format="%.2f")

                dpg.add_text("Landing PID")
                dpg.add_input_float(label="P", tag="landing_p", default_value=state.landing_PID[0], format="%.2f")
                dpg.add_input_float(label="I", tag="landing_i", default_value=state.landing_PID[1], format="%.2f")
                dpg.add_input_float(label="D", tag="landing_d", default_value=state.landing_PID[2], format="%.2f")
    
                dpg.add_button(label="Submit", callback= pid_submit_callback, tag="submit_PID_button")

#######################################################
# MAIN WINDOW
#######################################################
    
    with dpg.window(tag="main_window", label="TYTO Series 1585 Thrust Stand Control Application", pos=(0, 0), width=1310, height=725, no_move=True, no_resize=True, no_collapse=True, no_close=True):
        dpg.add_spacer(height=15)

        #######################################################
        # INPUT SECTION
        #######################################################
        with dpg.child_window(tag="input_section", width=1300, height=190, border=True):
            
            with dpg.group(tag="dynamic_event_inputs"):
                dpg.add_text("To get started, build a sequence of missions in the mission builder window")

            with dpg.group(tag="select_event_menu", horizontal=True, pos=(0, 120)):
                dpg.add_button(label="Takeoff", height=50, width=70, callback=takeoff_button_callback, tag="takeoff_button")
                dpg.add_button(label="Hover", height=50, width=70, callback=hover_button_callback, tag="hover_button")
                dpg.add_button(label="Cruise",height=50,width=70,callback=cruise_button_callback,tag="cruise_button")
                dpg.add_button(label="Land", height=50, width=70, callback=land_button_callback, tag="land_button")

                dpg.add_spacer(width=50)

                dpg.add_button(label="Add", height=50, width=70, callback=add_button_callback, tag="add_button")
                dpg.add_button(label="Undo",height=50,width=70,callback=undo_button_callback,tag="undo_button")
                dpg.add_button(label="Clear",height=50,width=70,callback=clear_button_callback,tag="clear_button")
                dpg.add_button(label="Start", height=50, width=70, callback=start_button_callback, tag="start_button")

                dpg.add_spacer(width=30)

                dpg.add_button(label="Update", height=50, width=70, callback=update_button_callback, show=False, tag="update_button")
                
            with dpg.child_window(width=195, height=170, pos=(1050, 10)):
                add_scaled_image("auburn_logo_image", desired_width=154)              

        #######################################################
        # CONSOLE LOG (possibly graph)
        #######################################################
        with dpg.group(tag="lower_section", horizontal=True):
            with dpg.child_window(tag="plot_windows", width=1000, height=500, border=True):
                dpg.add_text("Run a simulation to see the plots")
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
    dpg.create_viewport(title='TYTO Series 1585 Thrust Stand Control Script', width=1333, height=768)

    with dpg.viewport_menu_bar():
        dpg.add_menu_item(label="Specs", callback=show_drone_specs)
        dpg.add_menu_item(label="PID", callback=pid_menu_callback)

    dpg.setup_dearpygui()
    dpg.set_primary_window("main_window", True)

    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()