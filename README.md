# phone-to-timing
Small script to synchronize Fritz!Box Call List to Timing.app on Mac

# Installation

Install the requirements.

# Configuration

Copy the configuration file `example.phonetotiming.ini` to your home directory and
rename it to `example.phonetotiming.ini`

Edit the contents:

    [main]
    password = <your Fritz!Box password here>
    firstrun = true

For the `password` set the correct Fritz!Box password. This is all you need to do.

The existence of `firstrun` indicates that the script has not run before. On the first run, the script will remove this
entry and instead add a `lastprocessed` entry which contains the Id of the most recent entry in the call list.

The `lastprocessed` entry will be updated by the script on every run to keep track which calls have been written to 
Timing.app already.

# Running for the First Time

After you have copied and edited the configuration file, run the script manually for the first time. (No worries! It will not write anything to Timing.app, yet, because the `firstrun` key exists!)

    $ ./phonetotiming.py
    \o/ - everything seems to work. The latest call on your call list has the Id 1568.

If you see this output, everything is working. The script has read the call list and updated the configuration file with the ID shown.
Every subsequent phone call will be sent to Timing.app in the next run of the script.

# Running Regularly

To make the script run regularly (default: every 10 minutes), edit the file `net.winklerweb.phonetotiming.plist` and in line 9 set the correct path to the phonetotiming.py script.

    $ cp net.winklerweb.phonetotiming.plist ~/Library/LaunchAgents/
    $ cd ~/Library/LaunchAgents
    $ launchctl load net.winklerweb.phonetotiming.plist 
    $ launchctl start net.winklerweb.phonetotiming.plist 
