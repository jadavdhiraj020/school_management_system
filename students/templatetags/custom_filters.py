# students/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, class_name):
    """
    Adds a CSS class to a form field widget.
    """
    return field.as_widget(attrs={'class': class_name})
