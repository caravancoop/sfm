import json
from uuid import uuid4

from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic.edit import FormView
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.translation import get_language
from django.db import connection

from extra_views import FormSetView
from reversion.models import Version

from .forms import SourceForm, OrgForm, PersonForm, PersonMembershipForm, \
    OrganizationGeographyForm, ViolationForm
from source.models import Source, Publication
from organization.models import Organization, OrganizationName, \
    OrganizationAlias, Alias as OrganizationAliasObject, Classification
from person.models import Person, PersonName, PersonAlias, \
    Alias as PersonAliasObject
from membershipperson.models import MembershipPerson, Role, Rank, Context
from association.models import Association
from emplacement.models import Emplacement
from cities.models import Place, City, Country, Region, Subregion, District
from geosite.models import Geosite
from area.models import Area, Code
from violation.models import Violation, Type

SEARCH_CONTENT_TYPES = {
    'Source': Source,
    'Publication': Publication,
    'Organization': Organization,
    'Person': Person,
    'Violation': Violation,
}

GEONAME_TYPES = {
    'country': (Country, 'name',),
    'city': (City, 'name_std',),
    'district': (District, 'name_std',),
    'region': (Region, 'name_std',),
    'subregion': (Subregion, 'name_std',),
}

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        
        sources = Version.objects.filter(content_type__model='source').get_unique()
        context['edits'] = sorted(sources, 
                                  key=lambda x: x.revision.date_created, 
                                  reverse=True)
        
        if context['edits']:

            context['source_properties'] = [p for p in \
                                                dir(context['edits'][0].object) \
                                                    if p.endswith('_related')]
        
        session_keys = ['organizations', 'people', 'memberships', 'source_id']
        
        for session_key in session_keys:
            if self.request.session.get(session_key):
                del self.request.session[session_key]
        
        return context

def view_source(request, source_id):
    try:
        source = Source.objects.get(id=source_id)
    except Source.DoesNotExist:
        return HttpResponseNotFound()
    return render(request, 'sfm/view-source.html', context={'source': source})

