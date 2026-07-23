from django import template
from carRental.models import *

register = template.Library()

@register.simple_tag()
def multiply(qty,unit_price):
    return int(qty) * int(unit_price)
