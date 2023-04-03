import json
from platform import release
import pytz
from allauth.account.admin import EmailAddress
from django.shortcuts import render
from django.http import HttpResponse
from googleapiclient.errors import HttpError
from zanbilCalendarManager.calendarmanager import inquiryCalendars, recordAccessRequest
from .eventmanager import busyEvent, addEvent, recordCheckout, modifyEvent, releaseEvent
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from .roomids import rooms
from zanbilCalendarManager.models import AccessRequest, Office, Space, Accessibility, Event
from .forms import NewEvent, EditEvent, contactUsForm
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import eventStatus, eventsList, inquiryEvents, readyToCheckIn, recordMessage, spaceStatus, eventFinder, announcementComposer, announcementHandler, isEmailVerified, isUserCheckedin
from django.utils.timezone import localtime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


def spaceObject(spaceId):
    try:
        space = Space.objects.get(id=spaceId)
        return space
    except:
        return False


def emailStatus(request):
    return EmailAddress.objects.filter(user=request.user, verified=True).exists()


def httpErrorHandler(request, error):
    context = {
        'code': '',
        'reason': "Unknown Error",
    }
    if error.resp.status:
        context["code"] = error.resp.status
        if error.resp.get('content-type', '').startswith('application/json'):
            reason = json.loads(error.content).get(
                'error').get('errors')[0].get('reason')
            context["reason"] = reason
    template = loader.get_template(
        'zanbilCalendarManager/error.html')
    return HttpResponse(template.render(context, request))


def index(request):
    return HttpResponse("Hello Roham, this is ZANBIL!")


def login(request):
    if request.user.is_authenticated:
        return(request.path)
    else:
        template = loader.get_template(
            'zanbilCalendarManager/login.html')
        context = {}
        return HttpResponse(template.render(context, request))


