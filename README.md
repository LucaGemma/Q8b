# Q8b
Python architecture for sourcing, sensing and controlling single or multiple MZIs through the Q8b driver module from Qontrol Ltd. 
(https://qontrol.co.uk/product/q8b/)

The system is able to: 
- source and voltage control one MZI through the proper Q8b output and retrieve voltage and current measurements from the Q8b and voltage measurements from a Picoscope 4224 oscilloscope
- source and voltage control multiple MZIs through the proper Q8b output and retrieve voltage and current measurements from the Q8b and voltage measurements from a Picoscope 4224 oscilloscope
- produce log files and later build plots from such files
- simulate a single MZI with tunable parameters and plot dinamically its output
- simulate multiple MZIs with tunable parameters and plot dinamically their output 

Each measurement is saved with a pre-determined formatting into .txt files and plotted in a MATLab-like plot.

The entire architecture is tested through Jupyter Notebook and in the "MyCustomPackage", by running the _Required Packages.ipynb_ you can install all the required packages.
Finally, all the custom functions are collected together in the _mycustommodule.com_ custom module.
