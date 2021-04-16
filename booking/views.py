from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import *
from datetime import datetime, timedelta, date
from dateutil import parser
# DB call methods imports
from .dbcalls import *

# Create your views here.
#parser.parse(date).strftime("%a")

def Script(request):
    train = Trains(train_no = '12345',train_name = 'Test Train',running_day = 'Mon',seats_per_coach = 72,total_coaches = 10)
    train.save()
    s1 = Stations(station_id = 'CLT', station_name = 'Calicut')
    s1.save()
    s2 = Stations(station_id = 'CBE', station_name = 'Coimbatore')
    s2.save()
    s3 = Stations(station_id = 'MAS', station_name = 'Chennai')
    s3.save()
    admin = User(phone_no = '8888888888', name='Admin', otp = '1234', is_admin = True)
    admin.save()
    t1 = TrainTimeTable(
        train_no = train,
        station_id = s1,
        arr_time = datetime.now(),
        dep_time = datetime.now()+timedelta(minutes=5),
        running_day = 'Mon'
    )
    t1.save()
    t2 = TrainTimeTable(
        train_no = train,
        station_id = s2,
        arr_time = datetime.now()+timedelta(minutes=60),
        dep_time = datetime.now()+timedelta(minutes=65),
        running_day = 'Mon'
    )
    t2.save()
    t3 = TrainTimeTable(
        train_no = train,
        station_id = s3,
        arr_time = datetime.now()+timedelta(minutes=180),
        dep_time = datetime.now()+timedelta(minutes=185),
        running_day = 'Mon'
    )
    t3.save()
    return HttpResponse('Fuck')


