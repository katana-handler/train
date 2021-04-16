import uuid
from django.db import models

WEEK_CHOICES = (
    ('Mon','Mon'),
    ('Tue','Tue'),
    ('Wed','Wed'),
    ('Thu','Thu'),
    ('Fri','Fri'),
    ('Sat','Sat'),
    ('Sun','Sun'),
)

class Trains(models.Model):
    train_no = models.CharField(primary_key = True, max_length=10, help_text='Train No denoting every unique train')
    train_name = models.CharField(max_length = 30, help_text='Name of the Train')
    running_day = models.CharField(max_length=3, choices=WEEK_CHOICES, default='Mon', help_text='Since the tains are weekly, noting the day of the week is useful when searching for trains')
    total_coaches = models.IntegerField(default=10)
    seats_per_coach = models.IntegerField(default=72)

class Stations(models.Model):
    station_id = models.CharField(primary_key = True, max_length=5)
    station_name = models.CharField( max_length=20)

class TrainTimeTable(models.Model):
    class Meta:
        unique_together = (('train_no','station_id'))
    train_no = models.ForeignKey(Trains, on_delete=models.CASCADE)
    station_id = models.ForeignKey(Stations, on_delete=models.CASCADE)
    arr_time = models.DateTimeField()
    dep_time = models.DateTimeField()
    running_day = models.CharField(max_length=3, choices=WEEK_CHOICES, help_text='Notes the Day of the week depending on the current status of the train')
    indexes = [
        models.Index(fields=['station_id']),
        models.Index(fields=['station_id', 'dep_time']),
        models.Index(fields=['train_no', 'arr_time']),
        models.Index(fields=['train_no']),
        models.Index(fields=['station_id', 'running_day'])
    ]
    '''
        Made indexes based of the different queries made to make searching even more efficient
    '''

class TrainStatus(models.Model):
    '''
        This model takes care of the status of each train running on different days
        Also it stores the seat availability
    '''
    class Meta:
        unique_together = (('train_no','start_date'))
    id = models.CharField(primary_key = True, max_length = 30)
    started = models.BooleanField(default=False, help_text='marks True when the train is upadted for the first time')
    ended = models.BooleanField(default=False, help_text = 'marks True when the last update is done')
    train_no = models.ForeignKey(Trains, on_delete=models.CASCADE)
    start_date = models.DateField()
    last_station = models.ForeignKey(Stations, on_delete=models.CASCADE, help_text='Last updated station')
    delayed = models.BooleanField(default=False)
    last_booked_seat = models.IntegerField(default=0)
    last_booked_coach =  models.IntegerField(default=0)


class User(models.Model):
    phone_no = models.IntegerField(primary_key=True)
    otp = models.CharField(max_length=10)
    name = models.CharField(max_length=30, default='jane doe')
    is_admin = models.BooleanField(default=False)

class Ticket(models.Model):
    class Meta:
        unique_together = (('phone_no','seat_no','coach_no'))
    phone_no = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 30)
    train_no = models.ForeignKey(Trains, on_delete=models.CASCADE)
    seat_no = models.IntegerField()
    coach_no = models.IntegerField()
    date = models.DateField()
    indexes = [
        models.Index(fields=['phone_no'])
    ]

