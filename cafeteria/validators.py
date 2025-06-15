from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import MinimumLengthValidator


class ValidadorMinimoPersonalizado(MinimumLengthValidator):
    def get_help_text(self):
        return _("A senha deve conter pelo menos %(min_length)d caracteres.") % {'min_length': self.min_length}

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("A senha deve conter pelo menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
