from __future__ import print_function
import re
from googleapiclient.errors import HttpError
from .calendarconnector import zanbilServiceBuilder
from datetime import datetime, timedelta
from zanbilCalendarManager.models import Space, SpacesTraffic, Event, Attendee
from .utils import checkDuplicatedEvent, isUserInvited
from dateutil.relativedelta import relativedelta
from django.db.models import Q


# def isUserCheckedin(eventId, email):
#     try:
#         record = SpacesTraffic.objects.get(event_gid=eventId, user_email=email)
#         return True
#     except:
#         return False


def isUserCheckedout(eventId, email):
    try:
        record = SpacesTraffic.objects.get(event_gid=eventId, user_email=email)
        if(record.checkout_datetime):
            return True
        return False
    except:
        return False


def attendeesList(form):
    attendees = []
    for field in form:
        fieldName = field.html_name
        if(fieldName.startswith('attendee') and form.cleaned_data[fieldName] != ""):
            attendees.append(form.cleaned_data[fieldName])
    return attendees


def addEventBodyComposer(event):
    attendees = "\n \nAttendees : \n" + \
        "\n".join(list(event.attendees.values_list('email', flat=True)))
    data = {
        'summary': event.summary,
        'description': event.description + attendees,
        'start': {
            'dateTime': event.start.isoformat(),
            'timeZone': "Etc/Universal",
        },
        'end': {
            'dateTime': event.end.isoformat(),
            'timeZone': "Etc/Universal",
        },
    }
    return data


def busyEvent(event, user):
    try:
        space = event.space
        calnedarId = space.calendar_id
        event.status = 'a'
        event.save()
        service = zanbilServiceBuilder()
        gEvent = service.events().get(
            calendarId=calnedarId, eventId=event.google_id).execute()
        SpacesTraffic.objects.create(user=user, event=event)
        gEvent['colorId'] = '11'
        gEvent['status'] = 'tentative'
        service.events().update(
            calendarId=calnedarId, eventId=gEvent['id'], body=gEvent).execute()
        return "Succeed"
    except HttpError as error:
        return error


def recordCheckout(eventId, user):
    try:
        event = Event.objects.get(id=eventId)
        calendarId = event.space.calendar_id
        if(not isUserInvited(event, user)):
            return "notInvited"
        if(isUserCheckedout(eventId, user.email)):
            return "AlreadyCheckedOut"
        record = SpacesTraffic.objects.get(
            event_gid=event.google_id, user_email=user.email)
        record.checkout_datetime = datetime.now()
        record.save()
        return "Succeed"
    except HttpError as error:
        return error


def addEventToCalendar(event, space):
    try:
        calendarId = space.calendar_id
        service = zanbilServiceBuilder()
        data = addEventBodyComposer(event)
        googleEvent = service.events().insert(calendarId=calendarId, body=data).execute()
        googleId = googleEvent.get('id')
        event.google_id = googleId
        event.save()
        return True
    except:
        return False


def recurrentDateList(start, end, period, duration):
    gap = 1
    dur = 3
    startDates = []
    endDates = []
    if period is 'w':
        gap = 7
        dur = 54
    elif period is 'd':
        gap = 1
        dur = 180
    elif period is 'm':
        gap = 1
        dur = 12
    elif period is 'test':
        gap = 1
        dur = 3
    if period is 'm':
        startDates = [start+relativedelta(months=+i) for i in range(1, dur)]
        endDates = [end+relativedelta(months=+i) for i in range(1, dur)]
    else:
        startDates = [start+timedelta(days=(i * gap)) for i in range(1, dur)]
        endDates = [end+timedelta(days=(i * gap)) for i in range(1, dur)]
    return zip(startDates, endDates)


