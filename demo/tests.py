from unittest.mock import Mock, patch

from django.test import TestCase

from .aws_utils.aws_utils import AmazonPrefixTools
from .azure_utils.azure_utils import AzurePrefixTools
from .gcp_utils.gcp_utils import GooglePrefixTools
from .ip_address_tools.ip_address_tools import IPAddressTools
from .models import PrefixDataCache


class ProviderJsonCacheTests(TestCase):
	def setUp(self):
		"""Clear cached provider data so each test starts independently."""
		PrefixDataCache.objects.all().delete()

	def test_aws_json_is_shared_between_instances(self):
		"""Verify AWS data is fetched once and reused from the database cache.

		Example: two AWS helper instances return the same mocked payload while
		making only one request to the AWS endpoint.
		"""
		payload = {'prefixes': [{'ip_prefix': '192.0.2.0/24'}]}
		response = Mock(status_code=200)
		response.json.return_value = payload

		with patch('demo.aws_utils.aws_utils.requests.get', return_value=response) as request:
			self.assertEqual(AmazonPrefixTools().get_json_data(), payload)
			self.assertEqual(AmazonPrefixTools().get_json_data(), payload)

		request.assert_called_once()
		self.assertEqual(
			list(PrefixDataCache.objects.values_list('cache_key', flat=True)),
			['aws_prefix_data'],
		)

	def test_gcp_json_is_shared_between_instances(self):
		"""Verify GCP data is fetched once and reused from the database cache.

		Example: two GCP helper instances return the same mocked payload while
		making only one request to the Google Cloud endpoint.
		"""
		payload = {'prefixes': [{'ipv4Prefix': '192.0.2.0/24'}]}
		response = Mock(status_code=200)
		response.json.return_value = payload

		with patch('demo.gcp_utils.gcp_utils.requests.get', return_value=response) as request:
			self.assertEqual(GooglePrefixTools().get_json_data(), payload)
			self.assertEqual(GooglePrefixTools().get_json_data(), payload)

		request.assert_called_once()
		self.assertEqual(
			list(PrefixDataCache.objects.values_list('cache_key', flat=True)),
			['gcp_prefix_data'],
		)

	def test_azure_json_is_shared_between_instances(self):
		"""Verify Azure page and JSON requests happen only on the first lookup.

		Example: two helper instances share one cached payload after one request
		for the download page and one request for its JSON file.
		"""
		payload = {'values': [{'name': 'AzureCloud'}]}
		static_response = Mock(
			status_code=200,
			text='https://download.microsoft.com/path/ServiceTags_Public_20261031.json',
		)
		download_response = Mock(status_code=200)
		download_response.json.return_value = payload

		with patch(
			'demo.azure_utils.azure_utils.requests.get',
			side_effect=[static_response, download_response],
		) as request:
			self.assertEqual(AzurePrefixTools().get_json_data(), payload)
			self.assertEqual(AzurePrefixTools().get_json_data(), payload)

		self.assertEqual(request.call_count, 2)
		self.assertEqual(
			list(PrefixDataCache.objects.values_list('cache_key', flat=True)),
			['azure_prefix_data'],
		)


class ProviderLookupTests(TestCase):
	def test_aws_filters_by_service_and_region(self):
		"""Verify AWS names and service lookup use the matching records.

		Example: looking up EC2 returns its prefix, not the S3 prefix.
		"""
		tools = AmazonPrefixTools()
		tools.json_data = {
			'prefixes': [
				{'service': 'EC2', 'region': 'us-east-1', 'ip_prefix': '192.0.2.0/24'},
				{'service': 'S3', 'region': 'us-west-1', 'ip_prefix': '198.51.100.0/24'},
			]
		}

		self.assertEqual(tools.build_service_names_list(), ['EC2', 'S3'])
		self.assertEqual(tools.build_region_names_list(), ['us-east-1', 'us-west-1'])
		self.assertEqual(
			tools.lookup_prefixes_by_service_names('EC2'),
			['192.0.2.0/24'],
		)

	def test_gcp_filters_by_service_and_region(self):
		"""Verify GCP names and region lookup use the matching records.

		Example: looking up us-central1 returns its prefix, not europe-west1's.
		"""
		tools = GooglePrefixTools()
		tools.json_data = {
			'prefixes': [
				{'service': 'Google Cloud', 'scope': 'us-central1', 'ipv4Prefix': '192.0.2.0/24'},
				{'service': 'Google Cloud', 'scope': 'europe-west1', 'ipv4Prefix': '198.51.100.0/24'},
			]
		}

		self.assertEqual(tools.build_service_names_list(), ['Google Cloud'])
		self.assertEqual(tools.build_region_names_list(), ['europe-west1', 'us-central1'])
		self.assertEqual(
			tools.lookup_prefixes_by_region_names('us-central1'),
			['192.0.2.0/24'],
		)

	def test_azure_returns_only_ipv4_prefixes(self):
		"""Verify Azure lookup excludes IPv6 and returns the IPv4 prefix.

		Example: a service tag with IPv4 and IPv6 entries returns only IPv4.
		"""
		tools = AzurePrefixTools()
		tools.json_data = {
			'values': [
				{
					'name': 'AzureCloud',
					'properties': {
						'region': 'eastus',
						'addressPrefixes': ['192.0.2.0/24', '2001:db8::/32'],
					},
				}
			]
		}

		self.assertEqual(tools.build_service_names_list(), ['AzureCloud'])
		self.assertEqual(tools.build_region_names_list(), ['eastus'])
		self.assertEqual(
			tools.lookup_prefixes_by_service_names('AzureCloud'),
			['192.0.2.0/24'],
		)


