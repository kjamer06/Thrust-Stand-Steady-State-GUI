# TYTO Thrust Stand Control Station
The purpose of this program is to generate accurate data measurements to calculate the efficiency of drone propellers and motors. This will be done by running simple drone simulations to generate efficiency data to make informed decisions about parts for any UAV. The simulations are a bit rudimentary as of July 15th, 2026 however they are a great starting point for deciding on UAV parts. This script was my first attempt at making a modular application, most notably the simulations can be edited and completely changed by changing the Python source code.

## Dependencies

The only dependencies you need is the ***latest version of Python*** installed on your computer and the ***TYTO Flightstand Software*** which requires Windows 10 or 11.

Links to both can be found below to install 

[Tyto Flightstand Software](https://www.tytorobotics.com/blogs/manuals-and-datasheets/software-download)

[Latest Python](https://www.python.org/downloads/)

## Getting Started

Clone the GitHub repository with the command 

`git clone https://github.com/kjamer06/Thrust-Stand-Steady-State-GUI` 

Once cloned run the virtual environment with the command 

`.venv/Scripts/activate`

After entering the venv, ensure that the Flightstand Software is running in the background as this script will not work without it.

Run main.py and you should be greeted with a screen that looks similar to the image below

image here