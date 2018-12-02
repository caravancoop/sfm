from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseUpdateForm, BaseCreateForm, GetOrCreateChoiceField

from membershipperson.models import MembershipPersonMember
from person.models import Person

from emplacement.models import Emplacement, EmplacementStartDate, \
    EmplacementEndDate, EmplacementRealStart, EmplacementOpenEnded, \
    EmplacementOrganization, EmplacementSite, EmplacementAlias

from location.models import Location

from membershipperson.models import \
    MembershipPerson, MembershipPersonRank, MembershipPersonRole, \
    MembershipPersonTitle, MembershipPersonFirstCitedDate, \
    MembershipPersonLastCitedDate, MembershipPersonRealStart, \
    MembershipPersonRealEnd, MembershipPersonStartContext, \
    MembershipPersonEndContext, Rank, Role, MembershipPersonOrganization, \
    MembershipPersonMember

from composition.models import Composition, CompositionParent, \
    CompositionChild, CompositionRealStart, CompositionStartDate, \
    CompositionEndDate, CompositionOpenEnded, CompositionClassification

from association.models import Association, AssociationStartDate, \
    AssociationRealStart, AssociationEndDate, AssociationOpenEnded, \
    AssociationArea, AssociationOrganization

from .models import Organization, OrganizationName, OrganizationAlias, \
    OrganizationClassification, OrganizationDivisionId, OrganizationHeadquarters, \
    OrganizationFirstCitedDate, OrganizationLastCitedDate, OrganizationRealStart, \
    OrganizationOpenEnded


OPEN_ENDED_CHOICES = [
    ('Y', _('Yes')),
    ('N', _('No')),
    ('E', _('Last cited date is termination date')),
]


