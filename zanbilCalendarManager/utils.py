import pytz
from datetime import datetime
from zanbilCalendarManager.models import AccessRequest, ContactUsMessage, Office, Space, Accessibility, Event, SpacesTraffic
from django.template import loader
from django.http import HttpResponse
from allauth.account.admin import EmailAddress
from django.db.models import Q
from django.db.models.functions import Lower, Upper
from datetime import datetime, timedelta, date
from googleapiclient.errors import HttpError
from django.core.mail import send_mail


def eventStatus(request, eventId):
    event = False
    user = request.user
    try:
        event = Event.objects.get(id=eventId)
        if(event.status == 'd'):
            return 'deleted_event'
    except:
        return 'not_existed_event'
    if (not event.creator == user) and (not user == 'admin') and (not isUserInvited(event, user)):
        return 'no_access_event'
    tz = pytz.timezone('Europe/Berlin')
    current = datetime.now(tz)
    if(current > event.end):
        return 'event_expired'
    elif(event.creator == user or user == 'admin'):
        return 'owner'
    elif isUserInvited(event, user):
        return 'attendee'
    return 'no_access_event'


def spaceStatus(request, spaceId):
    user = request.user
    if not Space.objects.filter(id=spaceId).exists():
        return 'not_existed_space'
    space = Space.objects.get(id=spaceId)
    if space.accessibility_set.filter(user=user).exists():
        return 'accessible'
    else:
        return 'no_access_space'


def checkAccess(user, spaceId):
    try:
        accessibility = Accessibility.objects.get(user=user)
        accessToSpcae = accessibility.spaces.get(id=spaceId)
        return True
    except:
        return False


def announcementHandler(request, header, title, description):
    context = {
        'header': header,
        'title': title,
        'reason': description
    }
    template = loader.get_template(
        'zanbilCalendarManager/announcement.html')
    return HttpResponse(template.render(context, request))


def announcementComposer(request, error):
    header = {
        'deleted_event': 'Something is wrong',
        'not_owning_event': 'Something is wrong',
        'not_existed_event': 'Something is wrong',
        'no_access_event': 'Something is wrong',
        'not_invited': 'Something is wrong',
        'deleted_successfully': 'Done!',
        'access_requesut_pending': '',
        'access_requesut_rejected': "",
        'access_requesut_sent': "Perfect!",
        'unverified-email': 'Something is wrong',
        'no_event_found': 'Something is wrong',
        'not_existed_space': 'Something is wrong',
        'event_expired': 'Something is wrong',
        'already_checkedin': '',
        'successfull_checkin': 'Welcome',
        'successfully_deleted': 'Done!',
        'not_ready_to_checkIn': 'Something is wrong',
        'Unknown': 'Something is wrong',
    }
    title = {
        'deleted_event': 'Not Found',
        'not_owning_event': "You're not the owner of this event",
        'not_existed_event': 'Not Found',
        'no_access_event': "your'e not invited to this event",
        'not_invited': "your'e not invited to this event",
        'access_requesut_pending': "Repetitious request",
        'access_requesut_rejected': "Repetitious request",
        'access_requesut_sent': "Request Sent",
        'unverified-email': 'Please confirm you email first',
        'no_event_found': "No event found",
        'not_existed_space': 'Not found',
        'event_expired': 'Event Expired',
        'already_checkedin': 'Repetitious request',
        'successfull_checkin': 'Checked In!',
        'successfully_deleted': 'Event deleted',
        'not_ready_to_checkIn': 'Too Soon!',
        'Unknown': 'Please contact support'

    }
    description = {
        'deleted_event': 'Event Deleted',
        'not_owning_event': "Make sure your logged in with the correct email",
        'not_existed_event': "Event dosn't exist",
        'no_access_event': "Make sure your logged in with the correct email",
        'not_invited': "Make sure you're logged in with the email you got invited",
        'access_requesut_pending': "Your request for accessing this space is under review",
        'access_requesut_rejected': "You can't have access to this space",
        'access_requesut_sent': "We will review your request and mail you if needed",
        'unverified-email': "Check your email and click the confirmation link we sent you",
        'no_event_found': "You're not invited to any event for this space at this time",
        'not_existed_space': "Space dosn't exist",
        'event_expired': "Event ended",
        'already_checkedin': "You've cheked in to this event before",
        'successfull_checkin': "You checked in to this event successfully",
        'successfully_deleted': "",
        'not_ready_to_checkIn': "You can't check-in sooner than 5 minutes before event's start",
        'Unknown': ''
    }
    try:
        return announcementHandler(request, header[error], title[error], description[error])
    except:
        print("ERROR: ", error)
        return announcementHandler(request, "", "Unknown Error", "")


def unverifiedEmail(request):
    if not request.user.is_authenticated:
        return False
    return EmailAddress.objects.filter(user=request.user, verified=False).exists()


def isEmailVerified(user, email):
    return EmailAddress.objects.filter(user=user, email=email, verified=True).exists()


