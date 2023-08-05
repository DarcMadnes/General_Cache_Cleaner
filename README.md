# gcc.py
This tool is designed to specifically target the cache in your system.  a normal run takes around 50 seconds (my system was already cleaned) - i7 4790k 

ATM it targets cache in the following locations: localtemp; windows temp; dns cache, winstore app cache (for some reason my system is gathering cache there, evne though im not using it);
Releases, renews ipconfig etc; It's going to run disk.cleanup on all of your drives.. might get it to defrag HDD's and optimise SSD"s in the future

NOTE1: This tool will change the frequency at which you can create restore points, delete old restore points, and after a small delay will create a new one with that specific moment's date and time (just in case you need to reset b4 this whole cleanup happened.
NOTE2: this tool will get the curretly logged user, ask for your password, doesn't store, send, collect any data

MEGA NOTE: the code is splitted due to some errors in vscode...
