import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.core.urlresolvers import reverse_lazy

from extra_views import FormSetView

from membershipperson.models import MembershipPerson, Role, Rank, Context
from membershipperson.forms import MembershipPersonForm
from source.models import Source
from sfm_pc.utils import deleted_in_str

class MembershipPersonCreate(FormSetView):
    template_name = 'membershipperson/create.html'
    form_class = MembershipPersonForm
    success_url = reverse_lazy('create-geography')
    extra = 0
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding memberships, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect(reverse_lazy('create-source'))
        else:
            return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['organizations'] = self.request.session['organizations']
        context['people'] = self.request.session['people']
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        context['memberships'] = self.request.session['memberships']
        context['roles'] = [{'id': r.id, 'value': r.value} for r in Role.objects.all()]
        context['ranks'] = [{'id': r.id, 'value': r.value} for r in Rank.objects.all()]
        context['contexts'] = [{'id': c.id, 'value': c.value} for c in Context.objects.all()]
        return context

    def get_initial(self):
        data = []
        for i in self.request.session['memberships']:
            data.append({})
        return data

    def post(self, request, *args, **kwargs):
        PersonMembershipFormSet = self.get_formset()
        formset = PersonMembershipFormSet(request.POST)

 
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            membership = MembershipPerson.objects.get(id=formset.data[form_prefix + 'membership'])
            mem_data = {}
            if formset.data[form_prefix + 'role']:
                mem_data['MembershipPerson_MembershipPersonRole'] = {
                    'value': Role.objects.get(id=formset.data[form_prefix + 'role']),
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data[form_prefix + 'title']:
                mem_data['MembershipPerson_MembershipPersonTitle'] = {
                    'value': formset.data[form_prefix + 'title'],
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data[form_prefix + 'rank']:
                mem_data['MembershipPerson_MembershipPersonRank'] = {
                    'value': Rank.objects.get(id=formset.data[form_prefix + 'rank']),
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data[form_prefix + 'startcontext']:
                mem_data['MembershipPerson_MembershipStartContext'] = {
                    'value': formset.data[form_prefix + 'startcontext'],
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data.get(form_prefix + 'realstart'):
                mem_data['MembershipPerson_MembershipPersonRealStart'] = {
                    'value': formset.data[form_prefix + 'realstart'],
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data[form_prefix + 'endcontext']:
                mem_data['MembershipPerson_MembershipEndContext'] = {
                    'value': formset.data[form_prefix + 'endcontext'],
                    'confidence': 1,
                    'sources': [source]
                }
            if formset.data.get(form_prefix + 'realend'):
                mem_data['MembershipPerson_MembershipRealEnd'] = {
                    'value': formset.data[form_prefix + 'realend'],
                    'confidence': 1,
                    'sources': [source]
                }
            membership.update(mem_data)
 
        response = super().formset_valid(formset)
        return response

    def formset_invalid(self, formset):
        response = super().formset_invalid(formset)
        return response

class MembershipPersonUpdate(FormView):
    template_name = 'membershipperson/edit.html'
    form_class = MembershipPersonForm
    success_url = reverse_lazy('dashboard')
    sourced = True

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        
        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(form)
        else:
            self.source = Source.objects.get(id=request.POST.get('source'))

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def sources_list(self, obj, attribute):
        sources = [s for s in getattr(obj, attribute).get_sources()] \
                      + [self.source]
        return list(set(s for s in sources))

    def form_valid(self, form):
        response = super().form_valid(form)

        membership = MembershipPerson.objects.get(pk=self.kwargs['pk'])
        
        mem_info = {
            'MembershipPerson_MembershipPersonTitle': {
                'value': form.cleaned_data['title'],
                'confidence': 1,
                'sources': self.sources_list(membership, 'title')
            },
            'MembershipPerson_MembershipStartContext': {
                'value': form.cleaned_data['startcontext'],
                'confidence': 1,
                'sources': self.sources_list(membership, 'startcontext')
            },
            'MembershipPerson_MembershipPersonRealStart': {
                'value': form.cleaned_data['realstart'],
                'confidence': 1,
                'sources': self.sources_list(membership, 'realstart')
            },
            'MembershipPerson_MembershipEndContext': {
                'value': form.cleaned_data['endcontext'],
                'confidence': 1,
                'sources': self.sources_list(membership, 'endcontext')
            },
            'MembershipPerson_MembershipRealEnd': {
                'value': form.cleaned_data['realend'],
                'confidence': 1,
                'sources': self.sources_list(membership, 'realend')
            },
        }
        
        if form.cleaned_data.get('role'):
            mem_info['MembershipPerson_MembershipPersonRole'] = {
                'value': Role.objects.get(id=form.cleaned_data['role']),
                'confidence': 1,
                'sources': self.sources_list(membership, 'role')
            }

        if form.cleaned_data.get('rank'):
            mem_info['MembershipPerson_MembershipPersonRank'] = {
                'value': Rank.objects.get(id=form.cleaned_data['rank']),
                'confidence': 1,
                'sources': self.sources_list(membership, 'role')
            }

        membership.update(mem_info)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        membership = MembershipPerson.objects.get(pk=self.kwargs['pk'])

        form_data = {
            'title': membership.title.get_value(),
            'role': membership.role.get_value(),
            'rank': membership.rank.get_value(),
            'realstart': membership.realstart.get_value(),
            'realend': membership.realend.get_value(),
            'startcontext': membership.startcontext.get_value(),
            'endcontext': membership.endcontext.get_value(),
            'firstciteddate': membership.firstciteddate.get_value(),
            'lastciteddate': membership.lastciteddate.get_value()
        }
        
        context['form_data'] = form_data
        context['title'] = "Membership Person"
        context['membership'] = membership
        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()

        if not self.sourced:
            context['source_error'] = 'Please include the source for your changes'

        return context

#############################################
###                                       ###
### Below here are currently unused views ###
### which we'll probably need eventually  ###
###                                       ###
#############################################

class MembershipPersonDelete(DeleteView):
    model = MembershipPerson
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(MembershipPersonDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context

    def get_object(self, queryset=None):
        obj = super(MembershipPersonDelete, self).get_object()

        return obj

def membership_person_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="memberships.csv"'

    terms = request.GET.dict()
    membership_query = MembershipPerson.search(terms)

    writer = csv.writer(response)
    for membership in membership_query:
        writer.writerow([
            membership.member.get_value(),
            membership.role.get_value(),
            membership.rank.get_value(),
            membership.title.get_value(),
            repr(membership.firstciteddate.get_value()),
            repr(membership.lastciteddate.get_value()),
            membership.realstart.get_value(),
            membership.realend.get_value(),
        ])

    return response


def rank_autocomplete(request):
    term = request.GET.dict().get('term')

    ranks = Rank.objects.filter(value__icontains=term)

    ranks = [
        {
            'label': _(rank.value),
            'value': str(rank.id)
        }
        for rank in ranks
    ]

    return HttpResponse(json.dumps(ranks))


def role_autocomplete(request):
    term = request.GET.dict().get('term')

    roles = Role.objects.filter(value__icontains=term)

    roles = [
        {
            'label': _(role.value),
            'value': str(role.id)
        }
        for role in roles
    ]

    return HttpResponse(json.dumps(roles))
