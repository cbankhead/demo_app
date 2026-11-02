from django import forms
from .aws_utils import AmazonPrefixTools
from .azure_utils import AzurePrefixTools
from .gcp_utils import GooglePrefixTools

'''
Build the service names and region names lists using the AmazonPrefixTools class.
Then convert the lists to tuples for use in the form fields select lists.
This gets us out of the buisness of iteration loops in the template and allows us to use the built-in Django form fields.
'''

# ChoiceField.choices accepts a callable (evaluated lazily per-request, not at
# import time) — required here since these hit slow/unreliable third-party
# endpoints (looking at you, Azure) that previously blocked every app startup
# (collectstatic/migrate/gunicorn worker boot all import this module).
def _make_choices(fetch_names, placeholder):
    names = fetch_names()
    return [("", placeholder)] + [(name, name) for name in names]


def aws_service_names_choices():
    return _make_choices(AmazonPrefixTools().build_service_names_list, "-- Select a service --")


def aws_region_names_choices():
    return _make_choices(AmazonPrefixTools().build_region_names_list, "-- Select a region --")


def azure_service_names_choices():
    return _make_choices(AzurePrefixTools().build_service_names_list, "-- Select a service --")


def azure_region_names_choices():
    return _make_choices(AzurePrefixTools().build_region_names_list, "-- Select a region --")


def gcp_service_names_choices():
    return _make_choices(GooglePrefixTools().build_service_names_list, "-- Select a service --")


def gcp_region_names_choices():
    return _make_choices(GooglePrefixTools().build_region_names_list, "-- Select a region --")


class AmazonSiteForms(forms.Form):
    '''
    This class will build form fields for this demo site.
    We use this mainly to build the select lists for itmes like service names and region names.
    '''

    aws_service_names = forms.ChoiceField(
        label='Service Name',
        choices=aws_service_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'service_select'})
    )

    aws_region_names = forms.ChoiceField(
        label='Region Name',
        choices=aws_region_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'region_select'})
    )

class AzureSiteForms(forms.Form):
    '''
    This class will build form fields for this azure related pages on this demo site.
    We use this mainly to build the select lists for itmes like service names and region names.
    '''

    azure_service_names = forms.ChoiceField(
        label='Service Name',
        choices=azure_service_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'service_select'})
    )

    azure_region_names = forms.ChoiceField(
        label='Region Name',
        choices=azure_region_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'region_select'})
    )


class GoogleSiteForms(forms.Form):
    '''
    This class will build form fields for this GCP related pages on this demo site.
    We use this mainly to build the select lists for itmes like service names and region names.
    '''

    gcp_service_names = forms.ChoiceField(
        label='Service Name',
        choices=gcp_service_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'service_select'})
    )

    gcp_region_names = forms.ChoiceField(
        label='Region Name',
        choices=gcp_region_names_choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'region_select'})
    )