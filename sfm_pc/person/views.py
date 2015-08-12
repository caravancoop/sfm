# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader
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
    template_name = 'person/list.html'

    def get_context_data(self, **kwargs):
        context = super(PersonView, self).get_context_data(**kwargs)

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'name'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        person_query = Person.objects.order_by(dirsym + order_by)

        currlist = {}
        i = 0

        for p in person_query:

            artist_name = ''
            artist_id = None

            currlist[i] = {
                'person_id':    p.id,
                'name': p.name or '',
                'artist_id':    artist_id,
                'artist_name': artist_name,
            }
            i = i + 1



        paginator = Paginator(currlist.items(), 200)

        page = self.request.GET.get('page')
        try:
            person = paginator.page(page)
        except PageNotAnInteger:
            person = paginator.page(1)
        except EmptyPage:
            person = paginator.page(paginator.num_pages)


        context['person'] = person
        context['orderby'] = order_by
        context['direction'] = direction


        # Search values
        context['artist_id'] = sf_artist_id or ''
        context['artists'] = artists_list or ''
        
        return context


class PersonCreate(CreateView):
    template_name = 'person/form.html'
    form_class = PersonForm
    model = Person

    def get_success_url(self):
        return reverse_lazy('person')


class PersonUpdate(UpdateView):
    template_name = 'person/form.html'
    form_class = PersonForm
    model = Person

    def get_success_url(self):
        return reverse_lazy('person')


class PersonDelete(DeleteView):
    form_class = PersonForm
    model = Person
    success_url = reverse_lazy('person')


class AjaxGeneral(CreateView):

    @method_decorator(ajax_request)
    def dispatch(self, *args, **kwargs):
        return super(AjaxGeneral, self).dispatch(*args, **kwargs)


class PpPersonCreate(AjaxGeneral):
    template_name = 'person/popup/form.html'
    form_class = PersonForm
    model = Person
    
    def get_context_data(self, **kwargs):
        context = {}
        context['form'] = self.form_class(initial={'artist':self.request.GET.get('artist') or None})
        return context
    
    def get_success_url(self):
        return reverse_lazy('Pp_close_person', args=(self.object.id,))


class PpPersonUpdate(UpdateView):
    template_name = 'person/popup/form.html'
    form_class = PersonForm
    model = Person


class PpPersonCloseView(TemplateView):
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