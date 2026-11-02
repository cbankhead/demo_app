from django.http import JsonResponse
from django.shortcuts import render
from .aws_utils import AmazonPrefixTools
from .azure_utils import AzurePrefixTools
from .gcp_utils import GooglePrefixTools
from .ip_address_tools import IPAddressTools
from .forms import AmazonSiteForms, AzureSiteForms, GoogleSiteForms


# Create your views here.


def home(request):
    """Render the application's home page.

    Args:
        request: The incoming HTTP request.

    Returns:
        The rendered home page response.

    Example:
        GET /home/
    """
    message = 'Hello, demo!'
    return render(request, 'demo/home.html', {'message': message})


def aws_tools(request):
    """Render AWS lookup tools with available service and region names.

    Args:
        request: The incoming HTTP request.

    Returns:
        The rendered AWS tools page.

    Example:
        GET /aws_tools/
    """
    form = AmazonSiteForms()
    aws_service_names = '<br>'.join(AmazonPrefixTools().build_service_names_list())
    aws_region_names = '<br>'.join(AmazonPrefixTools().build_region_names_list())

    return render(
        request,
        'demo/aws/aws_tools.html',
        {
            'form': form,
            'aws_service_names': aws_service_names,
            'aws_region_names': aws_region_names,
        },
    )


def aws_tools_fetch_prefixes_by_ipv4_lookup(request):
    """Return AWS service and region matches for an IPv4 address.

    Args:
        request: A GET request containing the ``ipv4_address`` query parameter.

    Returns:
        JSON containing matching AWS prefixes, or an error response.

    Example:
        GET /aws_tools/fetch_prefixes_by_ipv4_lookup/?ipv4_address=192.0.2.1
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('ipv4_address'):
        return JsonResponse(
            {'error': 'Invalid request. Missing ipv4_address parameter.'},
            status=404,
        )

    ipv4_address = request.GET.get('ipv4_address')

    if not IPAddressTools().check_if_ipv4_address(ipv4_address):
        return JsonResponse(
            {'error': 'Invalid request. Invalid IP address.'},
            status=404,
        )

    data = AmazonPrefixTools().lookup_ip_address_service_usage(ipv4_address)
    return JsonResponse({'data': data})


def aws_tools_lookup_prefixes_by_service_names(request):
    """Return AWS IPv4 prefixes for the requested service.

    Args:
        request: A GET request containing the ``service_name`` query parameter.

    Returns:
        JSON containing the service's prefixes, or an error response.

    Example:
        GET /aws_tools/lookup_prefixes_by_service_names/?service_name=AMAZON
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('service_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing service_name parameter.'},
            status=404,
        )

    service_name = request.GET.get('service_name')

    data = AmazonPrefixTools().lookup_prefixes_by_service_names(service_name)
    return JsonResponse({'data': data})


def aws_tools_lookup_prefixes_by_region_names(request):
    """Return AWS IPv4 prefixes for the requested region.

    Args:
        request: A GET request containing the ``region_name`` query parameter.

    Returns:
        JSON containing the region's prefixes, or an error response.

    Example:
        GET /aws_tools/lookup_prefixes_by_region_names/?region_name=us-east-1
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('region_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing region_name parameter.'},
            status=404,
        )

    region_name = request.GET.get('region_name')

    data = AmazonPrefixTools().lookup_prefixes_by_region_names(region_name)
    return JsonResponse({'data': data})


def azure_tools(request):
    """Render Azure lookup tools with available service and region names.

    Args:
        request: The incoming HTTP request.

    Returns:
        The rendered Azure tools page.

    Example:
        GET /azure_tools/
    """
    form = AzureSiteForms()
    azure_service_names = '<br>'.join(AzurePrefixTools().build_service_names_list())
    azure_region_names = '<br>'.join(AzurePrefixTools().build_region_names_list())
    return render(
        request,
        'demo/azure/azure_tools.html',
        {
            'form': form,
            'azure_service_names': azure_service_names,
            'azure_region_names': azure_region_names,
        },
    )


def azure_tools_fetch_prefixes_by_ipv4_lookup(request):
    """Return Azure service and region matches for an IPv4 address.

    Args:
        request: A GET request containing the ``ipv4_address`` query parameter.

    Returns:
        JSON containing matching Azure prefixes, or an error response.

    Example:
        GET /azure_tools/fetch_prefixes_by_ipv4_lookup/?ipv4_address=192.0.2.1
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('ipv4_address'):
        return JsonResponse(
            {'error': 'Invalid request. Missing ipv4_address parameter.'},
            status=404,
        )

    ipv4_address = request.GET.get('ipv4_address')

    if not IPAddressTools().check_if_ipv4_address(ipv4_address):
        return JsonResponse(
            {'error': 'Invalid request. Invalid IP address.'},
            status=404,
        )

    data = AzurePrefixTools().lookup_ip_address_service_usage(ipv4_address)
    return JsonResponse({'data': data})


