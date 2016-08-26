from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from extra_views import FormSetView

from source.models import Source

class UtilityMixin(object):
    
    source = None

    def sourcesList(self, obj, attribute):
        sources = [s for s in getattr(obj, attribute).get_sources()] \
                      + [self.source]
        return list(set(s for s in sources if s))
    

class BaseFormSetView(FormSetView, UtilityMixin):
    
    required_session_data = []

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 _("Please add a source for this information"),
                                 extra_tags='alert alert-info')
            return redirect(reverse_lazy('create-source'))
        elif self.required_session_data:
            for session_key in self.required_session_data:
                try:
                    self.request.session[session_key]
                except KeyError:
                    return redirect(reverse_lazy('create-organization'))

        return super().dispatch(*args, **kwargs)

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


class BaseUpdateView(FormView, UtilityMixin):
    
    def post(self, request, *args, **kwargs):
        self.checkSource(request)
        self.validateForm()

    def checkSource(self, request):
        
        self.form = self.form_class(request.POST)

        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(self.form)
        else:
            self.source = Source.objects.get(id=request.POST.get('source'))
    
    def validateForm(self):
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)
    

class PaginatedList(ListView):
    
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

