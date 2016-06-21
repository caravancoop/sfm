import json
from uuid import uuid4

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import redirect
from django.contrib import messages

from extra_views import FormSetView
from reversion.models import Version

from .forms import SourceForm, OrgForm, PersonForm, PersonMembershipForm, \
    OrganizationGeographyForm
from source.models import Source, Publication
from organization.models import Organization, OrganizationName, \
    OrganizationAlias, Alias as OrganizationAliasObject, Classification
from person.models import Person, PersonName, PersonAlias
from person.models import Alias as PersonAliasObject
from membershipperson.models import MembershipPerson, Role, Rank, Context
from association.models import Association
from emplacement.models import Emplacement
from cities.models import Place, City, Country, Region, Subregion, District
from geosite.models import Geosite
from area.models import Area

class Dashboard(TemplateView):
    template_name = 'sfm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['edits'] = sorted(Version.objects.get_unique(), 
                                  key=lambda x: x.revision.date_created, 
                                  reverse=True)

        if self.request.session.get('source_id'):
            del self.request.session['source_id']
        
        return context

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

    def get_context_data(self, **kwargs):
        # Redirect to source creation page if no source in session
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding an organization, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('create-source')

        context = super(CreateOrgs, self).get_context_data(**kwargs)
        context['classifications'] = Classification.objects.all()

        context['source'] = Source.objects.get(id=self.request.session['source_id'])
        
        return context

    def post(self, request, *args, **kwargs):
        OrgFormSet = self.get_formset()
        formset = OrgFormSet(request.POST)
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)
    
    def formset_valid(self, formset):
        response = super().formset_valid(formset)
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
            
            form = {k: formset.data.getlist(k) for k in form_key_mapper}

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
           
            if name_id == 'None' or not name_id:
                return self.formset_invalid(formset)

            elif name_id == '-1':
                organization = Organization.create(org_info)      
            
            else:
                organization = Organization.objects.get(id=name_id)

            # Save aliases first
            alias_id_key = 'form-{0}-alias'.format(i)
            alias_text_key = 'form-{0}-alias_text'.format(i)
            
            aliases = formset.data.getlist(alias_text_key)
            
            form[alias_id_key] = []

            for alias in aliases:
                
                alias_obj, created = OrganizationAliasObject.objects.get_or_create(value=alias)

                alias_data = {
                    'Organization_OrganizationAlias': {
                        'value': alias_obj, 
                        'confidence': 1,
                        'sources': [source]
                    }
                }
                organization.update(alias_data)
                
                form[alias_id_key].append(alias_obj.id)
            
            # Next do classification
            classification = formset.data.get(form_prefix + 'classification')
            form[form_prefix + 'classification'] = [None]
            
            if classification:
                
                classification_obj = Classification.objects.get(id=classification)
                org_info['Organization_OrganizationClassification'] = {
                    'value': classification_obj,
                    'confidence': 1,
                    'sources': [source]
                }

                form[form_prefix + 'classification'] = [classification_obj.id]
            
            # Now do dates
            form[form_prefix + 'foundingdate'] = form[form_prefix + 'foundingdate'][0]
            realfounding = form_prefix + 'realfounding' in formset.data.keys()
            form[form_prefix + 'realfounding'] = realfounding

            # Add to dict used to update org
            org_info.update({
                'Organization_OrganizationFoundingDate': {
                    'value': form[form_prefix + 'foundingdate'],
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
 
            form[name_id_key] = organization.name.get_field().id

            self.organizations.append(organization)
            
            # rewrite keys
            form = {form_key_mapper[k]: form[k] for k in form_key_mapper}
            
            actual_form_index += 1
        
        self.request.session['organizations'] = [{'id': o.id, 'name': o.name.get_value().value} \
                                                     for o in self.organizations]
        
        return response

class CreatePeople(FormSetView):
    template_name = 'sfm/create-people.html'
    form_class = PersonForm
    success_url = '/membership-info/'
    extra = 1
    max_num = None

    def get_context_data(self, **kwargs):
        context = super(CreatePeople, self).get_context_data(**kwargs)
        
        if not self.request.session.get('source_id'):
            messages.add_message(self.request, 
                                 messages.INFO, 
                                 "Before adding people, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('create-source')
        
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

        form_data = {}
        for i in range(0,num_forms):
            first = True

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
            
            form[alias_id_key] = []

            for alias in aliases:
                
                alias_obj, created = PersonAliasObject.objects.get_or_create(value=alias)

                alias_data = {
                    'Person_PersonAlias': {
                        'value': alias_obj.value, 
                        'confidence': 1,
                        'sources': [source],
                    }
                }
                person.update(alias_data)
                
                form[alias_id_key].append(alias_obj.id)

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
           
            form[date_key] = deathdate

            self.people.append(person)
            
            try:
                del form[alias_text_key]
            except KeyError:
                pass

            form[name_id_key] = person.name.get_field().id

            form_data.update(form)

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

    def get_context_data(self, **kwargs):
        context = super(MembershipInfo, self).get_context_data(**kwargs)
        if not self.request.session.get('source_id'):
            messages.add_message(request, 
                                 messages.INFO, 
                                 "Before adding memberships, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('create-source')
        
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
    
    def get_context_data(self, **kwargs):
        context = super(OrganizationGeographies, self).get_context_data(**kwargs)
        if not self.request.session.get('source_id'):
            messages.add_message(request, 
                                 messages.INFO, 
                                 "Before adding memberships, please tell us about your source.",
                                 extra_tags='alert alert-info')
            return redirect('create-source')
        
        organizations = self.request.session['organizations']
        
        context['organizations'] = organizations
        context['source'] = Source.objects.get(id=self.request.session['source_id'])
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
        num_forms = 1 #int(formset.data['form-TOTAL_FORMS'][0])
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
                get_site = Geosite.objects.filter(geositename__value=geo.name)
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
                get_emp = Emplacement.objects.filter(emplacementorganization__value=org_id).filter(emplacementsite__value=site.id)
                if len(get_emp) > 0:
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
                    Emplacement.update(emp_data)
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
                get_area = Area.objects.filter(geoname__value = geo.name)
                if len(get_area) == 0:
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
                        'Area_AreaCode': {
                            'value': code,
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
                get_assoc = Association.objects.filter(associationorganization__value=org_id).filter(associationsite__value=site.id)
                if len(get_assoc) > 0:
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
                    Association.update(assoc_data)
                else:
                    assoc_data = {
                        'Association_AssociationOrganization': {
                            'value': Organization.objects.get(id=org_id),
                            'confidence': 1,
                            'source': [source]
                        },
                        'Association_AssociationSite': {
                            'value': site,
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
    alias_query = PersonAlias.objects.filter(value__icontains=term)
    results = []
    for alias in alias_query:
        results.append({
            'text': alias.value,
            'id': alias.id
        })
    return HttpResponse(json.dumps(results), content_type='application/json')

def geoname_autocomplete(request):
    term = request.GET.get('q')
    city_query = City.objects.filter(name_std__istartswith=term)
    results = []
    for city in city_query:
        results.append({
            'text': city.name + ' (city)',
            'value': city.name,
            'id': city.id,
            'type': 'city'
        })
    country_query = Country.objects.filter(name__istartswith=term)
    for country in country_query:
        results.append({
            'text': country.name + ' (country)',
            'value': country.name,
            'id': country.id,
            'type': 'country'
        })
    region_query = Region.objects.filter(name_std__istartswith=term)
    for region in region_query:
        results.append({
            'text': region.name + ' (region)',
            'value': region.name,
            'id': region.id,
            'type': 'region'
        })
    subregion_query = Subregion.objects.filter(name_std__istartswith=term)
    for subregion in subregion_query:
        results.append({
            'text': subregion.name + ' (subregion)',
            'value': subregion.name,
            'id': subregion.id,
            'type': 'subregion'
        })
    district_query = District.objects.filter(name_std__istartswith=term)
    for district in district_query:
        results.append({
            'text': district.name + ' (district)',
            'value': district.name,
            'id': district.id,
            'type': 'district'
        })
    results.sort(key=lambda x:x['text'])
    return HttpResponse(json.dumps(results),content_type='application/json')
