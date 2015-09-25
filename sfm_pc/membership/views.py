import json

from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Max

from organization.models import Organization
from .models import Membership, Role, Rank


class MembershipView(TemplateView):
    template_name = 'membership/search.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipView, self).get_context_data(**kwargs)

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'membershipperson__value'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        membership_query = (Membership.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))

        role = self.request.GET.get('role')
        if role:
            org_query = membership_query.filter(membershiprole__id=role)

        context['memberships'] = membership_query
        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()

        return context


class MembershipUpdate(TemplateView):
    template_name = 'membership/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['membership'])
        try:
            membership = Membership.objects.get(pk=kwargs.get('pk'))
        except Membership.DoesNotExist:
            msg = "This membership does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        errors = membership.update(data)
        if errors is None:
            return HttpResponse(
                json.dumps({"success": True}),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
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
        data = json.loads(request.POST.dict()['membership'])
        membership = Membership.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(MembershipCreate, self).get_context_data(**kwargs)
        context['membership'] = Membership()
        context['roles'] = Role.objects.all()
        context['ranks'] = Rank.objects.all()

        return context