def recurrentDateGenerator(initalStart, initalEnd, recurrent_period, duration, spaceId, initialEventId):
    dates = recurrentDateList(initalStart, initalEnd,
                              recurrent_period, duration)
    occupiedStartDates = []
    occupiedEndDates = []
    freeStartDates = []
    freeEndDates = []
    for (start, end) in dates:
        print("Start,", start)
        print("End", end)
        if not checkDuplicatedEvent(start, end, spaceId, initialEventId):
            print("FREE!")
            freeStartDates.append(start)
            freeEndDates.append(end)
        else:
            print("BUSY!!")
            occupiedStartDates.append(start)
            occupiedEndDates.append(end)
    return zip(freeStartDates, freeEndDates), zip(occupiedStartDates, occupiedEndDates)


def bulkUpdateAttendees(initialEvent):
    events = Event.objects.filter(sequence_id=initialEvent.sequence_id)
    attendees = initialEvent.attendees.all()
    for event in events:
        event.attendees.set(attendees)


def bulkEventCreator(initialEvent, dates, recurrent_period):
    events = [Event(summary=initialEvent.summary, start=date[0], end=date[1],
                    description=initialEvent.description, creator=initialEvent.creator, space=initialEvent.space, sequence_id=initialEvent.sequence_id, recurrent=True, recurrent_period=initialEvent.recurrent_period) for date in dates]
    Event.objects.bulk_create(events)


def bulkEventUpdater(initialEvent, dates, repeatation):
    events = Event.objects.filter(sequence_id=initialEvent.sequence_id)


def addEvent(spaceId, user, form, initialSequenceId):
    try:
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        recurrent_period = form.cleaned_data['repetition']
        if(not recurrent_period and checkDuplicatedEvent(start, end, spaceId, 0)):
            return False
        attendees = attendeesList(form)
        space = Space.objects.get(id=spaceId)
        initialEvent = Event(
            summary=form.cleaned_data['summary'], start=start, end=end, description=form.cleaned_data['description'], creator=user, space=space)
        initialEvent.save()
        initialEvent.sequence_id = initialSequenceId if initialSequenceId else initialEvent.pk
        for email in attendees:
            attendee, created = Attendee.objects.get_or_create(
                email=email.lower())
            initialEvent.attendees.add(attendee)
        initialEvent.save()
        if recurrent_period != 'n':
            initialEvent.recurrent = True
            initialEvent.recurrent_period = recurrent_period
            initialEvent.save()
            freeDates, busyDates = recurrentDateGenerator(
                start, end, recurrent_period, 0, spaceId, initialEvent.id)
            bulkEventCreator(initialEvent, freeDates, recurrent_period)
            bulkUpdateAttendees(initialEvent)
            events = Event.objects.filter(
                ~Q(status='d'), sequence_id=initialEvent.sequence_id)
            for event in events:
                addEventToCalendar(event, space)
            return initialEvent.id, busyDates
        else:
            addEventToCalendar(initialEvent, space)
            return initialEvent.id, False
    except HttpError as error:
        print("Error", error)
        return error


def modifyEvent(spaceId, eventId, user, form):
    try:
        start = form.cleaned_data['start']
        end = form.cleaned_data['end']
        update_mode = form.cleaned_data['update_mode']
        if checkDuplicatedEvent(start, end, spaceId, eventId):
            return False
        event = Event.objects.get(id=eventId)
        bulk = True if update_mode == 'a' else False
        sequenceId = event.sequence_id
        releaseEvent(event, bulk)
        return addEvent(spaceId, user, form, sequenceId)
    except HttpError as error:
        print("Error", error)
        return error


def releaseEvent(event, bulk):
    try:
        calnedarId = event.space.calendar_id
        current = datetime.now()
        service = zanbilServiceBuilder()
        if bulk:
            # , end__gte=current
            events = Event.objects.filter(~Q(status='d'),
                                          sequence_id=event.sequence_id)
            for event in events:
                try:
                    service.events().delete(calendarId=calnedarId,
                                            eventId=event.google_id, sendUpdates='all').execute()
                except:
                    print("Unable to delete google event!")
                    continue
            events.update(status='d')

        else:
            try:
                service.events().delete(calendarId=calnedarId,
                                        eventId=event.google_id, sendUpdates='all').execute()
            except:
                any
            event.status = 'd'
            event.save()
        return "successfully_deleted"
    except HttpError as error:
        print('An error occurred: %s' % error)
