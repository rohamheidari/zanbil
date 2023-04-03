from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from zanbilCalendarManager.calendarmanager import giveAccess
from zanbilCalendarManager.models import Office
from zanbilCalendarManager.models import Space
from django.contrib.auth.models import User
from zanbilCalendarManager.models import Accessibility
from zanbilCalendarManager.models import AccessRequest
from zanbilCalendarManager.models import ContactUsMessage
from .utils import sendRejectNotif


class OfficeAdmin(admin.ModelAdmin):
    verbose_name_plural = 'Offices'
    pass


admin.site.register(Office, OfficeAdmin)


class SpaceAdmin(admin.ModelAdmin):
    verbose_name_plural = 'Spaces'
    pass


admin.site.register(Space, SpaceAdmin)


class AccessibilityInline(admin.StackedInline):
    model = Accessibility
    extra = 0
    can_delete = True
    verbose_name_plural = 'Accessibilities'
    filter_horizontal = ('spaces',)


class UserAdmin(BaseUserAdmin):
    inlines = (AccessibilityInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.action(description='Accept request')
def grantAccess(modeladmin, request, queryset):
    queryset.update(status='a')
    for obj in queryset:
        giveAccess(obj.user, obj.space)


@admin.action(description='Reject request')
def rejectRequestAccess(modeladmin, request, queryset):
    queryset.update(status='r')
    for obj in queryset:
        sendRejectNotif(obj.user, obj.space)


class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'space', 'time', 'status')
    list_filter = ('time', 'status', 'space')
    readonly_fields = ('user', 'space', 'time', 'status')
    verbose_name = 'Access Request'
    verbose_name_plural = 'Access Requests'
    actions = [grantAccess, rejectRequestAccess]


admin.site.register(AccessRequest,  AccessRequestAdmin)


@admin.action(description='Resolve')
def resolveContactUsMessage(modeladmin, request, queryset):
    queryset.update(status='r')


@admin.action(description='Pend')
def PendContactUsMessage(modeladmin, request, queryset):
    queryset.update(status='p')


class ContactUsMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'phone', 'status')
    list_filter = ('time', 'status')
    readonly_fields = ('subject', 'description', 'email', 'phone')
    verbose_name = 'Contact Us Message'
    verbose_name_plural = 'Contact Us Messages'
    actions = [resolveContactUsMessage, PendContactUsMessage]
    pass


admin.site.register(ContactUsMessage, ContactUsMessageAdmin)
