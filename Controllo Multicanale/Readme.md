Log: contiene log di misure fatte il 20/01/2021 al BO1, pilotando in tensione (sweep con onda triangolare) un Mach-Zehnder, cambiando fibra di input e fibra di output (CIS e Trans).

Figures: contiene le immagini prodotte da Controllo Multicanale - onda triangolare.ipynb.

Controllo Multicanale - onda triangolare.ipynb: Il programma controlla in tensione i canali specificati nella lista "channels" con uno sweep da "voltage_start'' a ''voltage_stop'' per poi tornare a "voltage_start'', legge le rispettive tensioni e correnti, le salva su file e le visualizza a video con grafici. 

Plot generator.ipynb: Il programma apre un file .txt di misure di sweep di tensione, ricostruisce le liste di misure originali, le plotta e ne salva le immagini. Ciascun plot può essere sovrapposto o affiancato. 

Mass File Renamer.ipynb: Il programma adegua tutti i .txt contenuti in Log, rinominandoli con lo stesso pattern ( da ['Multiple', 'channels', 'control', '2021', '1', '20', '12', '36', '52'] a ['Multiple', 'channels', 'control', '20', '01', '2021', '17', '16', '30']).
