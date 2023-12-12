from django import template

register = template.Library()


@register.simple_tag()
def if_val_inlist(value, vals):
    return value in map(int, vals)
