# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.fields.files import FieldFile
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import redirect



class Dashboard(TemplateView):
    template_name = 'sfm_pc/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        
        return context


class Login(TemplateView):
    template_name = 'account/login.html'
    form_class = AuthenticationForm

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if not request.POST.get('remember_me', None):
                    request.session.set_expiry(0)
                return redirect('/' % request.path)
            else:
                return redirect('/login' % request.path)
        else:
            return redirect('/login' % request.path)