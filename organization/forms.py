from django import forms

from django.conf import settings
from django_date_extensions.fields import ApproximateDateFormField
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from sfm_pc.forms import BaseEditForm, GetOrCreateChoiceField, BasePostingsForm

from membershipperson.models import MembershipPersonMember
from person.models import Person

from emplacement.models import Emplacement, EmplacementStartDate, \
    EmplacementEndDate, EmplacementRealStart, EmplacementOpenEnded, \
    EmplacementOrganization, EmplacementSite, EmplacementAlias

from geosite.models import Geosite

from area.models import Area

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


class OrganizationBasicsForm(BaseEditForm):
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

    name = forms.CharField()
    division_id = forms.CharField(required=False)
    firstciteddate = ApproximateDateFormField(required=False)
    lastciteddate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField()
    open_ended = forms.ChoiceField(choices=OPEN_ENDED_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=OrganizationAlias.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=self.object_ref_pk,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases')
        self.fields['classification'] = GetOrCreateChoiceField(queryset=OrganizationClassification.objects.filter(object_ref__uuid=self.object_ref_pk),
                                                               required=False,
                                                               object_ref_pk=self.object_ref_pk,
                                                               object_ref_model=self._meta.model,
                                                               form=self,
                                                               field_name='classification')


class OrganizationRelationshipsForm(BaseEditForm):
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

    realstart = forms.BooleanField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(choices=OPEN_ENDED_CHOICES, required=False)
    parent = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    child = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    classification = forms.CharField(required=False)

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


class OrganizationPersonnelForm(BasePostingsForm):
    edit_fields = BasePostingsForm.edit_fields + [('person', MembershipPersonMember, False)]

    person = forms.ModelChoiceField(queryset=Person.objects.all())


class OrganizationEmplacementForm(BaseEditForm):
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
    ]

    realstart = forms.BooleanField()
    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(choices=OPEN_ENDED_CHOICES, required=False)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    site = forms.ModelChoiceField(queryset=Geosite.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['aliases'] = GetOrCreateChoiceField(queryset=EmplacementAlias.objects.filter(object_ref__id=self.object_ref_pk),
                                                        required=False,
                                                        object_ref_pk=self.object_ref_pk,
                                                        object_ref_model=self._meta.model,
                                                        form=self,
                                                        field_name='aliases')


class OrganizationAssociationForm(BaseEditForm):
    class Meta:
        model = Association
        fields = '__all__'

    edit_fields = [
        ('startdate', AssociationStartDate, False),
        ('enddate', AssociationEndDate, False),
        ('realstart', AssociationRealStart, False),
        ('organization', AssociationOrganization, False),
        ('area', AssociationArea, False),
        ('open_ended', AssociationOpenEnded, False),
    ]

    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(choices=OPEN_ENDED_CHOICES, required=False)
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False)
