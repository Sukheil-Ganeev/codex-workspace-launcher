"""
Модуль маркетинга и продвижения.

Содержит инструменты для email-маркетинга, парсинга Instagram,
реферальной программы и SMS-рассылок через Twilio.
"""

from .email_marketing import *
from .instagram_parser import *
from .referral_program import *
from .sms_twilio import *

__all__ = [
    'email_marketing',
    'instagram_parser',
    'referral_program',
    'sms_twilio',
]
