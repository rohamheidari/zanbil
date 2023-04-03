from calendar import calendar
from pyexpat import model
from re import S
from django.db import models
from location_field.models.plain import PlainLocationField
from django.contrib.auth.models import User


class Office(models.Model):
    name = models.CharField("Name", max_length=50)
    address = models.CharField(max_length=500)
    location = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Space(models.Model):
    CHAIR = 'c'
    ROOM = 'r'
    SPACE_TYPE = (
        (CHAIR, 'Chair'),
        (ROOM, 'Room'),
    )
    name = models.CharField("Name", max_length=50)
    calendar_id = models.CharField(max_length=100)
    calendar_embed_link = models.CharField(
        "Google calendar embed link", max_length=2000, blank=True, null=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=SPACE_TYPE, default=ROOM)
    capacity = models.IntegerField(blank=True, null=True)
    image = models.ImageField(
        upload_to='covers/%Y/%m/%d/', blank=True, null=True)

    @property
    def aws_url(self):
        return self.image.url

    def __str__(self):
        return self.name


class Attendee(models.Model):
    name = models.CharField("Name", max_length=100, blank=True, null=True)
    email = models.EmailField("Email", max_length=254)


class Event(models.Model):
    PENDING = 'p'
    ATTENDED = 'a'
    DELETED = 'd'
    STATUS_TYPE = (
        (PENDING, 'Pending'),
        (ATTENDED, 'Attended'),
        (DELETED, 'Deleted')
    )
    DAY = 'd'
    WEEK = 'w'
    MONTH = 'm'
    RECURRENT_PERIOD = (
        (DAY, 'Day'),
        (WEEK, 'Week'),
        (MONTH, 'Month'),
    )
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    space = models.ForeignKey(Space, null=True, on_delete=models.SET_NULL)
    summary = models.CharField("summary", max_length=100)
    description = models.CharField(
        "summary", max_length=1000, blank=True, null=True)
    start = models.DateTimeField("Start date & time",
                                 auto_now=False, auto_now_add=False)
    end = models.DateTimeField("End date & time",
                               auto_now=False, auto_now_add=False)
    status = models.CharField(
        max_length=1, choices=STATUS_TYPE, default=PENDING)
    attendees = models.ManyToManyField(Attendee)
    google_id = models.CharField(
        "Google Calendar ID", max_length=500, null=True)
    sequence_id = models.IntegerField("Sequence Number", blank=True, null=True)
    recurrent = models.BooleanField("Recurrent Event", default=False)
    recurrent_period = models.CharField(
        max_length=1, choices=RECURRENT_PERIOD, blank=True, null=True)


class Accessibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spaces = models.ManyToManyField(Space)


class SpacesTraffic(models.Model):
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    event = models.ForeignKey(
        Event, blank=True, null=True, on_delete=models.SET_NULL)
    # user_email = models.EmailField("Email", max_length=254)
    # event_gid = models.CharField("google calendar id", max_length=100)
    # space = models.ForeignKey(Space, on_delete=models.CASCADE)
    checkin_datetime = models.DateTimeField(
        "Checkin date & time", auto_now=False, auto_now_add=True)
    checkout_datetime = models.DateTimeField(
        "Checkin date & time", auto_now=False, auto_now_add=False, blank=True, null=True)

    def __str__(self):
        return self.user_email


class AccessRequest(models.Model):
    PENDING = 'p'
    ACCEPTED = 'a'
    REJECTED = 'r'
    STATUS_TYPE = (
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    time = models.DateTimeField(
        "Request Time", auto_now=False, auto_now_add=True)
    status = models.CharField(
        max_length=1, choices=STATUS_TYPE, default=PENDING)

    def __str__(self):
        return self.user.username + " => " + self.space.name


class ContactUsMessage(models.Model):
    PENDING = 'p'
    RESOLVED = 'r'
    STATUS_TYPE = (
        (PENDING, 'Pending'),
        (RESOLVED, 'Resolved'),
    )
    time = models.DateTimeField(
        "Request Time", auto_now=False, auto_now_add=True)
    subject = models.CharField("Subject", max_length=100)
    description = models.CharField("Description", max_length=1000)
    email = models.EmailField("Email", max_length=254)
    phone = models.CharField("Phone", max_length=15)
    status = models.CharField(
        max_length=1, choices=STATUS_TYPE, default=PENDING)

    def __str__(self):
        return self.subject
