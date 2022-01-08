from django import template

register = template.Library()


@register.simple_tag
def format_toast(string, title, subtitle):
    """Usage: {% format_string stringvar addition1 addition2 ... %} """
    return string.format(f"{title}: {subtitle}" if subtitle != "" else title)
