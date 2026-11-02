from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),

    path('aws_tools/', views.aws_tools, name='aws_tools'),
    path('aws_tools/fetch_prefixes_by_ipv4_lookup/', views.aws_tools_fetch_prefixes_by_ipv4_lookup, name='aws_tools_fetch_prefixes_by_ipv4_lookup'),
    path('aws_tools/lookup_prefixes_by_service_names/', views.aws_tools_lookup_prefixes_by_service_names, name='aws_tools_lookup_prefixes_by_service_names'),
    path('aws_tools/lookup_prefixes_by_region_names/', views.aws_tools_lookup_prefixes_by_region_names, name='aws_tools_lookup_prefixes_by_region_names'),

    path('azure_tools/', views.azure_tools, name='azure_tools'),
    path('azure_tools/fetch_prefixes_by_ipv4_lookup/', views.azure_tools_fetch_prefixes_by_ipv4_lookup, name='azure_tools_fetch_prefixes_by_ipv4_lookup'),
    path('azure_tools/lookup_prefixes_by_service_names/', views.azure_tools_lookup_prefixes_by_service_names, name='azure_tools_lookup_prefixes_by_service_names'),
    path('azure_tools/lookup_prefixes_by_region_names/', views.azure_tools_lookup_prefixes_by_region_names, name='azure_tools_lookup_prefixes_by_region_names'),

    path('gcp_tools/', views.gcp_tools, name='gcp_tools'),
    path('gcp_tools/fetch_prefixes_by_ipv4_lookup/', views.gcp_tools_fetch_prefixes_by_ipv4_lookup, name='gcp_tools_fetch_prefixes_by_ipv4_lookup'),
    path('gcp_tools/lookup_prefixes_by_service_names/', views.gcp_tools_lookup_prefixes_by_service_names, name='gcp_tools_lookup_prefixes_by_service_names'),
    path('gcp_tools/lookup_prefixes_by_region_names/', views.gcp_tools_lookup_prefixes_by_region_names, name='gcp_tools_lookup_prefixes_by_region_names'),

    path('cidr_calculator/', views.cidr_calculator, name='cidr_calculator'),
]