class CreateSource(FormView):
    template_name = 'sfm/create-source.html'
    form_class = SourceForm
    success_url = '/create-orgs/'
    
    def get_context_data(self, **kwargs):
        context = super(CreateSource, self).get_context_data(**kwargs)
        context['publication_uuid'] = str(uuid4())       

        pub_title = self.request.POST.get('publication_title')
        if pub_title:
            context['publication_title'] = pub_title

        pub_country = self.request.POST.get('publication_country')
        if pub_country:
            context['publication_country'] = pub_country

        context['countries'] = Country.objects.all()
 
        if self.request.session.get('source_id'):
            del self.request.session['source_id']
        
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        response = super(CreateSource, self).form_valid(form)
        # Try to find the publication

        publication_uuid = form.data.get('publication')
        
        if publication_uuid == 'None':
            return self.form_invalid(form)

        publication, created = Publication.objects.get_or_create(id=publication_uuid)

        if created:
            publication.title = form.data.get('publication_title')
            publication.country = form.data.get('publication_country')
            publication.save()
        
        self.publication = publication

       
        source, created = Source.objects.get_or_create(title=form.cleaned_data['title'],
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

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding an organization, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('/create-source/')
        else:
            return super(CreateOrgs, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(CreateOrgs, self).get_context_data(**kwargs)
        context['classifications'] = Classification.objects.all()

        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        
        return context

    def post(self, request, *args, **kwargs):
        
        OrgFormSet = self.get_formset()
        
        management_keys = [
            'form-MAX_NUM_FORMS', 
            'form-MIN_NUM_FORMS', 
            'form-INITIAL_FORMS', 
            'form-TOTAL_FORMS', 
            'form-FORMS_ADDED'
        ]

        form_data = {}
        
        for key, value in request.POST.items():
            if 'alias' in key:
                form_data[key] = request.POST.getlist(key)
            else:
                form_data[key] = request.POST.get(key)
        
        formset = OrgFormSet(form_data)
        
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)
    
    def formset_invalid(self, formset):
        response = super().formset_invalid(formset)
        
        for index, form in enumerate(formset.forms):
            alias_ids = formset.data.get('form-{}-alias'.format(index))
            if alias_ids:
                for alias_id in alias_ids:
                    try:
                        org_alias = OrganizationAlias.objects.get(id=alias_id)
                    except ValueError:
                        org_alias = None
                    
                    if org_alias:
                        try:
                            form.aliases.append(org_alias)
                        except AttributeError:
                            form.aliases = [org_alias]
            else:
                form.aliases = None
        
        return response

    def formset_valid(self, formset):
        forms_added = int(formset.data['form-FORMS_ADDED'][0])     
        
        self.organizations = []
        
        source = Source.objects.get(id=self.request.session['source_id'])

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
                    'sources': [source]
                },
            }
            
            try:
                organization = Organization.objects.get(id=name_id)
                existing_sources = organization.organizationname_set.all()[0].sources.all()
                
                org_info["Organization_OrganizationName"]['sources'].extend(existing_sources)
            
            except (Organization.DoesNotExist, ValueError):
                organization = Organization.create(org_info)

            # Save aliases first
            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.get(alias_text_key)
            
            if aliases:
                
                for alias in aliases:
                    
                    alias_obj, created = OrganizationAliasObject.objects.get_or_create(value=alias)

                    oa_obj, created = OrganizationAlias.objects.get_or_create(value=alias_obj,
                                                                              object_ref=organization,
                                                                              lang=get_language())
                    oa_obj.sources.add(source)
                    oa_obj.save()

            # Next do classification
            classification = formset.data.get(form_prefix + 'classification')
            
            if classification:
                
                classification_obj = Classification.objects.get(id=classification)
                org_info['Organization_OrganizationClassification'] = {
                    'value': classification_obj,
                    'confidence': 1,
                    'sources': [source]
                }

            # Now do dates
            realfounding = form_prefix + 'realfounding' in formset.data.keys()

            # Add to dict used to update org
            org_info.update({
                'Organization_OrganizationFoundingDate': {
                    'value': formset.data.get(form_prefix + 'foundingdate'),
                    'confidence': 1,
                    'sources': [source],
                },
                'Organization_OrganizationRealFounding': {
                    'value': realfounding,
                    'confidence': 1,
                    'sources': [source],
                },
            })
            
            # Now update org
            organization.update(org_info)
 
            self.organizations.append(organization)
            
            actual_form_index += 1
        
        self.request.session['organizations'] = [{'id': o.id, 'name': o.name.get_value().value} \
                                                     for o in self.organizations]
        
        response = super().formset_valid(formset)
        return response

