from __future__ import unicode_literals
import json

from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.db.models import Max
from .models import Person
from .forms import PersonForm

def ajax_request(function):
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return render_to_response('person/errors.html', {},
                                      context_instance=RequestContext(request))
        else:
            return function(request, *args, **kwargs)
    return wrapper

class PersonView(TemplateView):
    template_name = 'person/search.html'

    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        persons = Person.objects.all()
        context['persons'] = persons

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'personname__value'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        person_query = (Person.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))
        """
        currlist = [
            {
                'person_id': p.id,
                'name': p.get_name() or '',
                'alias': p.get_alias(),
                'notes': p.get_notes()
            }
            for p in person_query
        ]

        paginator = Paginator(currlist, 200)

        page = self.request.GET.get('page')
        try:
            person = paginator.page(page)
        except PageNotAnInteger:
            person = paginator.page(1)
        except EmptyPage:
            person = paginator.page(paginator.num_pages)

        context['person'] = person
        """
        context['orderby'] = order_by
        context['direction'] = direction

        return context

class PersonUpdate(UpdateView):
    template_name = 'person/edit.html'

    form_class = PersonForm
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonUpdate, self).get_context_data(**kwargs)
        context['title'] = "Person"

        return context

class FieldUpdate(TemplateView):
    template_name = 'field/popup/edit.html'

    def get_context_data(self, **kwargs):
        context = super(FieldUpdate, self).get_context_data(**kwargs)
        person = Person.from_id(context.get('person_id'))
        field = person.get_attribute_object(
            "Person"+context.get('field_type').capitalize()
        )
        context['field'] = field

        return context

class PersonCreate(TemplateView):
    template_name = 'person/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['person'])
        person = Person.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(PersonCreate, self).get_context_data(**kwargs)
        context['person'] = Person()

        return context



"""
class PersonDelete(DeleteView):
    form_class = PersonForm
    model = Person
    success_url = reverse_lazy('person')

class AjaxGeneral(CreateView):

    @method_decorator(ajax_request)
    def dispatch(self, *args, **kwargs):
        return super(AjaxGeneral, self).dispatch(*args, **kwargs)
"""

"""class PpPersonCreate(AjaxGeneral):
    template_name = 'person/popup/form2.html'
    form_class = PersonForm
    model = Person
    
    def get_context_data(self, **kwargs):
        context = {}
        context['form'] = self.form_class(initial={'artist':self.request.GET.get('artist') or None})
        return context
    
    def get_success_url(self):
        return reverse_lazy('Pp_close_person', args=(self.object.id,))
"""


"""class PpPersonCloseView(TemplateView):
    template_name = 'person/popup/close.html'

    def get_context_data(self, **kwargs):
        pk = kwargs['pk']
        person = Person.objects.filter(id=pk)
        
        context = {}
        context['pk'] = person[0].id or ''
        context['name'] = person[0].name or ''
        context['artist'] = person[0].artist or ''
        context['model'] = 'person'
        return context
"""
