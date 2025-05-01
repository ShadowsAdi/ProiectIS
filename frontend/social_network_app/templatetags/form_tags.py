from django import template

register = template.Library()

@register.filter
def add_class(value, class_name):
    """
    Adds a custom class to a form field widget.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    widget = value.field.widget
    widget.attrs.update({'class': class_name})
    return value

@register.filter
def add_placeholder(value, placeholder_text):
    """
    Adds a placeholder to a form field widget.
    Usage: {{ form.field|add_placeholder:"Enter your username" }}
    """
    widget = value.field.widget
    widget.attrs.update({'placeholder': placeholder_text})
    return value