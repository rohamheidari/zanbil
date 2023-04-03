from django import template
from ..utils import unverifiedEmail, spaceStatus

register = template.Library()


@register.filter
def notVerifiedEmail(request):
    return unverifiedEmail(request)


@register.filter
def spaceAccessStatus(request, space):
    status = spaceStatus(request, space.id)
    if status == 'accessible':
        return True
    return False


@register.filter
def recurrentPeriodLabel(recurrentPeriod):
    labels = {
        'd': 'Daily',
        'w': 'Weekly',
        'm': 'Monthly',
        None: 'None',
    }
    try:
        return(labels[recurrentPeriod])
    except:
        return "Unknown Period"
