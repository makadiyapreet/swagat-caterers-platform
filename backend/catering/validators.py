"""
Section 18: Zxcvbn Password Strength Validator
"""
from django.core.exceptions import ValidationError


class ZxcvbnPasswordValidator:
    """
    Validates password strength using zxcvbn library.
    Requires minimum score of 2 (fair).
    """

    def __init__(self, min_score=2):
        self.min_score = min_score

    def validate(self, password, user=None):
        try:
            from zxcvbn import zxcvbn
        except ImportError:
            # If zxcvbn not installed, skip validation
            return

        # Build list of user inputs (common names, emails)
        user_inputs = []
        if user:
            user_inputs.extend([
                getattr(user, 'username', ''),
                getattr(user, 'email', ''),
                getattr(user, 'first_name', ''),
                getattr(user, 'last_name', ''),
            ])

        result = zxcvbn(password, user_inputs=user_inputs)
        score = result.get('score', 0)  # 0-4

        if score < self.min_score:
            feedback = result.get('feedback', {})
            warning = feedback.get('warning', '')
            suggestions = feedback.get('suggestions', [])

            msg = 'This password is too weak.'
            if warning:
                msg += f' {warning}.'
            if suggestions:
                msg += ' ' + ' '.join(suggestions)

            raise ValidationError(msg, code='password_too_weak')

    def get_help_text(self):
        return 'Your password must have a strength score of at least "Fair" (2/4).'
