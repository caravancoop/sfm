import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.admin.utils import NestedObjects
from django.contrib import messages
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS
from django.utils.translation import get_language
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from extra_views import FormSetView
from cities.models import Place, City, Country, Region, Subregion, District

from source.models import Source
from geosite.models import Geosite
from emplacement.models import Emplacement
from area.models import Area
from association.models import Association
from organization.forms import OrganizationForm, OrganizationGeographyForm
from organization.models import Organization, OrganizationName, \
    OrganizationAlias, Alias, OrganizationClassification, Classification
from sfm_pc.utils import deleted_in_str, get_geoname_by_id
from sfm_pc.base_views import BaseFormSetView, BaseUpdateView

class OrganizationCreate(BaseFormSetView):
    template_name = 'organization/create.html'
    form_class = OrganizationForm
    success_url = reverse_lazy('create-composition')
    extra = 1
    max_num = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        
        return context

    def post(self, request, *args, **kwargs):
        
        form_data = {}
        
        for key, value in request.POST.items():
            if 'alias' in key or 'classification' in key:
                form_data[key] = request.POST.getlist(key)
            else:
                form_data[key] = request.POST.get(key)
        
        self.initFormset(form_data)
        
        return self.validateFormSet()
    
    def formset_invalid(self, formset):
        response = super().formset_invalid(formset)
        
        for index, form in enumerate(formset.forms):
            alias_ids = formset.data.get('form-{}-alias'.format(index))
            classification_ids = formset.data.get('form-{}-classification'.format(index))
            
            form.aliases = []
            form.classifications = []

            if alias_ids:
                form.aliases = OrganizationAlias.objects.filter(id__in=alias_ids)

            if classification_ids:
                form.classifications = OrganizationClassification.objects.filter(id__in=classification_ids)
        
        return response

    def formset_valid(self, formset):
        forms_added = int(formset.data['form-FORMS_ADDED'][0])     
        
        self.organizations = []
        
        self.source = Source.objects.get(id=self.request.session['source_id'])

        actual_form_index = 0
        
        for i in range(0, forms_added):

            form_prefix = 'form-{0}-'.format(i)
            actual_form_prefix = 'form-{0}-'.format(actual_form_index)

            form_key_mapper = {k: k.replace(str(i), str(actual_form_index)) \
                                   for k in formset.data.keys() \
                                       if k.startswith(form_prefix)}
            
            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            
            try:
                name_id = formset.data[name_id_key]
            except MultiValueDictKeyError:
                continue
            
            name_text = formset.data[name_text_key]
            
            org_info = {
                'Organization_OrganizationName': {
                    'value': name_text, 
                    'confidence': 1,
                    'sources': [self.source]
                },
            }
            
            try:
                organization = Organization.objects.get(id=name_id)
                sources = self.sourcesList(organization, 'name')
                
                org_info["Organization_OrganizationName"]['sources'] = sources
            
            except (Organization.DoesNotExist, ValueError):
                organization = Organization.create(org_info)

            # Save aliases first
            
            aliases = formset.data.get(form_prefix + 'alias_text')
            
            if aliases:
                
                for alias in aliases:
                    
                    alias_obj, created = Alias.objects.get_or_create(value=alias)

                    oa_obj, created = OrganizationAlias.objects.get_or_create(value=alias_obj,
                                                                              object_ref=organization,
                                                                              lang=get_language())
                    oa_obj.sources.add(self.source)
                    oa_obj.save()

            # Next do classifications
            
            classifications = formset.data.get(form_prefix + 'classification_text')
            
            if classifications:
                for classification in classifications:
                    
                    class_obj, created = Classification.objects.get_or_create(value=classification)
                    
                    oc_obj, created = OrganizationClassification.objects.get_or_create(value=class_obj,
                                                                                       object_ref=organization,
                                                                                       lang=get_language())
                    oc_obj.sources.add(self.source)
                    oc_obj.save()
            
            # Now get division ID

            division_id = formset.data.get(form_prefix + 'division_id')

            self.organizations.append(organization)
            
            actual_form_index += 1
        
        self.request.session['organizations'] = [{'id': o.id, 'name': o.name.get_value().value} \
                                                     for o in self.organizations]
        response = super().formset_valid(formset)
        
        return response


