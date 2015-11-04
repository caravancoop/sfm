import json

from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Max

from organization.models import Organization
from .models import Membership, Role, Rank


class MembershipView(TemplateView):
    template_name = 'membership/search.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipView, self).get_context_data(**kwargs)

        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()
        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


def membership_search(request):
    terms = request.GET.dict()

    membership_query = Membership.objects.all()
    page = int(terms.get('page', 1))

    column_names = [_('Role'), _('Title'), _('Rank'), _('Firest cited date'),
                     _('Last cited date')]
    keys = ['role', 'title', 'rank', 'firstciteddate', 'lastciteddate']

    paginator = Paginator(membership_query, 15)
    try:
        membership_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
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
        'column_names': column_names,
        'keys': keys,
        'objects': memberships,
        'paginator': html_paginator,
        'result_number': len(membership_query)
    }))


class MembershipUpdate(TemplateView):
    template_name = 'membership/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            membership = Membership.objects.get(pk=kwargs.get('pk'))
        except Membership.DoesNotExist:
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
        context = super(MembershipUpdate, self).get_context_data(**kwargs)
        context['title'] = "Membership"
        context['membership'] = Membership.objects.get(pk=context.get('pk'))

        return context


class MembershipCreate(TemplateView):
    template_name = 'membership/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Membership().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        membership = Membership.create(data)

        return HttpResponse(json.dumps({"success": True, "id": membership.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(MembershipCreate, self).get_context_data(**kwargs)
        context['membership'] = Membership()
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
