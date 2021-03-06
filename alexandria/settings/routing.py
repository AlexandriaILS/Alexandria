import os

# Route us to the correct settings file based on environment variables. Allows
# us to add a stage environment really easily.

env = os.environ.get("ENVIRONMENT", None)

if env == "local":
    from alexandria.settings.local import *
elif env == "testing":
    from alexandria.settings.testing import *
else:
    from alexandria.settings.prod import *
