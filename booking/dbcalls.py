from .models import *
from datetime import date,datetime
from dateutil import parser
import datetime

'''
    Most of the Function are explanatory by the name it self.
    Those less obvious have been commented with
'''


def GetDay(date):
    return date.strftime('%a')

def GetStationById(station_id):
    return Stations.objects.get(station_id = station_id)

def GetDateFromString(date):
    arr = date.split('-')
    return datetime.date(int(arr[0]),int(arr[1]),int(arr[2]))

def GetTrainsByStationIdAndDay(station_id, running_day):
    return TrainTimeTable.objects.filter(station_id = station_id, running_day = running_day)

def GetTrainsByStationId(station_id):
    return TrainTimeTable.objects.filter(station_id=station_id)

def GetOrCreateUserById(phone_no):
    return User.objects.get_or_create(phone_no = phone_no)

def GetUserById(phone_no):
    return User.objects.filter(phone_no = phone_no).first()

def GetTicketsByPhoneNo(phone_no):
    return Ticket.objects.filter(phone_no = phone_no)

def UpdateUserName(phone_no, name):
    user = GetUserById(phone_no)
    user.name = name
    user.save()

def GenerateOtp(user):
    '''
        We will generate a random OTP and send a SMS
        Currently just saving it as 1234
    '''
    user.otp = 1234
    user.save()

def IsAdmin(phone_no):
    user = User.objects.filter(phone_no=phone_no).first()
    if user == None or user.is_admin == False:
        return False
    return True

def GetTrainById(train_no):
    return Trains.objects.filter(train_no = train_no).first()

def GetOrCreateTrainStatus(train_no, date):
    ID = str(train_no)+str(date)
    status, new_status = TrainStatus.objects.get_or_create(id = ID)
    if new_status:
        status.start_date = date
        status.id = ID
        status.train_no = GetTrainById(train_no=train_no)
        status.last_station = TrainTimeTable.objects.filter(train_no=train_no).order_by('arr_time').first().station_id
        status.save()
    return status

def GetTrainStatus(train_no, date):
    return TrainStatus.objects.filter(id = str(train_no)+str(date)).first()


def GetNextUpdateStation(train_no, date):
    '''
        We use this function when we try to update the Live status of the train.
        Currently we use a very restricted way of updating, but it is straight forward
        and requires the admin to submit opt for each update
    '''
    ret = {
        'flag': True,
        'message': '',
        'ended': False,
    }
    all_stops = TrainTimeTable.objects.filter(train_no=train_no).order_by('arr_time')
    status = GetOrCreateTrainStatus(train_no,date)
    if not status.started:
        status.started=True
        ret['next_station'] = status.last_station
        return ret
    if status.ended:
        ret['flag'] = False
        ret['message'] = 'Train already reached destination'
        return ret

    curr_station = status.last_station.station_id
    last_stop = all_stops[len(all_stops)-1]
    next_flag=False
    mark_ended = True
    for new_stop in all_stops:
        if next_flag:
            curr_station = new_stop.station_id.station_id
            mark_ended = False
            break
        if curr_station == new_stop.station_id.station_id:
            next_flag = True
        if new_stop == last_stop:
                ret['ended']=True
    if mark_ended:
        status.ended = True
        ret['flag'] = False
        ret['message'] = 'Train already reached destination'
        ret['ended'] = True
        status.save()
        return ret
    ret['next_station'] = Stations.objects.get(station_id = curr_station)
    return ret


def UpdateTrainStatus(train_no, date, next_station, delayed, ended):
    status = GetTrainStatus(train_no, date)
    status.last_station = next_station
    status.delayed = delayed
    status.ended = ended
    status.started = True
    status.save()
    return "Sucess"


def CheckTrainValidity(train_no,date):
    '''
        This function makes sure that a train exixts on a particular day
        It is also used to see if there are tickets are available or not
        also it takes care when the user tries to book in the past
    '''
    validity = {
        'validity': True,
        'message': 'Train Available'
    }
    train = GetTrainById(train_no)
    if not train:
        validity['message'] = 'Such a Train does not exist'
        validity['validity'] = False
        return validity
    if train.running_day != date.strftime('%a'):
        validity['message'] = "Train No."+str(train_no)+" Not running on "+str(date.strftime("%a"))
        validity['validity'] = False
        return validity
    ts = GetOrCreateTrainStatus(train_no,date)
    if ts.last_booked_coach >= ts.train_no.total_coaches and ts.last_booked_seat >= ts.train_no.seats_per_coach:
        validity['message'] = 'No tickets Available'
        validity['validity'] = False
        return validity
    date_today = date.today()
    if date < date_today:
        validity['message'] = 'Cant Book in the past'
        validity['validity'] = False
    return validity

def BookTicketAndSave(details):
    '''
        Given the basic details required for a ticket. It makes a ticket and saves
    '''
    trainstatus = GetTrainStatus(details['train_no'],GetDateFromString(details['date']))
    validity = CheckTrainValidity(details['train_no'], GetDateFromString(details['date']))
    if not validity['validity']:
        return HttpResponse(validity['message'])
    trainstatus.last_booked_seat += 1
    if trainstatus.last_booked_seat > trainstatus.train_no.seats_per_coach:
        trainstatus.last_booked_coach += 1
    trainstatus.save()
    new_ticket = Ticket()
    new_ticket.phone_no = GetUserById(phone_no = details['phone_no']) 
    new_ticket.train_no = GetTrainById(train_no = details['train_no'])
    new_ticket.seat_no = trainstatus.last_booked_seat
    new_ticket.coach_no = trainstatus.last_booked_coach
    new_ticket.name = details['name']
    new_ticket.date = GetDateFromString(details['date'])
    new_ticket.save()
    return "Success"