def HomePage(request):
    '''
        Gives a dropdown lists of all the major actions
    '''
    if request.method == 'POST':
        form = HomePageFrom(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            url = {
                'Search Trains':'/search',
                'Book Ticket':'/book',
                'Live Status':'/livestatus',
                'Change Status':'/admin',
                'Show Bookings':'/history',
            }
            return HttpResponseRedirect(url.get(choice,''))
        else:
            return HttpResponse('Error in Request')
    else:
        form = HomePageFrom()
        context = {
            'form': form,
            'message': 'Select Action',
        }
        return render(request,'submitformwithmessage.html',context)

def CombineTrainData(from_stn_list, to_stn_list,from_stn,to_stn):
    '''
        Given the list of all trains at station A and B
        combines and gives the list of trains running from A to B
    '''
    trains = {
        "status": True,
        "from": from_stn,
        "to": to_stn,
        "Trains": [],
    }
    for traina in from_stn_list:
        for trainb in to_stn_list:
            if traina.station_id == trainb.station_id:
                continue
            if traina.train_no == trainb.train_no and traina.dep_time < trainb.dep_time:
                trains["Trains"].append([traina.dep_time,trainb.dep_time])
    return trains

def SearchTrain(request):
    '''
        Base Search Function to search trains and list them
    '''
    if request.method == 'POST':
        form = TrainSearchForm(request.POST)
        date_today = date.today()
        if form.is_valid():
            if form.cleaned_data['travel_date'] < date_today:
                return HttpResponse("Can't show past trains")
            from_stn = form.cleaned_data['train_from_stn']
            to_stn = form.cleaned_data['train_to_stn']
            from_stn_list = GetTrainsByStationIdAndDay(from_stn, GetDay(form.cleaned_data['travel_date']))
            to_stn_list = GetTrainsByStationId(to_stn)
            return JsonResponse(CombineTrainData(from_stn_list,to_stn_list,from_stn,to_stn))
        else:
            return HttpResponse("Error in Request")
    else:
        form = TrainSearchForm()
        context ={
            'form': form,
        }
    return render(request, 'submitform.html', context)

def FormatTicketData(user):
    '''
        Once the user is verified by OTP this gets all the tickets in a dict to be returned at a JSON object
    '''
    tickets = GetTicketsByPhoneNo(user.phone_no)
    bookings = {
        'status': True,
        'phone_no': user.phone_no,
        'name': user.name,
        'tickets': [],
    }
    for ticket in tickets:
        new_ticket = {
            'name': ticket.name,
            'train_no': ticket.train_no.train_no,
            'date':str(ticket.date),
            'seat':ticket.seat_no,
            'coach':ticket.coach_no,
        }
        bookings['tickets'].append(new_ticket)
    return bookings


def Bookings(request):
    '''
        Intermediate funtions for the task to see all the ticket history
        Once the user is verified Calls another fuction to get ticket details and returns the JSON object
    '''
    if request.session.has_key('otp') and request.session.has_key('phone_no'):
        user = GetUserById(request.session['phone_no'])
        request.session['history_flag'] = False
        request.session.clear()
        return JsonResponse(FormatTicketData(user))
    else:
        return HttpResponse('Error in Request')



def ShowBookingHistory(request):
    '''
        Starting Endpoint to show the booking history
    '''
    if request.method == 'POST':
        form = OnlyPhoneForm(request.POST)
        if form.is_valid():
            request.session['phone_no'] = form.cleaned_data['phone_no']
            return HttpResponseRedirect('/otp')
        else:
            return HttpResponse('Error in Request')
    else:
        request.session['history_flag'] = True
        form = OnlyPhoneForm()
        context = {
            'form': form,
            'message': 'Enter your Phone No',
        }
        return render(request, 'submitformwithmessage.html',context)


def CalculateCost(form):
    '''
        Can write a logic for price
        but for the time being a static value
    '''
    return 100

def GetBookingDetails(form):
    '''
        Helper function
    '''
    return {
        'name': form.cleaned_data.get('name'),
        'phone_no': form.cleaned_data.get('phone_no'),
        'train_no': form.cleaned_data.get('train_no'),
        'date': str(form.cleaned_data.get('date')),
        'cost': CalculateCost(form),
    }

def BookTicket(request):
    '''
        Takes in basic details 
        scope of improvement: with more UI functionalities we can encourage 
        more passengers in a single ticket
    '''
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            details = GetBookingDetails(form)
            validity = CheckTrainValidity(details['train_no'],GetDateFromString(details['date']))
            if not validity['validity']:
                return HttpResponse(validity['message'])
            request.session['details'] = details
            request.session['cost'] = details['cost']
            request.session['phone_no'] = details['phone_no']
            return HttpResponseRedirect('/otp')
        else:
            return HttpResponse('Error in Request')
    else:
        form = BookingForm()
        context = {
            'form': form,
            'message': 'Enter the details /n',
        }
        request.session['booking_flag']=True
        return render(request,'submitformwithmessage.html',context)

def NewUser(request):
    '''
        If a new phone No. pops up for which the user does not exist then this will take the name
        and register the user. After all we need more and more users xD
    '''
    if request.method == 'POST':
        form = OnlyNameForm(request.POST)
        if form.is_valid() and request.session.has_key('phone_no'):
            UpdateUserName(request.session['phone_no'],form.cleaned_data['name'])
            return HttpResponseRedirect('/otp')
        else:
            return HttpResponse('Error in Request')
    else:
        if request.session.has_key('phone_no'):
            phone_no = request.session['phone_no']
            form = OnlyNameForm()
            context = {
                'form': form,
                'message': 'What is the Name associated with the phone No. '+str(phone_no),
            }
            return render(request, 'submitformwithmessage.html', context)
        else:
            return HttpResponse('No phone No Found!')


def VerifyOtp(request):
    '''
        Takes in the otp from the user and depending on from where the request came
        directs the request accordingly. Currently using session variables which not the best option but
        lack of proper front end this was the way to go
    '''
    if request.method == 'POST':
        form = OtpForm(request.POST)
        if form.is_valid() and request.session.has_key('phone_no'):
            phone_no = request.session['phone_no']
            user = GetUserById(phone_no)
            if user.otp == form.cleaned_data['otp']:
                request.session['otp'] = True
                if request.session.has_key('booking_flag') and request.session['booking_flag']:
                    return HttpResponseRedirect('/payment')
                elif request.session.has_key('history_flag') and request.session['history_flag']:
                    return HttpResponseRedirect('/bookings')
                elif request.session.has_key('admin_flag') and request.session['admin_flag']:
                    return HttpResponseRedirect('/update')
                else:
                    return HttpResponse('Request from unknown source')
            else:
                return HttpResponse("Wrong Otp")
        else:
            return HttpResponse("Error in Request")
    else:
        if request.session.has_key('phone_no'):
            phone_no = request.session['phone_no']
            user, new_user = GetOrCreateUserById(phone_no = phone_no)
            if new_user or user.name == 'jane doe':
                return HttpResponseRedirect('/newuser')
            GenerateOtp(user)
            form = OtpForm()
            context = {
                'form': form,
                'message': 'New Otp Has Been Sent to your Phone No, '+str(user.name),
            }
            return render(request,'submitformwithmessage.html',context)
        else:
            return HttpResponse('No Phone Found')
        

def PaymentGateway(request):
    '''
        Mock payemnt gatway
    '''
    if request.method == 'POST':
        ##Can write logic to check payment etc etc
        if request.session.has_key('details'):
            BookTicketAndSave(request.session['details'])
            request.session['booking_flag'] = False
            request.session.clear()
            return HttpResponse('Booked Sucessfully')
        else:
            return HttpResponse('No Details Available')
    else:
        if request.session.has_key('cost'):
            form = OnlyPhoneForm()
            context = {
                'form': form,
                'message': 'Please Pay Rupees '+str(request.session['cost']),
            }
            return render(request,'submitformwithmessage.html',context)
        else:
            return HttpResponse('We dont need Donations :)')

def FormatTrainStatus(status):
    '''
        Helper Function
    '''
    return {
        'started':status.started,
        'ended': status.ended,
        'train_no': status.train_no.train_no,
        'last_station': status.last_station.station_name,
        'delayed': status.delayed,
    }

def TrainLiveStatus(request):
    '''
        Basic endpoint to see the live status of a train
    '''
    if request.method == 'POST':
        form = TrainNoAndDateForm(request.POST)
        if form.is_valid():
            train_no = form.cleaned_data['train_no']
            date = form.cleaned_data['date']
            validity = CheckTrainValidity(train_no, date)
            if not validity['validity']:
                return HttpResponse(validity['message'])
            status = GetTrainStatus(train_no,date)
            return JsonResponse(FormatTrainStatus(status))
        else:
            return HttpResponse('Error in Request')
    else:
        form = TrainNoAndDateForm()
        context = {
            'form': form,
            'message': 'Select the train and running day',
        }
        return render(request,'submitformwithmessage.html',context)


def StartUpdate(request):
    '''
        Entry point to start the update of a trains live status
        takes in the admin phone number and redirects to next step to get details 
    '''
    if request.method == 'POST':
        form = OnlyPhoneForm(request.POST)
        if form.is_valid():
            phone_no = form.cleaned_data['phone_no']
            if IsAdmin(phone_no):
                request.session['phone_no'] = phone_no
                return HttpResponseRedirect('/otp')
            else:
                return HttpResponse('Sorry you are not an Admin')
        else:
            return HttpResponse('Error in Request')
    else:
        form = OnlyPhoneForm()
        context = {
            'form': form,
            'message': 'Enter the Admin Phone No.'
        }
        request.session['admin_flag'] = True
        return render(request, 'submitformwithmessage.html', context)


def Update(request):
    '''
        Currently very basic method used to update
        asking for the train no and date
        and then showing the next station after the last updated station
        and take in the number of mimnutes it was late to arrive
    '''
    if request.method == 'POST':
        form = TrainNoAndDateForm(request.POST)
        if form.is_valid():
            train_no = form.cleaned_data['train_no']
            date = form.cleaned_data['date']
            validity = CheckTrainValidity(train_no,date)
            if not validity['validity']:
                return HttpResponse(validity['message'])
            next_station = GetNextUpdateStation(train_no, date)
            if not next_station['flag']:
                return HttpResponse(next_station['message'])
            request.session['train_no'] = train_no
            request.session['date'] = str(date)
            request.session['next_station'] = next_station['next_station'].station_id
            request.session['next_station_name'] = next_station['next_station'].station_name
            request.session['ended'] = next_station['ended']
            return HttpResponseRedirect('/makeupdate')
        else:
            return HttpResponse('Error in Request')
    else:
        form = TrainNoAndDateForm()
        context = {
            'form': form,
            'message': 'Enter the details of the train to update'
        }
        return render(request, 'submitformwithmessage.html', context)


def MakeUpdate(request):
    '''
        Once we have the number of minutes the train was late and the train details
        we update the train status including all the flags available
    '''
    if request.method == 'POST':
        form = LateByMinutesForm(request.POST)
        if form.is_valid():
            late_by = form.cleaned_data['late_by']
            delayed = True
            if late_by <= 0:
                delayed = False
            train_no = request.session['train_no']
            date = GetDateFromString(request.session['date'])
            ended = request.session['ended']
            next_station = GetStationById(request.session['next_station'])
            UpdateTrainStatus(train_no,date,next_station,delayed,ended)
            request.session['admin_flag'] = False
            request.session.clear()
            return HttpResponse('Updated')
        else:
            request.session['admin_flag'] = False
            request.session.clear()
            return HttpResponse('Error in Request')
    else:
        if not request.session.has_key('train_no') or not request.session.has_key('next_station'):
            return HttpResponse('Request from Unknown Source')
        form = LateByMinutesForm()
        context = {
            'form': form,
            'message': 'How Late did the train reach '+str(request.session['next_station_name']),
        }
        return render(request,'submitformwithmessage.html',context)
