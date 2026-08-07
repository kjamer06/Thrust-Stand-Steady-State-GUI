import dearpygui.dearpygui as dpg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from pathlib import Path


from core.state import state

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIRECTORY / "data"
DATA_DIR.mkdir(exist_ok=True)

def plot_takeoff():
    
    with dpg.plot(label="Takeoff Thrust Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Thrust (N)")

        dpg.add_line_series(state.time_plot, state.thrust_plot, parent=y_axis)

    with dpg.plot(label="Takeoff Power Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Power (W)")

        dpg.add_line_series(state.time_plot, state.power_plot, parent=y_axis)
    
    with PdfPages(DATA_DIR / "Takeoff Plots.pdf") as pdf:
        plt.figure()
        plt.plot(state.time_plot, state.thrust_plot, color='r')
        plt.ylabel("Thrust (N)")
        plt.xlabel("Time (s)")
        plt.title("Takeoff Thrust Plot")
        pdf.savefig()
        plt.close()

        plt.figure()
        plt.plot(state.time_plot, state.power_plot, color='g')
        plt.ylabel("Power (W)")
        plt.xlabel("Time (s)")
        plt.title("Takeoff Power Plot")
        pdf.savefig()
        plt.close()

    data = {
        "Thrust": state.thrust_plot,
        "Power": state.power_plot,
        "Time": state.time_plot
    }
    dataframe = pd.DataFrame(data)
    csv_path = DATA_DIR / "takeoff.csv"
    dataframe.to_csv(csv_path)

def plot_hover():
    pass

def plot_cruise():
    
    with dpg.plot(label="Cruise Thrust Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Velocity (m/s)")

        dpg.add_line_series(state.time_plot, state.thrust_plot, parent=y_axis)
    with dpg.plot(label="Cruise Altitude Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Altitude (m)")

        dpg.add_line_series(state.time_plot, state.altitude_plot, parent=y_axis)

    with dpg.plot(label="Cruise Power Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Power (W)")

        dpg.add_line_series(state.time_plot, state.power_plot, parent=y_axis)

    with PdfPages(DATA_DIR / "Cruise Plots.pdf") as pdf:
        plt.figure()
        plt.plot(state.time_plot, state.thrust_plot, color='r')
        plt.ylabel("Thrust (N)")
        plt.xlabel("Time (s)")
        plt.title("Cruise Thrust Plot")
        pdf.savefig()
        plt.close()

        plt.figure()
        plt.plot(state.time_plot, state.altitude_plot, color='g')
        plt.ylabel("Altitude (m)")
        plt.xlabel("Time (s)")
        plt.title("Cruise Altitude Plot")
        pdf.savefig()
        plt.close()

        plt.figure()
        plt.plot(state.time_plot, state.power_plot, color='b')
        plt.ylabel("Power (W)")
        plt.xlabel("Time (s)")
        plt.title("Cruise Power Plot")
        pdf.savefig()
        plt.close()
    
    data = {
        "Thrust": state.thrust_plot,
        "Power": state.power_plot,
        "Time": state.time_plot
    }
    dataframe = pd.DataFrame(data)
    csv_path = DATA_DIR / "cruise.csv"
    dataframe.to_csv(csv_path)

def plot_landing():
    with dpg.plot(label="Landing Altitude Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Altitude (m)")

        dpg.add_line_series(state.time_plot, state.altitude_plot, parent=y_axis)

    with dpg.plot(label="Landing Power Data", parent="plot_windows"):
        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Power (W)")

        dpg.add_line_series(state.time_plot, state.power_plot, parent=y_axis)
    with PdfPages(DATA_DIR / "Landing Plots.pdf") as pdf:
        plt.figure()
        plt.plot(state.time_plot, state.altitude_plot, color='r')
        plt.ylabel("Altitude (m)")
        plt.xlabel("Time (s)")
        plt.title("Landing Altitude Plot")
        pdf.savefig()
        plt.close()

        plt.figure()
        plt.plot(state.time_plot, state.power_plot, color='g')
        plt.ylabel("Power (W)")
        plt.xlabel("Time (s)")
        plt.title("Landing Power Plot")
        pdf.savefig()
        plt.close()

        
    data = {
        "Thrust": state.thrust_plot,
        "Power": state.power_plot,
        "Time": state.time_plot
    }
    
    dataframe = pd.DataFrame(data)
    csv_path = DATA_DIR / "landing.csv"
    dataframe.to_csv(csv_path)