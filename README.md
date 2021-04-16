# Basic Train Search/Book/Live Status App

There are 5 Major Endpoints / Function:
-> Search Tarin
    This Endpoint takes train no and a date as input and shows a list of all the trains.
-> Book Train
    This Endpoints Basically books a ticket currently only for one passenger at a time.
    The ticket allocation is very simple just involving total No of coach and No of seats in each coach
    and tickts are given out lineraly. Not supporting Waiting list or rac.
    Tickets are booked for the entire jojurney (Frist station to last) 
    (its not a bug its a feature, its Corona you know)
    Besides truly handling half journey tickets involes much deeper algorithms including various types 
    of coaches etc etc. So I have kept it very simple here
-> Live Status
    This lets you select train and its running day and find its current live status.
-> Change Status
    This is more like an admin only end point. Users who are admin can update the status of a train from here.
-> Show Booking
    In this particular project the login system is basically Phone No and Otp based only. once the user enters the OTP, he/she can see the entire booking history

-> /script  endpoint is currently commented out in the url folder. It creates the basic data for the user       to play locally

In the booking folder is where the entire app lies.
The models.py contains all the models.
The dbcalls.py contains all the functions which involves interaction with the DB.
The views.py contains all the exposed endpoints.
The templates folder contains basic HTML files through which a very simple UI is made


Rest I have commented above each function for easier understanding

Drawbacks:
Due to lack of proper UI. Displaying of data isn't taken care of, instead the JSON struction is shown
Again due to lack of proper FE inputs are very strict (Could provide dynamic drop downs for station name options everwhere) and giving inputs could be made easy
