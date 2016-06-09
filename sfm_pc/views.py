import json
from uuid import uuid4

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.views.generic.edit import FormView
from extra_views import FormSetView
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist

from .forms import SourceForm, OrgForm
from source.models import Source, Publication
from organization.models import Organization, OrganizationName

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        return context

class CreateSource(FormView):
    template_name = 'sfm/create-source.html'
    form_class = SourceForm
    success_url = '/create-orgs/'
    
    def get_context_data(self, **kwargs):
        context = super(CreateSource, self).get_context_data(**kwargs)
        context['publication_uuid'] = str(uuid4())
        
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        # Try to find the publication

        publication_uuid = form.data.get('publication')
        publication, created = Publication.objects.get_or_create(uuid=publication_uuid)

        if created:
            publication.title = form.data.get('publication_title')
            publication.country_iso = form.data.get('publication_country_iso')
            publication.country_name = form.data.get('publication_country_name')
            publication.save()
        
        self.publication = publication

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = super(CreateSource, self).form_valid(form)
        
        source = Source.objects.create(title=form.cleaned_data['title'],
                                       source_url=form.cleaned_data['source_url'],
                                       archive_url=form.cleaned_data['archive_url'],
                                       publication=self.publication,
                                       published_on=form.cleaned_data['published_on'])

        self.request.session['source_id'] = source.id
        return response

class CreateOrgs(FormSetView):
    template_name = 'sfm/create-orgs.html'
    form_class = OrgForm
    success_url = '/create-people/'
    extra = 1
    max_num = None

    def get_context_data(self, **kwargs):
        context = super(CreateOrgs, self).get_context_data(**kwargs)
        context['organization_uuid'] = str(uuid4())
        return context

    def post(self, request, *args, **kwargs):
        OrgFormSet = self.get_formset()
        formset = OrgFormSet(request.POST)

        print(request.POST)

        num_forms = int(formset.data['form-TOTAL_FORMS'][0])     
        
        self.organizations = []
 
        # handle aliases
        # handle names
        for i in range(0,num_forms):
            created = False
            try:
               organization = Organization.objects.get(organizationname__value=formset.data['form-' + str(i) + '-name'])
            except ObjectDoesNotExist:
               created = True
               organization = Organization.create({'Organization_OrganizationName': {'value': formset.data['form-' + str(i) + '-name'], 
                   'confidence': 1}}) # need to fix confidence thing ???
 
            #if created:
            # name, alias, classification, foundingdate, realfounding, dissolutiondate, realdissolution
            self.organizations.append(organization)

        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        response = super(CreateOrgs, self).formset_valid(formset)
        # what does the rest of this stuff do??
        return response

 
def publications_autocomplete(request):
    term = request.GET.get('q')
    publications = Publication.objects.filter(title__icontains=term).all()
    
    results = []
    for publication in publications:
        results.append({
            'text': publication.title,
            'country_iso': publication.country_iso,
            'id': str(publication.uuid),
        })
    
    return HttpResponse(json.dumps(results), content_type='application/json')

def organizations_autocomplete(request):
    term = request.GET.get('q')
    organizations = Organization.objects.filter(organizationname__value__icontains=term).all()
 
    results = []
    for organization in organizations:
        results.append({
            'text': str(organization.name),
            'id': str(organization.name),
        })
    response = {
        'results': results,
        'next_id': 1,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')

def aliases_autocomplete(request):
    term = request.GET.get('q')
    aliases = Organization.objects.filter(organizationalias__value__icontains=term).order_by().values('organizationalias__value').distinct()

    results = []
    for alias in aliases:
        results.append({
            'text': str(alias),
            'id': str(alias)
        })
    return HttpResponse(json.dumps(results), content_type='application/json')
