from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError


class Domain(models.Model):
    name = models.CharField(max_length=253, default=settings.DEFAULT_HOST_KEY)

    @classmethod
    def get_default(cls):
        return cls.objects.get_or_create(name=settings.DEFAULT_HOST_KEY)[0]

    @classmethod
    def get_default_pk(cls):
        try:
            return cls.objects.get_or_create(name=settings.DEFAULT_HOST_KEY)[0].pk
        except ProgrammingError:
            # We're running migrations for the first time. There's nothing in the
            # db yet, so we can just return any value and the right one will be
            # pulled for future objects.
            return 1

    @classmethod
    def get_system(cls):
        return cls.objects.get_or_create(name=settings.DEFAULT_SYSTEM_HOST_KEY)[0]

    def __str__(self):
        return self.name


class SettingsContainer:
    def __init__(self, host):
        self.host = host

    def __getattr__(self, item):
        # allow dot notation on the request object for templates
        return Setting.get(name=item, host=self.host)

    def get(self, name: str, **kwargs):
        return Setting.get(name, **kwargs, host=self.host)

    def get_int(self, name: str, **kwargs):
        return Setting.get_int(name, **kwargs, host=self.host)

    def as_dict(self):
        # todo: fix
        return Setting.objects.filter(host=self.host).values_list(
            "name", "value", flat=True
        )


class Setting(models.Model):
    name = models.CharField(max_length=50)
    value = models.TextField()
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )

    @classmethod
    def get(
        cls, name: str, host: Domain = None, default: int | str = None
    ) -> str | None:
        if not host:
            host = Domain.get_default()
        if result := cls.objects.filter(name=name, host=host).first():
            return result.value
        return default

    def __str__(self):
        return f"{self.host.name}: {self.name}={self.value}"

    @classmethod
    def get_int(cls, *args, **kwargs) -> int | None:
        # Handle settings that might be None without extra boilerplate.
        if result := cls.get(*args, **kwargs):
            return int(result)
        return None