class CidrCalculatorTests(TestCase):
	def setUp(self):
		"""Create a fresh IP address helper before each test."""
		self.address_tools = IPAddressTools()

	def test_calculates_network_details_for_a_slash_24(self):
		"""Check that a /24 input produces the expected network details.

		Example: 192.0.2.10/24 belongs to 192.0.2.0/24, with usable hosts
		from 192.0.2.1 through 192.0.2.254.
		"""
		# Arrange: use an address and prefix with known network boundaries.
		ipv4_address = '192.0.2.10'
		cidr_prefix = 24

		# Act: ask the helper to calculate the network details.
		network_details = self.address_tools.get_network_information_from_ipv4_address(
			ipv4_address,
			cidr_prefix,
		)

		# Assert: verify the values a user relies on in the calculator.
		self.assertEqual(network_details['network_address'], '192.0.2.0')
		self.assertEqual(network_details['broadcast_address'], '192.0.2.255')
		self.assertEqual(network_details['netmask'], '255.255.255.0')
		self.assertEqual(network_details['prefix_length'], 24)
		self.assertEqual(network_details['num_addresses'], 256)
		self.assertEqual(network_details['hosts'], '192.0.2.1 - 192.0.2.254')

	def test_rejects_an_invalid_ipv4_address(self):
		"""Check that malformed IPv4 input raises a clear validation error.

		Example: "not-an-ip-address" with prefix 24 raises ValueError.
		"""
		with self.assertRaisesMessage(ValueError, 'Invalid IPv4 address'):
			self.address_tools.get_network_information_from_ipv4_address(
				'not-an-ip-address',
				24,
			)

	def test_rejects_an_ipv6_address(self):
		"""Check that IPv6 input is not accepted by the IPv4 validator.

		Example: 2001:db8::1 is an IPv6 address, so validation returns False.
		"""
		self.assertFalse(self.address_tools.check_if_ipv4_address('2001:db8::1'))

	def test_cidr_calculator_rejects_an_ipv6_address(self):
		"""Check that the IPv4 calculator raises an error for IPv6 input.

		Example: calculating 2001:db8::1/24 raises an invalid IPv4 error.
		"""
		with self.assertRaisesMessage(ValueError, 'Invalid IPv4 address'):
			self.address_tools.get_network_information_from_ipv4_address(
				'2001:db8::1',
				24,
			)

	def test_rejects_a_cidr_prefix_greater_than_32(self):
		"""Check that a prefix above the IPv4 maximum raises ValueError.

		Example: prefix 33 is invalid for IPv4.
		"""
		with self.assertRaisesMessage(ValueError, 'Invalid CIDR prefix'):
			self.address_tools.get_network_information_from_ipv4_address(
				'192.0.2.10',
				33,
			)

	def test_calculates_slash_zero_host_range_without_enumerating_hosts(self):
		"""Calculate a /0 host range without iterating billions of addresses.

		Example: the usable host range for 0.0.0.0/0 is 0.0.0.1 through
		255.255.255.254.
		"""
		with patch(
			'demo.ip_address_tools.ip_address_tools.ipaddress.IPv4Network.hosts',
			side_effect=AssertionError('The calculator must not enumerate hosts.'),
		):
			network_details = self.address_tools.get_network_information_from_ipv4_address(
				'192.0.2.10',
				0,
			)

		self.assertEqual(network_details['network_address'], '0.0.0.0')
		self.assertEqual(network_details['broadcast_address'], '255.255.255.255')
		self.assertEqual(network_details['num_addresses'], 4294967296)
		self.assertEqual(network_details['hosts'], '0.0.0.1 - 255.255.255.254')

	def test_includes_both_addresses_in_a_slash_31_host_range(self):
		"""Treat both /31 addresses as hosts, per point-to-point IPv4 rules.

		Example: 192.0.2.10/31 has the host range 192.0.2.10 through
		192.0.2.11.
		"""
		network_details = self.address_tools.get_network_information_from_ipv4_address(
			'192.0.2.10',
			31,
		)

		self.assertEqual(network_details['hosts'], '192.0.2.10 - 192.0.2.11')

	def test_slash_32_host_range_contains_only_the_input_address(self):
		"""Treat the single address in a /32 as its complete host range.

		Example: 192.0.2.10/32 has the host range 192.0.2.10 through itself.
		"""
		network_details = self.address_tools.get_network_information_from_ipv4_address(
			'192.0.2.10',
			32,
		)

		self.assertEqual(network_details['hosts'], '192.0.2.10 - 192.0.2.10')

	def test_post_returns_calculated_network_details(self):
		"""Check that a valid form POST returns network details as JSON.

		Example: posting 192.0.2.10 and prefix 24 returns network 192.0.2.0.
		"""
		response = self.client.post(
			'/cidr_calculator/',
			{'ipv4_input': '192.0.2.10', 'cidr_input': '24'},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response.json()['data']['network_address'],
			'192.0.2.0',
		)

	def test_post_returns_an_error_for_a_non_integer_prefix(self):
		"""Check that a non-integer form prefix returns a JSON error.

		Example: posting "abc" as the CIDR prefix returns an error response.
		"""
		response = self.client.post(
			'/cidr_calculator/',
			{'ipv4_input': '192.0.2.10', 'cidr_input': 'abc'},
		)

		self.assertEqual(response.status_code, 404)
		self.assertEqual(
			response.json()['error'],
			'Invalid request. CIDR prefix must be an integer.',
		)
