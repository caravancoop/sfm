from django import forms
from django.forms import BaseFormSet
from django.conf import settings

from django_date_extensions.fields import ApproximateDateFormField

from composition.models import Classification
from organization.models import Organization


class CompositionForm(forms.Form):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    related_organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    related_org_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    relationship_type = forms.ChoiceField(choices=(('parent', 'Parent',), ('child', 'Child',)))
    relationship_type_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    classification = forms.ModelChoiceField(queryset=Classification.objects.all())
    classification_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)

    startdate = ApproximateDateFormField(required=False)
    enddate = ApproximateDateFormField(required=False)
    date_confidence = forms.ChoiceField(choices=settings.CONFIDENCE_LEVELS)


class BaseCompositionFormSet(BaseFormSet):

    def clean(self):
        '''
        Custom form validation to check for recursive command hierarchies.
        '''
        # Don't bother doing any validation if there are outstanding errors
        if any(self.errors):
            return

        try:
            assert not self.is_recursive()
        except AssertionError:
            msg = ('It looks like your command hierarchy is recursive. Double-' +
                   'check to make sure unit command flows in one direction.')
            raise forms.ValidationError(msg)

    def is_recursive(self):
        '''
        Make sure that parent-child relationships are nonrecursive (i.e. assert
        that command flows in one direction).
        '''
        decision = False

        # Produce an edgelist representing the command hierarchy, and a list
        # of parent organizations
        edgelist, parents = [], []
        for form in self.forms:

            organization_id = form.cleaned_data['organization']
            related_organization_id = form.cleaned_data['related_organization']
            rel_type = form.cleaned_data['relationship_type']

            if rel_type == 'child':
                parents.append(related_organization_id)
                edge = {'parent': related_organization_id, 'child': organization_id}

            elif rel_type == 'parent':
                parents.append(organization_id)
                edge = {'parent': organization_id, 'child': related_organization_id}

            else:
                msg = ('Unknown relationship type: %s' % str(rel_type))
                raise forms.ValidationError(msg)

            edgelist.append(edge)

        # For each parent unit in the edgelist, recurse its command hierarchy
        # and check whether the given unit reappears
        for parent in parents:

            clean_hierarchy = self.check_hierarchy(parent, parent, edgelist)

            if not clean_hierarchy:
                decision = True
                break

        return decision

    def check_hierarchy(self, ancestor, parent, edgelist):
        '''
        Recurse an edgelist to check whether an "ancestor" appears more than
        once.
        '''
        children = list(edge['child'] for edge in edgelist if edge['parent'] == parent)

        if len(children) > 0:
            for child in children:
                # If the "ancestor" unit appears somewhere in its own hierarchy,
                # the command chain must be recursive
                if child == ancestor:
                    return False

            return self.check_hierarchy(ancestor, child, edgelist)

        else:
            return True
