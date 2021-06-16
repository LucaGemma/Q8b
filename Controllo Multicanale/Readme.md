#Controllo Multicanale
_Log_ folder : contains all measurements logs done at the BO1 lab by voltage driving a single MZI, with different input and output fiber (CIS & Trans).

_Figures_ folder : contains the images produced by the file _Controllo Multicanale - onda triangolare.ipynb_.

_Controllo Multicanale - onda triangolare.ipynb_ : an interactive python notebook for voltage driving the specified channels of the Q8b driver, from a sweep from "voltage_start" to "voltage_stop" and back to "voltage_start". It measures the voltages and currents, save them on file and visualize them on plots. 

_Plot generator.ipynb_ : an interactive python notebook that opens te .txt data file, builds the original data, plot them and save the resulting images. 

_Mass File Renamer.ipynb_ : an interactive python notebook that collectively rename all the .txt contained in the _Log_ folder. Used to ensure that alle the .txt files obey to the predefined nomenclature. E.g.: ['Multiple', 'channels', 'control', '20', '01', '2021', '17', '16', '30']).
