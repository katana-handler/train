from django import forms

HOMEPAGE_CHOICES = (
    ('Search Trains','Search Trains'),
    ('Book Ticket','Book Ticket'),
    ('Live Status','Live Status'),
    ('Change Status','Change Status'),
    ('Show Bookings','Show Bookings'),
)

'''
    forms are used to take input and send them as parameters from the UI to the Back End
'''

class TrainSearchForm(forms.Form):
    train_from_stn = forms.CharField(label = "From",max_length =80)
    train_to_stn = forms.CharField(label = "To",max_length =80)
    travel_date = forms.DateField(label = 'travel date', widget=forms.SelectDateWidget())

class OtpForm(forms.Form):
    otp = forms.CharField(label = 'OTP', max_length=10)

class OnlyPhoneForm(forms.Form):
    phone_no = forms.CharField(label = "Phone No", max_length=10)

class OnlyNameForm(forms.Form):
    name = forms.CharField(label = "Name",max_length = 30)

class TrainNoAndDateForm(forms.Form):
    train_no = forms.CharField(label='Train No', max_length=10)
    date = forms.DateField(label = 'Train Running Date', widget=forms.SelectDateWidget())

class LateByMinutesForm(forms.Form):
    late_by = forms.IntegerField(label = 'Late by (in Mins)')

class BookingForm(forms.Form):
    name = forms.CharField(label = 'Passenger Name', max_length=30)
    phone_no = forms.CharField(label = 'Booking Phone No.', max_length=10)
    train_no = forms.CharField(label = 'Train No.', max_length=10)
    date = forms.DateField(label = 'Travel Date', widget=forms.SelectDateWidget())

class HomePageFrom(forms.Form):
    choice = forms.ChoiceField( choices=HOMEPAGE_CHOICES)