def isUserInvited(event, user):
    emails = user.emailaddress_set.filter(
        verified=True).values_list(Lower('email'), flat=True)
    if event.attendees.filter(email__in=emails).exists():
        return True
    return False


def isUserCheckedin(event, user):
    return SpacesTraffic.objects.filter(event=event, user=user).exists()


def checkDuplicatedEvent(start, end, spaceId, eventId):
    space = Space.objects.get(id=spaceId)
    sequenceId = 0
    if Event.objects.filter(id=eventId).exists():
        sequenceId = Event.objects.get(id=eventId).sequence_id
    events1 = Event.objects.filter(
        ~Q(sequence_id=sequenceId), ~Q(id=eventId), space=space, start__gte=start, start__lte=end, status__in=['p', 'a']).exists()
    events2 = Event.objects.filter(
        ~Q(sequence_id=sequenceId), ~Q(id=eventId), space=space, end__gte=start, end__lte=end, status__in=['p', 'a']).exists()
    events3 = Event.objects.filter(
        ~Q(sequence_id=sequenceId), ~Q(id=eventId), space=space, start__lte=start, end__gte=end, status__in=['p', 'a']).exists()
    return events1 or events2 or events3


def readyToCheckIn(event, user):
    tz = pytz.timezone('Europe/Berlin')
    current = datetime.now(tz)
    myStart = event.start - timedelta(minutes=5)
    if current > myStart and current < event.end and not isUserCheckedin(event, user):
        return True
    return False


def eventFinder(request, space, start, end):
    try:
        newEvents = Event.objects.filter(
            ~Q(status='d'), space=space, start__lte=start, end__gte=end).order_by('-start')
        eventAccess = eventStatus(request, newEvents[0].id)
        if eventAccess == 'attendee' or eventAccess == 'owner':
            return newEvents[0]
        else:
            return False
    except:
        return False


def inquiryEvents(space, user, start, end):
    try:
        if not space:
            newEvents = Event.objects.filter(
                ~Q(status='d'), start__gte=start, start__lte=end).order_by('start')
        else:
            newEvents = Event.objects.filter(
                ~Q(status='d'), space=space, start__gte=start, start__lte=end).order_by('start')
        eventsForUser = []
        tz = pytz.timezone('Europe/Berlin')
        current = datetime.now(tz)
        for event in newEvents:
            if event.creator == user:
                event.owner = True
                event.invited = False
            elif isUserInvited(event, user):
                event.invited = True
                event.owner = False
            else:
                continue
            if current > event.end:
                event.expired = True
            event.readyToCheckIn = readyToCheckIn(event, user)
            if current < event.end:
                eventsForUser.append(event)
        return eventsForUser

    except HttpError as error:
        return error


def eventsList(user, space, rangeStart, rangeEnd):
    tz = pytz.timezone('Europe/Berlin')
    currentDay = date.today()
    startDay = currentDay
    endToday = currentDay + timedelta(days=1)
    endSevenDays = currentDay + timedelta(days=8)
    endThirtyDays = currentDay + timedelta(days=31)
    today = inquiryEvents(space, user, startDay, endToday)
    sevenDays = inquiryEvents(space, user, startDay, endSevenDays)
    thirtyDays = inquiryEvents(space, user, startDay, endThirtyDays)
    rangeDays = False
    if rangeStart:
        tempStart = date.fromisoformat(rangeStart)
        tempEnd = date.fromisoformat(rangeEnd) + timedelta(days=1)
        rangeDays = inquiryEvents(
            space, user, tempStart, tempEnd)
        if len(rangeDays) == 0:
            rangeDays = False
    if len(today) == 0:
        today = False
    if len(sevenDays) == 0:
        sevenDays = False
    if len(thirtyDays) == 0:
        thirtyDays = False
    userEvents = [
        {
            "id": 1,
            "name": "Today",
            "events": today,
        },
        {
            "id": 2,
            "name": "Next 7 Days",
            "events": sevenDays,
        },
        {
            "id": 3,
            "name": "Next 30 Days",
            "events": thirtyDays,
        },
        {
            "id": 4,
            "name": "Range",
            "events": rangeDays,
        }
    ]
    return userEvents


def sendAcceptNotif(user, space):
    message = 'Dear %s, \n\n Your request for accessing space %s has been accepted! \n You can reserve this space from now on. \n\n Best regards \n Zanbil Team' % (
        user.username, space.name)
    send_mail(
        'Space accessibility update',
        message,
        None,
        [user.email],
        fail_silently=False,
    )


def sendRejectNotif(user, space):
    message = 'Dear %s, \n\n Your request for accessing space %s has been Rejected :( \n The administrator did not find you eligible for having access to this space, you can contact support in this regard. \n\n Best regards \n Zanbil Team' % (
        user.username, space.name)
    send_mail(
        'Space accessibility update',
        message,
        None,
        [user.email],
        fail_silently=False,
    )


def recordMessage(form):
    try:
        subject = form.cleaned_data['subject']
        description = form.cleaned_data['description']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        ContactUsMessage(subject=subject, description=description,
                         email=email, phone=phone).save()
        return True
    except:
        return False