class CreatePeople(FormSetView):
    template_name = 'sfm/create-people.html'
    form_class = PersonForm
    success_url = '/membership-info/'
    extra = 1
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding a person, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('/create-source/')
        else:
            return super(CreatePeople, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreatePeople, self).get_context_data(**kwargs)
        
        context['organizations'] = self.request.session['organizations']
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        return context

    def post(self, request, *args, **kwargs):
        PersonFormSet = self.get_formset()
        formset = PersonFormSet(request.POST)       
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        response = super().formset_valid(formset)
        num_forms = int(formset.data['form-TOTAL_FORMS'][0])
        
        self.people = []
        self.memberships = []

        source = Source.objects.get(id=self.request.session['source_id'])

        for i in range(0,num_forms):
            first = True

            form_prefix = 'form-{0}-'.format(i)
            
            form_keys = [k for k in formset.data.keys() \
                             if k.startswith(form_prefix)]
            
            name_id_key = 'form-{0}-name'.format(i)
            name_text_key = 'form-{0}-name_text'.format(i)
            
            name_id = formset.data[name_id_key]
            name_text = formset.data[name_text_key]
           
            if name_id == 'None':
                return self.formset_invalid(formset)

            elif name_id == '-1':
                person_info = {
                    'Person_PersonName': {
                        'value': name_text, 
                        'confidence': 1,
                        'sources': [source],
                    },
                }
                
                person = Person.create(person_info)      
            else:
                person = Person.objects.get(id=name_id)
            
            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.getlist(alias_text_key)
            
            for alias in aliases:
                
                alias_obj, created = PersonAliasObject.objects.get_or_create(value=alias)

                pa_obj, created = PersonAlias.objects.get_or_create(object_ref=person,
                                                                    value=alias_obj)
                
                pa_obj.sources.add(source)
                pa_obj.save()

            date_key = 'form-{0}-deathdate'.format(i)
            deathdate = formset.data.get(date_key)

            if deathdate:
                death_data = {
                    'Person_PersonDeathDate': {
                        'value': deathdate,
                        'confidence': 1,
                        'sources': [source],
                    }
                }
                person.update(death_data)
           
            self.people.append(person)
            
            orgs_key = 'form-{0}-orgs'.format(i)
            orgs = formset.data.getlist(orgs_key)

            for org in orgs:
                mem_data = {
                    'MembershipPerson_MembershipPersonMember': {
                        'value': person,
                        'confidence': 1,
                        'sources': [source],
                    },
                    'MembershipPerson_MembershipPersonOrganization': { 
                        'value': Organization.objects.get(id=org),
                        'confidence': 1,
                        'sources': [source],
                    }
                }
                membership = MembershipPerson.create(mem_data)
                self.memberships.append({
                    'person': str(person.name),
                    'organization': str(Organization.objects.get(id=org).name),
                    'membership': membership.id,
                    'first': first
                })
                first = False
        
        self.request.session['people'] = [{'id': p.id, 'name': p.name.get_value().value} \
                                                     for p in self.people]
        self.request.session['memberships'] = self.memberships
        return response

class MembershipInfo(FormSetView):
    template_name = 'sfm/membership-info.html'
    form_class = PersonMembershipForm
    success_url = '/organization-geo/'
    extra = 0
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding memberships, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('/create-source/')
        else:
            return super(MembershipInfo, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MembershipInfo, self).get_context_data(**kwargs)
        
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
                    'source': [source]
                }
            if formset.data[form_prefix + 'title']:
                mem_data['MembershipPerson_MembershipPersonTitle'] = {
                    'value': formset.data[form_prefix + 'title'],
                    'confidence': 1,
                    'source': [source]
                }
            if formset.data[form_prefix + 'rank']:
                mem_data['MembershipPerson_MembershipPersonRank'] = {
                    'value': Rank.objects.get(id=formset.data[form_prefix + 'rank']),
                    'confidence': 1,
                    'source': [source]
                }
            if formset.data[form_prefix + 'startcontext']:
                mem_data['MembershipPerson_MembershipStartContext'] = {
                    'value': formset.data[form_prefix + 'startcontext'],
                    'confidence': 1,
                    'source': [source]
                }
            if formset.data.get(form_prefix + 'realstart'):
                mem_data['MembershipPerson_MembershipPersonRealStart'] = {
                    'value': formset.data[form_prefix + 'realstart'],
                    'confidence': 1,
                    'source': [source]
                }
            if formset.data[form_prefix + 'endcontext']:
                mem_data['MembershipPerson_MembershipEndContext'] = {
                    'value': formset.data[form_prefix + 'endcontext'],
                    'confidence': 1,
                    'source': [source]
                }
            if formset.data.get(form_prefix + 'realend'):
                mem_data['MembershipPerson_MembershipRealEnd'] = {
                    'value': formset.data[form_prefix + 'realend'],
                    'confidence': 1,
                    'source': [source]
                }
            membership.update(mem_data)
 
        response = super().formset_valid(formset)
        return response

    def formset_invalid(self, formset):
        response = super().formset_invalid(formset)
        return response

