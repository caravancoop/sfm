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
from organization.models import Organization, OrganizationName, \
    OrganizationAlias, Alias, Classification

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
        context['classifications'] = Classification.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        OrgFormSet = self.get_formset()
        formset = OrgFormSet(request.POST)

        num_forms = int(formset.data['form-TOTAL_FORMS'][0])     
        
        self.organizations = []
 
        form_data = {}
        for i in range(0,num_forms):

            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            
            form = {k: formset.data.getlist(k) for k in form_keys}

            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            
            name_id = formset.data[name_id_key]
            name_text = formset.data[name_text_key]
           
            if name_id == 'None':
                return self.formset_invalid(formset)

            elif name_id == '-1':
                org_info = {
                    'Organization_OrganizationName': {
                        'value': name_text, 
                        'confidence': 1
                    },
                }
                
                organization = Organization.create(org_info)      
            else:
                organization = Organization.objects.get(id=name_id)
                
            # TODO: Figure out the aliases, classification, dates, booleans
            # add aliases to this organization
            
            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.getlist(alias_text_key)
            
            form[alias_id_key] = []

            for alias in aliases:
                
                alias_obj, created = Alias.objects.get_or_create(value=alias)

                alias_data = {
                    'Organization_OrganizationAlias': {
                        'value': alias_obj, 
                        'confidence': 1
                    }
                }
                organization.update(alias_data)
                
                form[alias_id_key].append(alias_obj.id)
           
            classification = formset.data.get(form_prefix + 'classification')
            form[form_prefix + 'classification'] = [None]

            if classification:
                print('classification', classification)
                classification_obj = Classification.objects.get(id=classification)
                organization.update({
                    'Organization_OrganizationClassification': {
                        'value': classification_obj,
                        'confidence': 1
                    }
                })

                form[form_prefix + 'classification'] = [classification_obj.id]
            
            form[form_prefix + 'foundingdate'] = form[form_prefix + 'foundingdate'][0]
            realfounding = form_prefix + 'realfounding' in formset.data.keys()
            
            form[form_prefix + 'dissolutiondate'] = form[form_prefix + 'dissolutiondate'][0]
            realdissolution = form_prefix + 'realdissolution' in formset.data.keys()
 
            self.organizations.append(organization)

            del form[alias_text_key]

            form[name_id_key] = organization.name.get_field().id

            self.organizations.append(organization)
            form_data.update(form)
        
        form_data['form-TOTAL_FORMS'] = num_forms
        form_data['form-INITIAL_FORMS'] = '0'
        form_data['form-MIN_NUM_FORMS'] = ''
        form_data['form-MAX_NUM_FORMS'] = ''
        
        dummy_formset = OrgFormSet(form_data)
        
        if dummy_formset.is_valid():
            return self.formset_valid(dummy_formset)
        else:
            return self.formset_invalid(dummy_formset)

 
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
            'id': organization.id,
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def aliases_autocomplete(request):
    term = request.GET.get('q')
    alias_query = OrganizationAlias.objects.filter(value__value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value.value,
            'id': alias.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

    
