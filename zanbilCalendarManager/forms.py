from django import forms
import pytz
from datetime import datetime, timedelta
from .utils import checkDuplicatedEvent


class NewEvent(forms.Form):
    CHOICES = (
        ('n', 'n'),
        ('d', 'd'),
        ('w', 'w'),
        ('m', 'm'),
    )
    summary = forms.CharField(label='summary', max_length=100)
    description = forms.CharField(
        label='description', max_length=1000, required=False)
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    space_id = forms.IntegerField()
    repetition = forms.ChoiceField(choices=CHOICES)

    def __init__(self, *args, **kwargs):
        numberOfAttendees = kwargs.pop('numberOfAttendees', 1)
        super(NewEvent, self).__init__(*args, **kwargs)
        for i in range(numberOfAttendees):
            self.fields['attendee_%d' % i] = forms.EmailField(required=False)

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        spaceId = cleaned_data.get("space_id")
        tz = pytz.timezone('Europe/Berlin')
        current = datetime.now(tz) - timedelta(minutes=5)
        if checkDuplicatedEvent(start, end, spaceId, 0):
            self.add_error(
                None, "This space is booked for the time you chose, please select another time.")
        if start < current:
            self.add_error('start', "Start time should be after current time")
        if end < start:
            self.add_error('end', "End time should be after start time")
        return cleaned_data


class EditEvent(forms.Form):
    UPDATE_CHOICES = (
        ('s', 's'),
        ('a', 'a'),
    )
    REPETITIION_CHOICES = (
        ('n', 'n'),
        ('d', 'd'),
        ('w', 'w'),
        ('m', 'm'),
    )
    summary = forms.CharField(label='summary', max_length=100)
    description = forms.CharField(
        label='description', max_length=1000, required=False)
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    event_id = forms.IntegerField()
    space_id = forms.IntegerField()
    update_mode = forms.ChoiceField(choices=UPDATE_CHOICES)
    repetition = forms.ChoiceField(choices=REPETITIION_CHOICES)

    def __init__(self, *args, **kwargs):
        numberOfAttendees = kwargs.pop('numberOfAttendees', 1)
        super(EditEvent, self).__init__(*args, **kwargs)
        for i in range(numberOfAttendees):
            self.fields['attendee_%d' % i] = forms.EmailField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        eventId = cleaned_data.get("event_id")
        spaceId = cleaned_data.get("space_id")
        tz = pytz.timezone('Europe/Berlin')
        current = datetime.now(tz)
        if checkDuplicatedEvent(start, end, spaceId, eventId):
            self.add_error(
                None, "This space is booked for the time you chose, please select another time.")
        if end < current:
            self.add_error('end', "End time should be after current time")
        if end < start:
            self.add_error('end', "End time should be after start time")
        return cleaned_data


class contactUsForm(forms.Form):
    subject = forms.CharField(label='subject', max_length=100, required=True)
    description = forms.CharField(
        label='description', max_length=1000, required=True)
    email = forms.EmailField(label='email', required=True)
    phone = forms.IntegerField(label='phone', required=False)
