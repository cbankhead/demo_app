import ipaddress
import logging
from http import HTTPStatus
from operator import itemgetter

import requests

from ..cache_utils import get_or_fetch
from ..ip_address_tools.ip_address_tools import IPAddressTools


logger = logging.getLogger(__name__)


class AmazonPrefixTools:
    """Download and search the IP address ranges published by AWS.

    Example:
        tools = AmazonPrefixTools()
        service_names = tools.build_service_names_list()
    """

    def __init__(self):
        """Set the AWS endpoint and mark its JSON as not loaded.

        Returns:
            Nothing.

        Example:
            tools = AmazonPrefixTools()
        """
        # This URL returns the raw AWS IP range JSON.
        self.json_url: str = "https://ip-ranges.amazonaws.com/ip-ranges.json"

        # This holds the full JSON response, or None before it is loaded.
        self.json_data = None

    def get_json_data(self):
        """Return the AWS JSON, loading it from the shared cache when possible.

        Returns:
            The full AWS JSON response, or None if it could not be loaded.

        Example:
            json_data = tools.get_json_data()
        """
        if self.json_data is None:
            self.json_data = get_or_fetch(
                "aws_prefix_data",
                self._fetch_json_data,
            )

        return self.json_data

    def _fetch_json_data(self):
        """Download the AWS JSON response from its endpoint.

        Returns:
            The full JSON response, or None if the request failed.

        Example:
            json_data = tools._fetch_json_data()
        """
        try:
            response = requests.get(
                self.json_url,
                timeout=10,
                headers={"User-Agent": "Demo App"},
            )
        except requests.RequestException:
            logger.exception("Could not download AWS IP range JSON.")
            return None

        if response.status_code != HTTPStatus.OK:
            logger.warning(
                "AWS IP range endpoint returned status %s.",
                response.status_code,
            )
            return None

        return response.json()

    def _get_prefixes(self):
        """Return AWS prefix records, or an empty list if loading failed.

        Returns:
            A list of AWS prefix records.

        Example:
            prefixes = tools._get_prefixes()
        """
        json_data = self.get_json_data()
        if json_data is None:
            return []

        return json_data.get("prefixes", [])

    def build_service_names_list(self) -> list:
        """Return the alphabetized AWS service names.

        Returns:
            Unique service names from the AWS JSON.

        Example:
            service_names = tools.build_service_names_list()
        """
        service_names = set()

        for prefix_data in self._get_prefixes():
            service_name = prefix_data.get("service")
            if service_name is not None:
                service_names.add(service_name)

        return sorted(service_names)

    def build_region_names_list(self) -> list:
        """Return the alphabetized AWS region names.

        Returns:
            Unique region names from the AWS JSON.

        Example:
            region_names = tools.build_region_names_list()
        """
        region_names = set()

        for prefix_data in self._get_prefixes():
            region_name = prefix_data.get("region")
            if region_name is not None:
                region_names.add(region_name)

        return sorted(region_names)

    def lookup_ip_address_service_usage(self, ip_address: str) -> list:
        """Find AWS prefixes that contain an IP address.

        Args:
            ip_address: The IP address to look for.

        Returns:
            Matching service, region, and prefix details.

        Example:
            matches = tools.lookup_ip_address_service_usage("192.0.2.1")
        """
        address_tools = IPAddressTools()
        matching_prefixes = []

        for prefix_data in self._get_prefixes():
            network_prefix = prefix_data.get("ip_prefix")
            if network_prefix is None:
                continue

            address_is_in_prefix = address_tools.check_if_ip_address_in_network_prefix(
                ip_address,
                network_prefix,
            )
            if not address_is_in_prefix:
                continue

            matching_prefix = {
                "service": prefix_data.get("service"),
                "region": prefix_data.get("region"),
                "ip_prefix": network_prefix,
            }
            matching_prefixes.append(matching_prefix)

        matching_prefixes.sort(key=itemgetter("service"))
        return matching_prefixes

    def lookup_prefixes_by_service_names(self, service_name: str) -> list:
        """Return the sorted IPv4 prefixes used by an AWS service.

        Args:
            service_name: The AWS service name to look for.

        Returns:
            Unique network prefixes used by that service.

        Example:
            prefixes = tools.lookup_prefixes_by_service_names("AMAZON")
        """
        matching_prefixes = set()

        for prefix_data in self._get_prefixes():
            prefix_service_name = prefix_data.get("service")
            network_prefix = prefix_data.get("ip_prefix")

            if prefix_service_name == service_name and network_prefix is not None:
                matching_prefixes.add(network_prefix)

        return sorted(matching_prefixes, key=ipaddress.ip_network)
    def lookup_prefixes_by_region_names(self, region_name: str) -> list:
        """Return the sorted IPv4 prefixes used by an AWS region.

        Args:
            region_name: The AWS region name to look for.

        Returns:
            Unique network prefixes used by that region.

        Example:
            prefixes = tools.lookup_prefixes_by_region_names("us-east-1")
        """
        matching_prefixes = set()

        for prefix_data in self._get_prefixes():
            prefix_region_name = prefix_data.get("region")
            network_prefix = prefix_data.get("ip_prefix")

            if prefix_region_name == region_name and network_prefix is not None:
                matching_prefixes.add(network_prefix)

        return sorted(matching_prefixes, key=ipaddress.ip_network)


def main():
    """Provide a place to work through methods during development.
    Example:
        tools = AmazonPrefixTools()
        service_names = tools.build_service_names_list()
    """
    pass


if __name__ == "__main__":
    main()