# your_app/templatetags/customer_filters.py

from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Return dict value by key"""
    try:
        return dictionary.get(key)
    except:
        return None


@register.filter
def mul(value, arg):
    """Multiply values"""
    try:
        return value * arg
    except:
        return ''


@register.filter
def div(value, arg):
    """Divide values"""
    try:
        return value / arg
    except:
        return ''


@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except:
        return ''


@register.filter
def concat(value, arg):
    """Concatenate strings"""
    return f"{value}{arg}"
