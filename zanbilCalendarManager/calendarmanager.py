from __future__ import print_function
from errno import errorcode
from googleapiclient.errors import HttpError
from .calendarconnector import clientServiceBuilder, zanbilServiceBuilder
from .eventmanager import releaseEvent
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from zanbilCalendarManager.models import AccessRequest, Accessibility, Space, Event
from .utils import sendAcceptNotif


def attendedEventsChecker():
    checkPeriod = 10
    scheduler = BackgroundScheduler()
    scheduler.add_job(checkAttended, 'interval', minutes=checkPeriod)
    scheduler.start()


def checkAttended():
    try:
        print("checking")
        currentTime = datetime.now()
        lowerBound = timedelta(minutes=60)
        upperBound = timedelta(minutes=15)
        timeMin = currentTime - lowerBound
        timeMax = currentTime - upperBound
        events = Event.objects.filter(
            start__gte=timeMin, start__lte=timeMax, status='p')
        for event in events:
            releaseEvent(event)
        return

    except HttpError as error:
        print('An error occurred: %s' % error)


def inquiryCalendars(request):
    try:
        accessibility = Accessibility.objects.get(user=request.user)
        return accessibility.spaces.all()
    except Accessibility.DoesNotExist:
        return False
    except HttpError as error:
        print("Error", error)
        return error


def giveAccess(user, space):
    try:
        accessibilty, created = Accessibility.objects.get_or_create(user=user)
        accessibilty.spaces.add(space)
        accessibilty.save()
        sendAcceptNotif(user, space)
        return True
    except:
        return False


def recordAccessRequest(request, space):
    try:
        accessRequest = AccessRequest(user=request.user, space=space)
        accessRequest.save()
        return True
    except:
        return False