def home(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    startDay = date.today()
    endToday = startDay + timedelta(days=7)
    upcomingEvents = inquiryEvents(False, request.user, startDay, endToday)
    upcomingEvents = upcomingEvents[0:10]
    if len(upcomingEvents) == 0:
        upcomingEvents = False
    userSpaces = inquiryCalendars(request)
    if userSpaces:
        userSpaces = userSpaces[0:10]
    template = loader.get_template(
        'zanbilCalendarManager/home.html')
    context = {
        'upcomingEvents': upcomingEvents,
        'spaces': userSpaces,
    }
    return HttpResponse(template.render(context, request))


def allEvents(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    today = date.today()
    tomorrow = today + timedelta(days=7)
    spaceId = request.GET.get("space", None)
    rangeStart = request.GET.get("start", False)
    rangeEnd = request.GET.get("end", False)
    print("Range : ", rangeStart, rangeEnd)
    space = False
    if spaceId:
        spaceAccess = spaceStatus(request, spaceId)
        if spaceAccess == "not_existed_space":
            return announcementComposer(request, spaceAccess)
        else:
            space = Space.objects.get(id=spaceId)
    allSpaces = Space.objects.all()
    eventsForUser = eventsList(request.user, space, rangeStart, rangeEnd)
    if isinstance(eventsForUser, HttpError):
        return httpErrorHandler(request, eventsForUser)
    template = loader.get_template(
        'zanbilCalendarManager/eventselector.html')
    context = {
        'eventsForUser': eventsForUser,
        'range': (rangeStart or rangeEnd),
        'rangeStart': rangeStart,
        'rangeEnd': rangeEnd,
        'space': space,
        'allSpaces': allSpaces,
    }
    print("CONTEXT", context)
    return HttpResponse(template.render(context, request))


def spaces(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    userSpaces = inquiryCalendars(request)
    if isinstance(userSpaces, HttpError):
        return httpErrorHandler(request, userSpaces)
    allSpaces = Space.objects.all()
    allOffices = Office.objects.all()
    offices = set()
    if userSpaces:
        for space in userSpaces:
            offices.add(space.office)
    template = loader.get_template(
        'zanbilCalendarManager/spaces.html')
    context = {
        'spacesForUser': userSpaces,
        'offices': offices,
        'allSpaces': allSpaces,
        'allOffices': allOffices,
    }
    return HttpResponse(template.render(context, request))


def checkInEvent(request, eventId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    eventAccess = eventStatus(request, eventId)
    if not eventAccess == 'attendee' and not eventAccess == 'owner':
        return announcementComposer(request, eventAccess)
    event = Event.objects.get(id=eventId)
    if isUserCheckedin(event, request.user):
        return announcementComposer(request, "already_checkedin")
    if not readyToCheckIn(event, request.user):
        return announcementComposer(request, "not_ready_to_checkIn")
    newStatus = busyEvent(event, request.user)
    if isinstance(newStatus, HttpError):
        return httpErrorHandler(request, newStatus)
    elif newStatus == "Succeed":
        return announcementComposer(request, "successfull_checkin")
    else:
        return announcementComposer(request, 'no_access_event')


def checkInSpace(request, spaceId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    spaceAccess = spaceStatus(request, spaceId)
    if spaceAccess == 'not_existed_space':
        return announcementComposer(request, spaceAccess)
    space = Space.objects.get(id=spaceId)
    tz = pytz.timezone('Europe/Berlin')
    current = datetime.now(tz)
    start = current + timedelta(minutes=5)
    event = eventFinder(request, space, start, current)
    if not event:
        return announcementComposer(request, "no_event_found")
    return redirect('/eventsummary/%s' % (event.id))


def checkOut(request, eventId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/log2in", request.path))
    eventAccess = eventStatus(request, eventId)
    if not eventAccess == 'attendee' and not eventAccess == 'owner':
        return announcementComposer(request, eventAccess)
    newStatus = recordCheckout(eventId, request.user)
    if isinstance(newStatus, HttpError):
        return httpErrorHandler(request, newStatus)
    context = {
        'status': newStatus,
        'roomName': Event.objects.get(id=eventId).space.name,
    }
    template = loader.get_template(
        'zanbilCalendarManager/checkoutresult.html')
    return HttpResponse(template.render(context, request))


def calendar(request, spaceId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    spaceAccess = spaceStatus(request, spaceId)
    if spaceAccess == 'no_access_space':
        return redirect('%s/%s' % ("/request-access", spaceId))
    elif not spaceAccess == 'accessible':
        return announcementComposer(request, spaceAccess)
    responsiveIframe = None
    if Space.objects.get(id=spaceId).calendar_embed_link != None:
        responsiveIframe = Space.objects.get(
            id=spaceId).calendar_embed_link.replace('style="', 'style = "width:100%; ')
    context = {
        'space': Space.objects.get(id=spaceId),
        'iframe': responsiveIframe,
        'user': request.user
    }
    template = loader.get_template(
        'zanbilCalendarManager/calendar.html')
    return HttpResponse(template.render(context, request))


def createEvent(request, spaceId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    spaceAccess = spaceStatus(request, spaceId)
    if spaceAccess == 'no_access_space':
        return redirect('%s/%s' % ("/request-access", spaceId))
    elif not spaceAccess == 'accessible':
        return announcementComposer(request, spaceAccess)
    elif not isEmailVerified(request.user, request.user.email):
        return announcementComposer(request, 'unverified-email')
    status = True
    form = NewEvent()
    if request.method == 'POST':
        numberOfAttendees = int(request.POST['number_of_attendees'])
        form = NewEvent(request.POST, numberOfAttendees=numberOfAttendees)
        if form.is_valid():
            eventId, busyDates = addEvent(spaceId, request.user, form, False)
            if isinstance(eventId, HttpError):
                return httpErrorHandler(request, eventId)
            if(eventId):
                return eventModificationResult(request, eventId, busyDates)
        else:
            print("Errors : ", form.errors)
    context = {
        'form': form,
        'spaceId': spaceId,
        'status': status,
        'space': Space.objects.get(id=spaceId),
    }
    template = loader.get_template(
        'zanbilCalendarManager/createevent.html')
    return HttpResponse(template.render(context, request))


def eventModificationResult(request, eventId, busyDates):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    eventAccess = eventStatus(request, eventId)
    if eventAccess == 'deleted_event' or eventAccess == 'not_existed_event' or eventAccess == 'no_access_event':
        return announcementComposer(request, eventAccess)
    event = Event.objects.get(id=eventId)
    if busyDates:
        busyDates = list(busyDates)
    context = {
        'event': event,
        'access': eventAccess,
        'readyToCheckin': readyToCheckIn(event, request.user),
        'busyDates': busyDates,
    }
    template = loader.get_template(
        'zanbilCalendarManager/eventmodificationsummary.html')
    return HttpResponse(template.render(context, request))


def eventSummary(request, eventId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    eventAccess = eventStatus(request, eventId)
    if eventAccess == 'deleted_event' or eventAccess == 'not_existed_event' or eventAccess == 'no_access_event':
        return announcementComposer(request, eventAccess)
    event = Event.objects.get(id=eventId)
    context = {
        'event': event,
        'access': eventAccess,
        'readyToCheckin': readyToCheckIn(event, request.user)
    }
    template = loader.get_template(
        'zanbilCalendarManager/eventsummary.html')
    return HttpResponse(template.render(context, request))


def editEvent(request, eventId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    status = eventStatus(request, eventId)
    if not status == 'owner':
        return announcementComposer(request, status)
    elif not isEmailVerified(request.user, request.user.email):
        return announcementComposer(request, 'unverified-email')
    event = Event.objects.get(id=eventId)
    spaceId = event.space.id
    form = EditEvent()
    if request.method == 'POST':
        if 'save' in request.POST:
            numberOfAttendees = int(request.POST['number_of_attendees'])
            form = EditEvent(
                request.POST, numberOfAttendees=numberOfAttendees)
            if form.is_valid():
                eventId, busyDates = modifyEvent(
                    spaceId, eventId, request.user, form)
                if isinstance(eventId, HttpError):
                    return httpErrorHandler(request, eventId)
                if(eventId):
                    return eventModificationResult(request, eventId, busyDates)
            else:
                print("Errors : ", form.errors)
        elif 'delete' in request.POST:
            updateMode = request.POST['update_mode']
            if updateMode == 'a':
                return deleteEvent(request, eventId, True)
            else:
                return deleteEvent(request, eventId, False)
    start = localtime(event.start).replace(tzinfo=None).isoformat()
    end = localtime(event.end).replace(tzinfo=None).isoformat()
    context = {
        'form': form,
        'event': event,
        'spaceId': spaceId,
        'eventId': eventId,
        'start': start,
        'end': end,
        'space': Space.objects.get(id=spaceId),
        'recurrent_period': event.recurrent_period,
    }
    template = loader.get_template(
        'zanbilCalendarManager/editevent.html')
    return HttpResponse(template.render(context, request))


def deleteEvent(request, eventId, bulk):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    status = eventStatus(request, eventId)
    if not status == 'owner':
        return announcementComposer(request, status)
    elif not isEmailVerified(request.user, request.user.email):
        return announcementComposer(request, 'unverified-email')
    event = Event.objects.get(id=eventId)
    result = releaseEvent(event, bulk)
    if isinstance(result, HttpError):
        return httpErrorHandler(request, status)
    return announcementComposer(request, result)


def requestAccess(request, spaceId):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % ("/accounts/login", request.path))
    status = spaceStatus(request, spaceId)
    if status == 'accessible':
        return redirect('%s/%s' % ("/calendar", spaceId))
    elif status == 'not_existed_space':
        return announcementComposer(request, status)
    elif not isEmailVerified(request.user, request.user.email):
        return announcementComposer(request, 'unverified-email')
    space = Space.objects.get(id=spaceId)
    if AccessRequest.objects.filter(user=request.user, space=space).exists():
        status = AccessRequest.objects.get(
            user=request.user, space=space).status
        if status == 'p':
            return announcementComposer(request, 'access_requesut_pending')
        elif status == 'r':
            return announcementComposer(request, 'access_requesut_rejected')
    elif request.method == 'POST':
        result = recordAccessRequest(request, space)
        if result:
            return announcementComposer(request, 'access_requesut_sent')
        else:
            return announcementComposer(request, 'Unknown')

    else:
        context = {
            'user': request.user,
            'space': space,
        }
        template = loader.get_template(
            'zanbilCalendarManager/request-access.html')
        return HttpResponse(template.render(context, request))


def terms(request):
    template = loader.get_template(
        'zanbilCalendarManager/terms.html')
    context = {}
    return HttpResponse(template.render(context, request))


def privacyPolicy(request):
    template = loader.get_template(
        'zanbilCalendarManager/privacypolicy.html')
    context = {}
    return HttpResponse(template.render(context, request))


def contactUs(request):
    template = loader.get_template(
        'zanbilCalendarManager/contactus.html')
    context = {
        'messageStatus': False,
    }
    if request.method == 'POST':
        form = contactUsForm(request.POST)
        if form.is_valid():
            recordMessage(form)
            context = {
                'messageStatus': True,
            }
    return HttpResponse(template.render(context, request))
