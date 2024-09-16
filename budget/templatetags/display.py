from django import template


register = template.Library()

@register.filter
def display(string: str) -> str:
    return string.replace("_", " ").title()