class OrganizationGeographies(FormSetView):
    template_name = 'sfm/organization-geo.html'
    form_class = OrganizationGeographyForm
    success_url = '/create-events/'
    extra = 1
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding geographies, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('/create-source/')
        else:
            return super(OrganizationGeographies, self).dispatch(*args, **kwargs)

   
    def get_context_data(self, **kwargs):
        context = super(OrganizationGeographies, self).get_context_data(**kwargs)
        
        organizations = self.request.session['organizations']
        people = self.request.session['people']
  
        context['people'] = people 
        context['organizations'] = organizations
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        
        form = self.form_class()
        context['geo_types'] = form.fields['geography_type'].choices
        
        return context

    def post(self, request, *args, **kwargs):
        organizations = self.request.session['organizations']

        OrganizationGeographyFormset = self.get_formset()
        formset = OrganizationGeographyFormset(request.POST)
 
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
            startdate = formset.data[form_prefix + 'startdate']
            enddate = formset.data[form_prefix + 'enddate']
            org_id = formset.data[form_prefix + 'org']
            geoid = formset.data[form_prefix + 'geoname']
            geotype = formset.data[form_prefix + 'geotype']
            
            if geotype == 'country':
                geo = Country.objects.get(id=geoid)
                admin1 = None
                admin2 = None
                coords = None
                code = geo.code
                geometry = None 
            
            elif geotype == 'region':
                geo = Region.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
                code = geo.code
                geometry = None
            
            elif geotype == 'subregion':
                geo = Subregion.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
                code = geo.code
                geometry = None
            
            elif geotype == 'city':
                geo = City.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location
                code = None
                geometry = None
            
            else:
                geo = District.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location
                code = None
                geometry = None
            
            if formset.data[form_prefix + 'geography_type'] == 'Site':
                get_site = Geosite.objects.filter(geositegeonameid__value=geo.id)
                if len(get_site) == 0:
                    site_data = {
                        'Geosite_GeositeName': {
                            'value': formset.data[form_prefix + 'name'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Geosite_GeositeGeoname': {
                            'value': geo.name,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Geosite_GeositeGeonameId': {
                            'value': geo.id,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Geosite_GeositeAdminLevel1': {
                            'value': admin1,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Geosite_GeositeAdminLevel2': {
                            'value': admin2,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Geosite_GeositeCoordinates': {
                            'value': coords,
                            'confidence': 1,
                            'source': [source]
                        }
                    }
                    site = Geosite.create(site_data)
                else:
                    site = get_site[0]
                get_emp = Emplacement.objects.filter(emplacementorganization__value=org_id).filter(emplacementsite__value=site.id).first()
                if get_emp:
                    # update dates?
                    # add sources
                    emp_data = {
                        'Emplacement_EmplacementStartDate': {
                            'value': formset.data[form_prefix + 'startdate'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Emplacement_EmplacementEndDate': {
                            'value': formset.data[form_prefix + 'enddate'],
                            'confidence': 1,
                            'source': [source]
                        } 
                    } 
                    get_emp.update(emp_data)
                else:
                    emp_data = {
                        'Emplacement_EmplacementOrganization': {
                            'value': Organization.objects.get(id=org_id),
                            'confidence': 1,
                            'source': [source]
                        },
                        'Emplacement_EmplacementSite': {
                            'value': site,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Emplacement_EmplacementStartDate': {
                            'value': formset.data[form_prefix + 'startdate'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Emplacement_EmplacementEndDate': {
                            'value': formset.data[form_prefix + 'enddate'],
                            'confidence': 1,
                            'source': [source]
                        }
                    }
                    Emplacement.create(emp_data)
            else:
                get_area = Area.objects.filter(areageonameid__value = geo.id)
                if len(get_area) == 0:
                    code_obj = Code.objects.create(value=code)
                    area_data = {
                        'Area_AreaName': {
                            'value': formset.data[form_prefix + 'name'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Area_AreaGeoname': {
                            'value': geo.name,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Area_AreaGeonameId': {
                            'value': geo.id,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Area_AreaCode': {
                            'value': code_obj,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Area_AreaGeometry': {
                            'value': geometry,
                            'confidence': 1,
                            'source': [source]
                        }
                    }
                    area = Area.create(area_data)
                else:
                    area = get_area[0]
                get_assoc = Association.objects.filter(associationorganization__value=org_id).filter(associationarea__value=area.id).first()
                if get_assoc:
                    # update dates?
                    # add sources
                    assoc_data = {
                        'Association_AssociationStartDate': {
                            'value': formset.data[form_prefix + 'startdate'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Association_AssociationEndDate': {
                            'value': formset.data[form_prefix + 'enddate'],
                            'confidence': 1,
                            'source': [source]
                        } 
                    } 
                    get_assoc.update(assoc_data)
                else:
                    assoc_data = {
                        'Association_AssociationOrganization': {
                            'value': Organization.objects.get(id=org_id),
                            'confidence': 1,
                            'source': [source]
                        },
                        'Association_AssociationArea': {
                            'value': area,
                            'confidence': 1,
                            'source': [source]
                        },
                        'Association_AssociationStartDate': {
                            'value': formset.data[form_prefix + 'startdate'],
                            'confidence': 1,
                            'source': [source]
                        },
                        'Association_AssociationEndDate': {
                            'value': formset.data[form_prefix + 'enddate'],
                            'confidence': 1,
                            'source': [source]
                        }
                    }
                    Association.create(assoc_data)
        response = super().formset_valid(formset)
        
        return response

class CreateViolations(FormSetView):
    template_name = 'sfm/create-events.html'
    form_class = ViolationForm
    success_url = '/'
    extra = 1
    max_num = None

    def dispatch(self, *args, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding an event, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('/create-source/')
        else:
            return super(CreateViolations, self).dispatch(*args, **kwargs)

   
    def get_context_data(self, **kwargs):
        context = super(CreateViolations, self).get_context_data(**kwargs)
        
        organizations = self.request.session.get('organizations')
        people = self.request.session.get('people')

        context['types'] = Type.objects.all()
        context['people'] = people         
        context['organizations'] = organizations
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        return context

    def post(self, request, *args, **kwargs):
        organizations = self.request.session['organizations']

        ViolationFormset = self.get_formset()
        formset = ViolationFormset(request.POST)

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
            startdate = formset.data[form_prefix + 'startdate']
            enddate = formset.data[form_prefix + 'enddate']
            locationdescription = formset.data[form_prefix + 'locationdescription']
            geoid = formset.data[form_prefix + 'geoname']
            geotype = formset.data[form_prefix + 'geotype']
            description = formset.data[form_prefix + 'description']
            perpetrators = formset.data[form_prefix + 'perpetrators']
            orgs = formset.data[form_prefix + 'orgs']
            vtype = formset.data[form_prefix + 'vtype'] 

            newtype, flag = Type.objects.get_or_create(id=vtype)

            if geotype == 'country':
                geo = Country.objects.get(id=geoid)
                admin1 = None
                admin2 = None
                coords = None
            elif geotype == 'region':
                geo = Region.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
            elif geotype == 'subregion':
                geo = Subregion.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = None
            elif geotype == 'city':
                geo = City.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location
            else:
                geo = District.objects.get(id=geoid)
                admin1 = geo.parent.name
                admin2 = geo.parent.parent.name
                coords = geo.location

            violation_data = {
                'Violation_ViolationDescription': {
                   'value': description,
                   'sources': [source],
                   'confidence': 1
                },
                'Violation_ViolationLocationDescription': {
                    'value': locationdescription,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationType': {
                    'value': newtype,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationPerpetrator': {
                    'value': Person.objects.get(id=perpetrators),
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationPerpetratorOrganization': {
                    'value': Organization.objects.get(id=orgs),
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationAdminLevel1': {
                    'value': admin1,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationAdminLevel2': {
                    'value': admin2,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationGeoname': {
                    'value': geo.name,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationGeonameId': {
                    'value': geo.id,
                    'sources': [source],
                    'confidence': 1
                },
                'Violation_ViolationLocation': {
                    'value': coords,
                    'sources': [source],
                    'confidence': 1
                }
            }
            Violation.create(violation_data)
        response = super().formset_valid(formset)
        return response


def search(request):
    query = request.GET.get('q')
    filters = request.GET.getlist('entity_type')
    location = request.GET.get('geoname_id')
    radius = request.GET.get('radius')
    geoname_type = request.GET.get('geoname_type')

    results = {}
    select = ''' 
        SELECT DISTINCT ON(content_type, object_ref_id) 
          content_type,
          value_type,
          object_ref_id
        FROM search_index
        WHERE 1=1 
    '''
    
    params = []

    
    if query:
        
        select = ''' 
            {select}
            AND plainto_tsquery('english', %s) @@ content
        '''.format(select)
        
        params = [query]

    if filters:
        filts = ' OR '.join(["content_type = '{}'".format(f) for f in filters])
        select = ''' 
            {select}
            AND ({filts})
        '''.format(select=select, filts=filts)
    
    if location and radius and geoname_type:

        # TODO: Make this work for areas once we have them
        model, _ = GEONAME_TYPES[geoname_type]
        geoname_obj = model.objects.get(id=location).location
        select = ''' 
            {select}
            AND ST_Intersects(ST_Buffer_Meters(ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {radius}), site)
        '''.format(select=select,
                   lon=geoname_obj.x,
                   lat=geoname_obj.y,
                   radius=(int(radius) * 1000))

    select = ''' 
        {select} 
        ORDER BY content_type, object_ref_id
    '''.format(select=select)
        
    cursor = connection.cursor()
        
    cursor.execute(select, params)
    
    result_types = {}
    
    for result in cursor:
        content_type, value_type, object_ref_id = result
        
        try:
            result_types[content_type].append(object_ref_id)
        except KeyError:
            result_types[content_type] = [object_ref_id]

    for content_type, objects in result_types.items():
        model = SEARCH_CONTENT_TYPES[content_type]
        results[content_type] = model.objects.filter(id__in=objects)
    
    context = {
        'results': results, 
        'query': query, 
        'filters': filters,
    }

    return render(request, 'sfm/search.html', context)

def source_autocomplete(request):
    term = request.GET.get('q')
    sources = Source.objects.filter(title__icontains=term).all()
    
    results = []
    for source in sources:
        text = '{0} ({1} - {2})'.format(source.title,
                                        source.publication.title,
                                        source.publication.country)
        results.append({
            'text': text,
            'id': str(source.id),
        })
    
    return HttpResponse(json.dumps(results), content_type='application/json')

def publications_autocomplete(request):
    term = request.GET.get('q')
    publications = Publication.objects.filter(title__icontains=term).all()
    
    results = []
    for publication in publications:
        results.append({
            'text': publication.title,
            'country': publication.country,
            'id': str(publication.id),
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

def people_autocomplete(request):
    term = request.GET.get('q')
    people = Person.objects.filter(personname__value__icontains=term).all()
    results = []
    for person in people:
        results.append({
            'text': str(person.name),
            'id': person.id,
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def personalias_autocomplete(request):
    term = request.GET.get('q')
    alias_query = PersonAlias.objects.filter(value__value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value.value,
            'id': alias.value.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def geoname_autocomplete(request):
    term = request.GET.get('q')
    types = request.GET.getlist('types')

    if not types:
        types = request.GET.getlist('types[]', GEONAME_TYPES.keys())
    
    results = []
    for geo_type in types:
        model, field = GEONAME_TYPES[geo_type]
        
        query_kwargs = {'{}__istartswith'.format(field): term}
        
        for result in model.objects.filter(**query_kwargs):
            value = getattr(result, field)
            results.append({
                'text': '{0} ({1})'.format(value, geo_type),
                'value': value,
                'id': result.id,
                'type': geo_type,
            })

    results.sort(key=lambda x:x['text'])
    return HttpResponse(json.dumps(results),content_type='application/json')
