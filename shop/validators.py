import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class PasswordValidator(object):
    def __init__(self):
        self.pattern = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")

    def validate(self, password, user=None):
        if not self.pattern.match(password):
            raise ValidationError(
                _("Password must have at least one uppercase letter," \
                + " at least one lowercase letter, at least one number, and at least one special character")
            )

    def get_help_text(self):
        return _("Password must have at least one uppercase letter," \
                + " at least one lowercase letter, at least one number, and at least one special character")