from alexandria.utils.templatetags.format_toast import format_toast
from alexandria.utils.templatetags.settings_value import settings_value


def test_settings_value(settings):
    settings.HELLO_WORLD = "hello world"

    assert settings_value("HELLO_WORLD") == "hello world"


def test_format_toast():
    format = "A book - {}"
    title = "Hello"
    subtitle = "World"

    assert format_toast(format, title, subtitle) == "A book - Hello: World"
    assert format_toast(format, title, "") == "A book - Hello"
