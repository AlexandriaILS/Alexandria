from django import template

register = template.Library()


@register.simple_tag
def format_toast(string, title, subtitle):
    """Usage: {% format_toast base_string title subtitle %} """
    return string.format(f"{title}: {subtitle}" if subtitle != "" else title)
