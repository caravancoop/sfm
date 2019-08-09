from uuid import uuid4

from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.views.generic.edit import ModelFormMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from reversion.views import RevisionMixin

from countries_plus.models import Country

from extra_views import FormSetView

from source.models import AccessPoint

class CacheMixin(object):
    cache_timeout = 60 * 60 * 24

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)


class CreateUpdateMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all()
        return context

    def form_invalid(self, form):
        for field in form.fields.values():
            if hasattr(field, 'new_instances'):
                for model in field.new_instances:
                    model.delete()

        return super().form_invalid(form)


class BaseDetailView(DetailView):
    def get_queryset(self):

        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            return queryset
        else:
            return queryset.filter(published=True)


@method_decorator([never_cache, transaction.atomic], name='dispatch')
class BaseEditView(LoginRequiredMixin,
                   CreateUpdateMixin,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['source_info'] = {}

        for form_field in self.request.POST:
            if form_field.endswith('_source'):
                value = self.request.POST.getlist(form_field)
                context['source_info'][form_field] = AccessPoint.objects.filter(uuid__in=value)

        context['confidence_choices'] = {
            '1': _('Low'),
            '2': _('Medium'),
            '3': _('High'),
        }

        return context


class BaseUpdateView(BaseEditView, UpdateView):
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['post_data'] = self.request.POST
        return form_kwargs


class BaseCreateView(BaseEditView, CreateView):
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['post_data'] = self.request.POST
        return form_kwargs


class BaseDeleteView(DeleteView):
    """
    Base view for deleting objects, providing a little extra context.
    """
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['cancel_link'] = self.get_cancel_link()
        return context

    def get_cancel_link(self):
        raise NotImplementedError('This method must be implemented on children.')


class BaseDeleteRelationshipView(BaseDeleteView):
    """
    Base view for deleting a relationship between two entities.
    """
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['delete_obj_1'], context['delete_obj_2'] = self.get_objects_to_delete()
        return context

    def get_objects_to_delete(self):
        raise NotImplementedError('This method must be implemented on children.')