class OrganizationBasicsForm(BaseUpdateForm):
    class Meta:
        model = Organization
        fields = '__all__'

    edit_fields = [
        ('name', OrganizationName, False),
        ('aliases', OrganizationAlias, True),
        ('classification', OrganizationClassification, True),
        ('division_id', OrganizationDivisionId, False),
        ('firstciteddate', OrganizationFirstCitedDate, False),
        ('lastciteddate', OrganizationLastCitedDate, False),
        ('realstart', OrganizationRealStart, False),
        ('open_ended', OrganizationOpenEnded, False),
    ]

    name = forms.CharField(label=_("Name"))
    division_id = forms.CharField(label=_("Country"), required=False)
    firstciteddate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    lastciteddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    realstart = forms.BooleanField(label=_("Start date?"))
    open_ended = forms.ChoiceField(label=_("Open-ended?"), choices=OPEN_ENDED_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id', None)

        super().__init__(*args, **kwargs)

        self.fields['aliases'] = GetOrCreateChoiceField(label=_("Other names"),
                                                        queryset=OrganizationAlias.objects.filter(object_ref__uuid=organization_id),
                                                        required=False,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases',
                                                        object_ref_pk=organization_id)
        self.fields['classification'] = GetOrCreateChoiceField(label=_("Classification"),
                                                               queryset=OrganizationClassification.objects.filter(object_ref__uuid=organization_id),
                                                               required=False,
                                                               object_ref_model=self._meta.model,
                                                               form=self,
                                                               field_name='classification',
                                                               object_ref_pk=organization_id)


class OrganizationCreateBasicsForm(BaseCreateForm, OrganizationBasicsForm):
    pass


class OrganizationCompositionForm(BaseUpdateForm):
    class Meta:
        model = Composition
        fields = '__all__'

    edit_fields = [
        ('parent', CompositionParent, False),
        ('child', CompositionChild, False),
        ('realstart', CompositionRealStart, False),
        ('startdate', CompositionStartDate, False),
        ('enddate', CompositionEndDate, False),
        ('open_ended', CompositionOpenEnded, False),
        ('classification', CompositionClassification, False),
    ]

    realstart = forms.BooleanField(label=_("Start date?"))
    startdate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    enddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    open_ended = forms.ChoiceField(label=_("Open-ended?"), choices=OPEN_ENDED_CHOICES, required=False)
    parent = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    child = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    classification = forms.CharField(label=_("Relationship classification"), required=False)

    def clean(self):

        if self.errors.get('parent') and self.post_data.get('child_source'):
            self.post_data['parent_source'] = self.post_data['child_source']
            self.cleaned_data['parent'] = Organization.objects.get(id=self.post_data['parent'][0])
            del self.errors['parent']

        if self.errors.get('child') and self.post_data.get('parent_source'):
            self.post_data['child_source'] = self.post_data['parent_source']
            self.cleaned_data['child'] = Organization.objects.get(id=self.post_data['child'][0])
            del self.errors['child']

        super().clean()


class OrganizationCreateCompositionForm(BaseCreateForm, OrganizationCompositionForm):
    pass


class OrganizationPersonnelForm(BaseUpdateForm):
    edit_fields = [
        ('rank', MembershipPersonRank, False),
        ('role', MembershipPersonRole, False),
        ('title', MembershipPersonTitle, False),
        ('firstciteddate', MembershipPersonFirstCitedDate, False),
        ('lastciteddate', MembershipPersonLastCitedDate, False),
        ('realstart', MembershipPersonRealStart, False),
        ('realend', MembershipPersonRealEnd, False),
        ('startcontext', MembershipPersonStartContext, False),
        ('endcontext', MembershipPersonEndContext, False),
        ('member', MembershipPersonMember, False),
        ('organization', MembershipPersonOrganization, False),
    ]

    clone_sources = {
        'organization': 'member',
    }

    member = forms.ModelChoiceField(label=_("Person name"), queryset=Person.objects.all())
    rank = forms.ModelChoiceField(label=_("Rank"), queryset=Rank.objects.distinct('value'), required=False)
    role = forms.ModelChoiceField(label=_("Role"), queryset=Role.objects.distinct('value'), required=False)
    title = forms.CharField(label=_("Title"), required=False)
    firstciteddate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    lastciteddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    realstart = forms.BooleanField(label=_("Start date?"))
    realend = forms.BooleanField(label=_("End date?"))
    startcontext = forms.CharField(label=_("Context for start date"), required=False)
    endcontext = forms.CharField(label=_("Context for end date"), required=False)

    def __init__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id')

        super().__init__(*args, **kwargs)

        self.fields['organization'] = forms.ModelChoiceField(queryset=Organization.objects.filter(uuid=organization_id))

    class Meta:
        model = MembershipPerson
        fields = '__all__'


class OrganizationCreatePersonnelForm(BaseCreateForm, OrganizationPersonnelForm):
    pass


class OrganizationEmplacementForm(BaseUpdateForm):
    class Meta:
        model = Emplacement
        fields = '__all__'

    edit_fields = [
        ('startdate', EmplacementStartDate, False),
        ('enddate', EmplacementEndDate, False),
        ('realstart', EmplacementRealStart, False),
        ('organization', EmplacementOrganization, False),
        ('site', EmplacementSite, False),
        ('open_ended', EmplacementOpenEnded, False),
        ('aliases', EmplacementAlias, True),
        ('organization', EmplacementOrganization, False),
    ]

    clone_sources = {
        'organization': 'site',
    }

    realstart = forms.BooleanField(label=_("Start date?"))
    startdate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    enddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    open_ended = forms.ChoiceField(label=_("Open-ended?"), choices=OPEN_ENDED_CHOICES, required=False)
    organization = forms.ModelChoiceField(label=_("Organization"), queryset=Organization.objects.all(), required=False)
    site = forms.ModelChoiceField(label=_("Location name"), queryset=Location.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id')
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(label=_("Location other names"),
                                                        queryset=EmplacementAlias.objects.all(),
                                                        required=False,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases',
                                                        object_ref_pk=organization_id)


class OrganizationCreateEmplacementForm(BaseCreateForm, OrganizationEmplacementForm):
    pass


class OrganizationAssociationForm(BaseUpdateForm):
    class Meta:
        model = Association
        fields = '__all__'

    edit_fields = [
        ('realstart', AssociationRealStart, False),
        ('startdate', AssociationStartDate, False),
        ('enddate', AssociationEndDate, False),
        ('realstart', AssociationRealStart, False),
        ('organization', AssociationOrganization, False),
        ('area', AssociationArea, False),
        ('open_ended', AssociationOpenEnded, False),
    ]

    clone_sources = {
        'organization': 'area'
    }

    realstart = forms.BooleanField(label=_("Start date?"))
    startdate = ApproximateDateFormField(label=_("Date first cited"), required=False)
    enddate = ApproximateDateFormField(label=_("Date last cited"), required=False)
    open_ended = forms.ChoiceField(label=_("Open-ended?"), choices=OPEN_ENDED_CHOICES, required=False)
    organization = forms.ModelChoiceField(label=_("Organization"), queryset=Organization.objects.all(), required=False)
    area = forms.ModelChoiceField(label=_("Location name"), queryset=Location.objects.all(), required=False)


class OrganizationCreateAssociationForm(BaseCreateForm, OrganizationAssociationForm):
    pass
