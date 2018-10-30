from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.views.generic.edit import ModelFormMixin
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from reversion.views import RevisionMixin

from countries_plus.models import Country

from extra_views import FormSetView

from source.models import Source

class CacheMixin(object):
    cache_timeout = 60 * 60 * 24

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class EditUpdateMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['post_data'] = self.request.POST
        form_kwargs['object_ref_pk'] = self.kwargs[self.slug_field_kwarg]
        return form_kwargs

    def form_invalid(self, form):
        for field in form.fields.values():
            if hasattr(field, 'new_instances'):
                for model in field.new_instances:
                    model.delete()

        return super().form_invalid(form)


@method_decorator([never_cache, transaction.atomic], name='dispatch')
class BaseEditView(LoginRequiredMixin,
                   EditUpdateMixin,
                   ModelFormMixin,
                   RevisionMixin):
    '''
    SubClasses need to implement meta like so:

        model = Person
        slug_field = 'uuid'
        slug_field_kwarg = 'slug'
        context_object_name = 'person'

    They also need to provide a 'get_success_url' method
    '''
    pass


class BaseUpdateView(BaseEditView, UpdateView):
    pass


class BaseCreateView(BaseEditView, CreateView):
    pass
