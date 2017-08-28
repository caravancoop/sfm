import json

from  more_itertools import unique_everseen

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def create_select2_data(select_lang):
  data_array = ["English", "French", "Spanish"]
  trans_obj = {
      'fr': 'French',
      'en': 'English',
      'es': 'Spanish',
    }

  full_text = trans_obj[select_lang]
  data_array.insert(0, full_text)
  data_array = list(unique_everseen(data_array))

  # Returns an array of languages – with the current language as the first element.
  # To configure the select2 dropdown in the correct order.
  return json.dumps(data_array)