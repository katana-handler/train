from django.urls import path

from . import views

urlpatterns = [
    path('',views.HomePage),
    path('search', views.SearchTrain),
    path('book',views.BookTicket),
    path('otp', views.VerifyOtp),
    path('newuser', views.NewUser),
    path('payment', views.PaymentGateway),
    path('history',views.ShowBookingHistory),
    path('bookings', views.Bookings),
    path('livestatus', views.TrainLiveStatus),
    path('admin',views.StartUpdate),
    path('update', views.Update),
    path('makeupdate', views.MakeUpdate),
    #path('script',views.Script),
]