class OrganizationUpdate(BaseUpdateView):
    template_name = 'organization/edit.html'
    form_class = OrganizationForm
    success_url = reverse_lazy('dashboard')
    sourced = True

    def post(self, request, *args, **kwargs):

        self.checkSource(request)
        
        self.aliases = request.POST.getlist('alias')
        
        self.validateForm(request.POST)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        organization = Organization.objects.get(pk=self.kwargs['pk'])
        
        org_info = {
            'Organization_OrganizationName': {
                'value': form.cleaned_data['name_text'],
                'confidence': 1,
                'sources': self.sourcesList(organization, 'name'),
            },
            'Organization_OrganizationClassification': {
                'value': form.cleaned_data['classification'],
                'confidence': 1,
                'sources': self.sourcesList(organization, 'classification'),
            },
        }
        
        organization.update(org_info)
        
        if self.aliases:
            
            aliases = []

            for alias in self.aliases:
            
                try:
                    # try to get an object based on ID
                    oa_obj = OrganizationAlias.objects.get(id=alias)
                    oa_obj.sources.add(self.source)
                    oa_obj.save()

                    aliases.append(oa_obj)
                except ValueError:
                    alias_obj, created = Alias.objects.get_or_create(value=alias)

                    oa_obj = OrganizationAlias.objects.create(value=alias_obj,
                                                              object_ref=organization,
                                                              lang=get_language())
                    oa_obj.sources.add(self.source)
                    oa_obj.save()

            organization.organizationalias_set = aliases
            organization.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        organization = Organization.objects.get(pk=self.kwargs['pk'])
        
        
        form_data = {
            'name': organization.name.get_value(),
            'classification': [i.get_value() for i in organization.classification.get_list()],
            'alias': [i.get_value() for i in organization.aliases.get_list()],
        }

        context['form_data'] = form_data
        context['title'] = 'Organization'
        context['source_object'] = organization
        context['source'] = Source.objects.filter(id=self.request.GET.get('source_id')).first()
 

        if not self.sourced:
            context['source_error'] = 'Please include the source for your changes'
        
        return context

def classification_autocomplete(request):
    term = request.GET.get('q')
    classifications = Classification.objects.filter(value__icontains=term).all()
    
    results = []
    for classification in classifications:
        results.append({
            'text': classification.value,
            'id': classification.id,
        })

    return HttpResponse(json.dumps(results), content_type='application/json')

