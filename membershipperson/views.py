import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView, FormView
from django.contrib.admin.utils import NestedObjects
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from .models import MembershipPerson, Role, Rank
from sfm_pc.utils import deleted_in_str
from sfm_pc.forms import PersonMembershipForm


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


class MembershipPersonView(TemplateView):
    template_name = 'membershipperson/search.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipPersonView, self).get_context_data(**kwargs)

        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()
        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


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


def membership_person_search(request):
    terms = request.GET.dict()

    membership_query = MembershipPerson.search(terms)

    page = int(terms.get('page', 1))

    keys = ['role', 'title', 'rank', 'firstciteddate', 'lastciteddate']

    paginator = Paginator(membership_query, 15)
    try:
        membership_page = paginator.page(page)
    except PageNotAnInteger:
        membership_page = paginator.page(1)
        page = 1
    except EmptyPage:
        membership_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    memberships = [
        {
            "id": membership.id,
            "role": str(membership.role.get_value()),
            "title": str(membership.title.get_value()),
            "rank": str(membership.rank.get_value()),
            "firstciteddate": str(membership.firstciteddate.get_value()),
            "lastciteddate": str(membership.lastciteddate.get_value()),
        }
        for membership in membership_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': membership_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': memberships,
        'paginator': html_paginator,
        'result_number': len(membership_query)
    }))


class MembershipPersonUpdate(FormView):
    template_name = 'membershipperson/edit.html'
    form_class = PersonMembershipForm
    success_url = '/'
    sourced = True

    def post(self, request, *args, **kwargs):
        form = PersonMembershipForm(request.POST)
        
        if not request.POST.get('source'):
            self.sourced = False
            return self.form_invalid(form)
        else:
            self.source = Source.objects.get(id=request.POST.get('source'))

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)

        membership = MembershipPerson.objects.get(pk=self.kwargs['pk'])
        mem_info = {
            'MembershipPerson_MembershipPersonRole' : {
                'value': Role.objects.get(id=form.cleaned_data['role']),
                'confidence': 1,
                'source': list(set(list(membership.role.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipPersonTitle': {
                'value': form.cleaned_data['title'],
                'confidence': 1,
                'source': list(set(list(membership.title.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipPersonRank': {
                'value': Rank.objects.get(id=form.cleaned_data['rank']),
                'confidence': 1,
                'source': list(set(list(membership.rank.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipStartContext': {
                'value': form.cleaned_data['startcontext'],
                'confidence': 1,
                'source': list(set(list(membership.startcontext.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipPersonRealStart': {
                'value': form.cleaned_data['realstart'],
                'confidence': 1,
                'source': list(set(list(membership.realstart.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipEndContext': {
                'value': form.cleaned_data['endcontext'],
                'confidence': 1,
                'source': list(set(list(membership.endcontext.get_sources() + [self.source])))
            },
            'MembershipPerson_MembershipRealEnd': {
                'value': form.cleaned_data['realend'],
                'confidence': 1,
                'source': list(set(list(membership.realend.get_sources() + [self.source])))
            },
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
            'lastciteddate': membership.lastciteddate.get_value(),
        }
        
        context['form_data'] = form_data
        context['title'] = "Membership Person"
        context['membership'] = membership
        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()

        if not self.sourced:
            context['source_error'] = 'Please include the source for your changes'

        return context


class MembershipPersonCreate(TemplateView):
    template_name = 'membershipperson/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = MembershipPerson().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        membership = MembershipPerson.create(data)

        return HttpResponse(json.dumps({"success": True, "id": membership.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(MembershipPersonCreate, self).get_context_data(**kwargs)
        context['membership'] = MembershipPerson()
        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()

        return context


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
