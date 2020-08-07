import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class PasswordValidator(object):
    def __init__(self):
        self.pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$")

    def validate(self, password, user=None):
        if not self.pattern.match(password):
            raise ValidationError(
                _("Passwords must be at least 8 characters long, and contain one capital letter and one number")
            )

    def get_help_text(self):
        return _("Passwords must be at least 8 characters long, and contain one capital letter and one number")