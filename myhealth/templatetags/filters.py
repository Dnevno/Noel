from django import template

register = template.Library()

@register.filter
def urlcontains(value, arg):
    return arg in value