def organization_autocomplete(request):
    term = request.GET.get('q')
    organizations = Organization.objects.filter(organizationname__value__icontains=term).all()

    results = []
    for organization in organizations:
        results.append({
            'text': str(organization.name),
            'id': organization.id,
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def alias_autocomplete(request):
    term = request.GET.get('q')
    alias_query = OrganizationAlias.objects.filter(value__value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value.value,
            'id': alias.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def division_autocomplete(request):
    term = request.GET.get('q')
    countries = Country.objects.filter(name__icontains=term)

    results = []
    for country in countries:
        results.append({
            'text': str(country.name),
            'id': country.id,
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

class OrganizationCreateGeography(BaseFormSetView):
    template_name = 'organization/create-geography.html'
    form_class = OrganizationGeographyForm
    success_url = reverse_lazy('create-event')
    extra = 1
    max_num = None

   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        organizations = self.request.session['organizations']
        people = self.request.session['people']
  
        context['people'] = people 
        context['organizations'] = organizations
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        
        form = self.form_class()
        context['geo_types'] = form.fields['geography_type'].choices
        
        return context

    def formset_valid(self, formset):
        source = Source.objects.get(id=self.request.session['source_id'])
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        
        for i in range(0, num_forms):
            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            startdate = formset.data[form_prefix + 'startdate']
            enddate = formset.data[form_prefix + 'enddate']
            org_id = formset.data[form_prefix + 'org']
            geoid = formset.data[form_prefix + 'geoname']
            geotype = formset.data[form_prefix + 'geotype']
            
            geo = get_geoname_by_id(geoid)
            parent = geo.parent
            admin1 = parent.name
            admin2 = parent.parent.name
            coords = getattr(geo, 'location')
            
            if formset.data[form_prefix + 'geography_type'] == 'Site':
                
                site, created = Geosite.objects.get_or_create(geositegeonameid__value=geo.id)
                
                site_data = {
                    'Geosite_GeositeName': {
                        'value': formset.data[form_prefix + 'name'],
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Geosite_GeositeGeoname': {
                        'value': geo.name,
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Geosite_GeositeGeonameId': {
                        'value': geo.id,
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Geosite_GeositeAdminLevel1': {
                        'value': admin1,
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Geosite_GeositeAdminLevel2': {
                        'value': admin2,
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Geosite_GeositeCoordinates': {
                        'value': coords,
                        'confidence': 1,
                        'sources': [source]
                    }
                }
                site.update(site_data)
                
                emp, created = Emplacement.objects.get_or_create(emplacementorganization__value=org_id,
                                                                 emplacementsite__value=site.id)
                emp_data = {
                    'Emplacement_EmplacementOrganization': {
                        'value': Organization.objects.get(id=org_id),
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Emplacement_EmplacementSite': {
                        'value': site,
                        'confidence': 1,
                        'sources': [source]
                    },
                }
                
                if formset.data[form_prefix + 'startdate']:
                    emp_data['Emplacement_EmplacementStartDate'] = {
                        'value': formset.data[form_prefix + 'startdate'],
                        'confidence': 1,
                        'sources': [source]
                    }
                
                if formset.data[form_prefix + 'enddate']:
                    emp_data['Emplacement_EmplacementEndDate'] = {
                        'value': formset.data[form_prefix + 'enddate'],
                        'confidence': 1,
                        'sources': [source]
                    }

                emp.update(emp_data)
            
            else:
                
                area, created = Area.objects.get_or_create(areageonameid__value=geo.id)
                
                if created:
                    
                    code_obj, created = Code.objects.get_or_create(value=code)
                    
                    area_data = {
                        'Area_AreaName': {
                            'value': formset.data[form_prefix + 'name'],
                            'confidence': 1,
                            'sources': [source]
                        },
                        'Area_AreaGeoname': {
                            'value': geo.name,
                            'confidence': 1,
                            'sources': [source]
                        },
                        'Area_AreaGeonameId': {
                            'value': geo.id,
                            'confidence': 1,
                            'sources': [source]
                        },
                        'Area_AreaCode': {
                            'value': code_obj,
                            'confidence': 1,
                            'sources': [source]
                        },
                        'Area_AreaGeometry': {
                            'value': geometry,
                            'confidence': 1,
                            'sources': [source]
                        }
                    }
                    area.update(area_data)
                
                assoc, created = Association.objects.get_or_create(associationorganization__value=org_id,
                                                                   associationarea__value=area.id)
                
                assoc_data = {
                    'Association_AssociationStartDate': {
                        'value': formset.data[form_prefix + 'startdate'],
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Association_AssociationEndDate': {
                        'value': formset.data[form_prefix + 'enddate'],
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Association_AssociationOrganization': {
                        'value': Organization.objects.get(id=org_id),
                        'confidence': 1,
                        'sources': [source]
                    },
                    'Association_AssociationArea': {
                        'value': area,
                        'confidence': 1,
                        'sources': [source]
                    }
                }
                assoc.update(assoc_data)
        
        response = super().formset_valid(formset)
        
        return response


#############################################
###                                       ###
### Below here are currently unused views ###
### which we'll probably need eventually  ###
###                                       ###
#############################################

class OrganizationDelete(DeleteView):
    model = Organization
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(OrganizationDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        context['title'] = _("Organization")
        context['model'] = "organization"
        return context

    def get_object(self, queryset=None):
        obj = super(OrganizationDelete, self).get_object()

        return obj

def organization_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="organizations.csv"'

    terms = request.GET.dict()
    organization_query = Organization.search(terms)

    writer = csv.writer(response)
    for organization in organization_query:
        writer.writerow([
            organization.id,
            organization.name.get_value(),
            organization.alias.get_value(),
            organization.classification.get_value(),
        ])

    return response

