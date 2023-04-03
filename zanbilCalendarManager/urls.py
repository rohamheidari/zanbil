from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('spaces', views.spaces, name='spaces'),
    re_path(r'^events/$', views.allEvents, name='allEvents'),
    path('', views.home, name='home'),
    path('request-access/<int:spaceId>',
         views.requestAccess, name='requestAccess'),
    path('checkin-space/<int:spaceId>',
         views.checkInSpace, name='checkInSpace'),
    path('checkin-event/<int:eventId>',
         views.checkInEvent, name='checkInEvent'),
    path('checkout/<int:eventId>',
         views.checkOut, name='checkOut'),
    path('calendar/<int:spaceId>',
         views.calendar, name='calendar'),
    path('create-event/<int:spaceId>',
         views.createEvent, name='createEvent'),
    path('request-access/<int:spaceId>',
         views.requestAccess, name='requestAccess'),
    path('eventsummary/<int:eventId>',
         views.eventSummary, name='eventSummary'),
    path('edit-event/<int:eventId>',
         views.editEvent, name='editEvent'),
    path('delete-event/<int:eventId>',
         views.deleteEvent, name='deleteEvent'),
    path('privacy-policy',
         views.privacyPolicy, name='privacyPolicy'),
    path('terms-and-conditions',
         views.terms, name='terms'),
    path('contact-us',
         views.contactUs, name='contactUs'),
    #     path('checkout/<str:roomId>/<str:eventId>',
    #          view=views.checkOut, name='checkOut'),
]
