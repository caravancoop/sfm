from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from countries_plus.models import Country

from extra_views import FormSetView

from source.models import Source

class CacheMixin(object):
    cache_timeout = 60 * 60 * 24

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(super(CacheMixin, self).dispatch)(*args, **kwargs)

class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class BaseEditView(UpdateView, NeverCacheMixin, LoginRequiredMixin):
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
        context['countries'] = Country.objects.all()
        return context

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['post_data'] = self.request.POST
        form_kwargs['object_ref_pk'] = self.kwargs[self.slug_field_kwarg]
        return form_kwargs


################################################################
## The views below here are probably ready to be factored out ##
################################################################

class UtilityMixin(object):

    source = None

    def sourcesList(self, obj, attribute):
        sources = [s for s in getattr(obj, attribute).get_sources()] \
                      + [self.source]
        return list(set(s for s in sources if s))


class BaseFormSetView(NeverCacheMixin, UtilityMixin, FormSetView):

    required_session_data = []

    def post(self, request, *args, **kwargs):
        self.initFormset(request.POST)
        return self.validateFormSet()

    def initFormset(self, form_data):
        Formset = self.get_formset()
        self.formset = Formset(form_data)

    def validateFormSet(self):
        if self.formset.is_valid():
            return self.formset_valid(self.formset)
        else:
            return self.formset_invalid(self.formset)


class BaseUpdateView(NeverCacheMixin, UtilityMixin, FormView):

    def post(self, request, *args, **kwargs):
        self.checkSource(request)
        self.validateForm()

    def checkSource(self, request):

        self.form = self.form_class(request.POST)

        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(self.form)
        else:
            self.source = Source.objects.get(uuid=request.POST.get('source'))

    def validateForm(self):
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            print(self.form.errors)
            return self.form_invalid(self.form)


class PaginatedList(NeverCacheMixin, ListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(context['object_list'], 25)

        page = self.request.GET.get('page')
        try:
            context['object_list'] = paginator.page(page)
        except PageNotAnInteger:
            context['object_list'] = paginator.page(1)
        except EmptyPage:
            context['object_list'] = paginator.page(paginator.num_pages)

        return context

    def get_queryset(self):
        order_by_field = self.request.GET.get('order_by')

        if order_by_field:
            order_by = self.orderby_lookup.get(order_by_field)

            if order_by:
                return self.model.objects.order_by(order_by)

        return self.model.objects.all()


