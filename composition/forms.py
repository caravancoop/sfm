import datetime

from django import forms
from django.forms import BaseFormSet
from django.conf import settings
from django.utils.translation import ugettext as _

from django_date_extensions.fields import ApproximateDateFormField

from organization.models import Organization
from sfm_pc.utils import get_command_edges

class CompositionForm(forms.Form):
    parent = forms.CharField()
    parent_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    child = forms.CharField()
    child_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    classification_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    startdate = ApproximateDateFormField(required=False)
    realstart = forms.BooleanField(required=False)
    startdate_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    enddate = ApproximateDateFormField(required=False)
    open_ended = forms.ChoiceField(choices=settings.OPEN_ENDED_CHOICES)
    enddate_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)


class BaseCompositionFormSet(BaseFormSet):

    def clean(self):

        for form in self.forms:
            # Check end date/open-ended pair
            open_ended = form.cleaned_data.get('open_ended')
            if open_ended == 'E':

                try:
                    # An end date must exist if the value of open_ended is "exact"
                    assert form.cleaned_data.get('enddate')
                except AssertionError:
                    msg = _('If the value of open-ended is "Exact", an end date is required.')
                    form.add_error('enddate', msg)

            # Check for parent/child fields that refer to the same org
            parent = form.cleaned_data.get('parent')
            child = form.cleaned_data.get('child')

            try:
                assert parent != child
            except AssertionError:
                msg = _('Parent and Child fields must refer to different units.')
                for field in ('parent', 'child'):
                    form.add_error(field, msg)

        # Since the next check can be pretty expensive, don't bother doing any
        # further validation if there are outstanding errors
        if any(self.errors):
            return

        # Check for recursive command structures
        try:
            assert not self.is_recursive()
        except AssertionError:
            msg = _('It looks like your command hierarchy is recursive. Double-' +
                   'check to make sure unit command flows in one direction.')
            raise forms.ValidationError(msg)


    def is_recursive(self):
        '''
        Make sure that parent-child relationships are nonrecursive (i.e. assert
        that command flows in one direction).
        '''
        decision = False

        # Produce an edgelist representing the command hierarchy, and a set
        # of all units labelled in the form
        edgelist, orgs = [], set()
        for form in self.forms:

            parent_id = form.cleaned_data['parent']
            parent = Organization.objects.get(id=parent_id)
            parent_uuid = str(parent.uuid)

            child_id = form.cleaned_data['child']
            child = Organization.objects.get(id=child_id)
            child_uuid = str(child.uuid)

            orgs.update((parent_uuid, child_uuid))
            edgelist.append({'from': parent_uuid, 'to': child_uuid})

            # If we already have compositions on file for these units, add those
            # relationships to the edgelist
            when = str(datetime.date.today())
            if form.cleaned_data.get('enddate'):
                open_ended = form.cleaned_data.get('open_ended')
                if not open_ended == 'Y':
                    when = form.cleaned_data['enddate']

            for org_id in (parent_uuid, child_uuid):
                parent_edgelist = get_command_edges(org_id, when=when, parents=True)
                child_edgelist = get_command_edges(org_id, when=when, parents=False)

                for lst in (parent_edgelist, child_edgelist):
                    edgelist.extend(lst)

        # For each unit in the form, recurse its command hierarchy
        # and check whether the given unit reappears
        for org in orgs:

            clean_hierarchy = self.check_hierarchy(org, org, edgelist)

            if not clean_hierarchy:
                decision = True
                break

        return decision

    def check_hierarchy(self, ancestor, parent, edgelist):
        '''
        Recurse an edgelist to check whether an "ancestor" appears more than
        once.
        '''
        children = list(edge['to'] for edge in edgelist if edge['from'] == parent)

        if len(children) > 0:
            for child in children:
                # If the "ancestor" unit appears somewhere in its own hierarchy,
                # the command chain must be recursive
                if child == ancestor:
                    return False

            return self.check_hierarchy(ancestor, child, edgelist)

        else:
            return True
