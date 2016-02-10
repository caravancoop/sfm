import json
import csv

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.views.generic.edit import DeleteView
from django.contrib.admin.util import NestedObjects
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from organization.models import Organization
from .models import MembershipPerson, Role, Rank
from sfm_pc.utils import deleted_in_str

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


class MembershipPersonUpdate(TemplateView):
    template_name = 'membershipperson/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            membership = MembershipPerson.objects.get(pk=kwargs.get('pk'))
        except MembershipPerson.DoesNotExist:
            msg = "This membership does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = membership.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )
        membership.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(MembershipPersonUpdate, self).get_context_data(**kwargs)
        context['title'] = "Membership Person"
        context['membership'] = MembershipPerson.objects.get(pk=context.get('pk'))

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