def azure_tools_lookup_prefixes_by_service_names(request):
    """Return Azure IPv4 prefixes for the requested service tag.

    Args:
        request: A GET request containing the ``service_name`` query parameter.

    Returns:
        JSON containing the service tag's prefixes, or an error response.

    Example:
        GET /azure_tools/lookup_prefixes_by_service_names/?service_name=AzureCloud
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('service_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing service_name parameter.'},
            status=404,
        )

    service_name = request.GET.get('service_name')

    data = AzurePrefixTools().lookup_prefixes_by_service_names(service_name)
    return JsonResponse({'data': data})


def azure_tools_lookup_prefixes_by_region_names(request):
    """Return Azure IPv4 prefixes for the requested region.

    Args:
        request: A GET request containing the ``region_name`` query parameter.

    Returns:
        JSON containing the region's prefixes, or an error response.

    Example:
        GET /azure_tools/lookup_prefixes_by_region_names/?region_name=eastus
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('region_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing region_name parameter.'},
            status=404,
        )

    region_name = request.GET.get('region_name')

    data = AzurePrefixTools().lookup_prefixes_by_region_names(region_name)
    return JsonResponse({'data': data})


def gcp_tools(request):
    """Render GCP lookup tools with available service and region names.

    Args:
        request: The incoming HTTP request.

    Returns:
        The rendered GCP tools page.

    Example:
        GET /gcp_tools/
    """
    form = GoogleSiteForms()
    gcp_service_names = '<br>'.join(GooglePrefixTools().build_service_names_list())
    gcp_region_names = '<br>'.join(GooglePrefixTools().build_region_names_list())
    return render(
        request,
        'demo/gcp/gcp_tools.html',
        {
            'form': form,
            'gcp_service_names': gcp_service_names,
            'gcp_region_names': gcp_region_names,
        },
    )


def gcp_tools_fetch_prefixes_by_ipv4_lookup(request):
    """Return GCP service and region matches for an IPv4 address.

    Args:
        request: A GET request containing the ``ipv4_address`` query parameter.

    Returns:
        JSON containing matching GCP prefixes, or an error response.

    Example:
        GET /gcp_tools/fetch_prefixes_by_ipv4_lookup/?ipv4_address=192.0.2.1
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('ipv4_address'):
        return JsonResponse(
            {'error': 'Invalid request. Missing ipv4_address parameter.'},
            status=404,
        )

    ipv4_address = request.GET.get('ipv4_address')

    if not IPAddressTools().check_if_ipv4_address(ipv4_address):
        return JsonResponse(
            {'error': 'Invalid request. Invalid IP address.'},
            status=404,
        )

    data = GooglePrefixTools().lookup_ip_address_service_usage(ipv4_address)
    return JsonResponse({'data': data})


def gcp_tools_lookup_prefixes_by_service_names(request):
    """Return GCP IPv4 prefixes for the requested service.

    Args:
        request: A GET request containing the ``service_name`` query parameter.

    Returns:
        JSON containing the service's prefixes, or an error response.

    Example:
        GET /gcp_tools/lookup_prefixes_by_service_names/?service_name=Google%20Cloud
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('service_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing service_name parameter.'},
            status=404,
        )

    service_name = request.GET.get('service_name')

    data = GooglePrefixTools().lookup_prefixes_by_service_names(service_name)
    return JsonResponse({'data': data})


def gcp_tools_lookup_prefixes_by_region_names(request):
    """Return GCP IPv4 prefixes for the requested region.

    Args:
        request: A GET request containing the ``region_name`` query parameter.

    Returns:
        JSON containing the region's prefixes, or an error response.

    Example:
        GET /gcp_tools/lookup_prefixes_by_region_names/?region_name=us-central1
    """
    if request.method != 'GET':
        return JsonResponse(
            {'error': 'Invalid request method. Only GET requests are allowed.'},
            status=405,
        )
    if not request.GET.get('region_name'):
        return JsonResponse(
            {'error': 'Invalid request. Missing region_name parameter.'},
            status=404,
        )

    region_name = request.GET.get('region_name')

    data = GooglePrefixTools().lookup_prefixes_by_region_names(region_name)
    return JsonResponse({'data': data})

def cidr_calculator(request):
    """Render the CIDR form or return network details for a POST submission.

    Args:
        request: A GET request to display the form, or a POST request with
            ``ipv4_input`` and ``cidr_input`` form fields.

    Returns:
        The calculator page for GET requests, or JSON with calculation results
        or a validation error for POST requests.

    Example:
        POST /cidr_calculator/ with ipv4_input=192.0.2.10 and cidr_input=24
    """
    if request.method == 'POST':
        ipv4_address = request.POST.get('ipv4_input')
        cidr_prefix = request.POST.get('cidr_input')

        if not ipv4_address or not cidr_prefix:
            return JsonResponse(
                {
                    'error': (
                        'Invalid request. Missing ipv4_address or '
                        'cidr_prefix parameter.'
                    ),
                },
                status=404,
            )

        try:
            cidr_prefix = int(cidr_prefix)
        except ValueError:
            return JsonResponse(
                {'error': 'Invalid request. CIDR prefix must be an integer.'},
                status=404,
            )

        try:
            data = IPAddressTools().get_network_information_from_ipv4_address(
                ipv4_address,
                cidr_prefix,
            )
            return JsonResponse({'data': data})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=404)

    return render(request, 'demo/cidr_calculator/cidr_calculator.html')