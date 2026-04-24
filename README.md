# py-network-timer

A simple GUI program that allows the scheduling of internet 
connection/disconnection. Intended for internet intake control.

# how to use

This tools is comprised of two tabs: A status tab and a schedule tab.

The status tab has checkboxes for your wifi and internet devices, allowing you
to select one or the other to disconnect on the schedule, even while the 
schedule is running.

Clicking "Start Schedule" will load the schedule you've entered on the 
schedule tab and begin executing it. Clicking the "Stop Schedule" button will
reconnect any disconnected devices and stop the schedule.

When the program is running, a status of the program will display indicating
if the network devices are disconnected and when they will reconnect, or if
devices are not scheduled to be disconnected at the current time.

On the schedule tab, you can define 3 different types of disconnection 
intervals: Daily, Weekly, or by specific date. To add a specific interval, 
select the desired interval type and click "add interval".

Start times must be before end times in each interval, so if you find that you
are unable to edit a time, make sure it doesn't try to go beyond the other time
(end time before start time, or start time after end time).

To remove intervals, simply select the rows you want to remove and click
"remove interval". 

This has been my first project thought up and executed from start to finish.
Feedback is greatly appreciated, thank you for checking out my project!

