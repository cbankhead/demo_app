import ipaddress
import logging
import re
from http import HTTPStatus
from operator import itemgetter

import requests

from ..cache_utils import get_or_fetch
from ..ip_address_tools.ip_address_tools import IPAddressTools


logger = logging.getLogger(__name__)


class AzurePrefixTools:
    """Download and search the IP address ranges published by Azure.

    Example:
        tools = AzurePrefixTools()
        service_names = tools.build_service_names_list()
    """

    def __init__(self):
        """Set Azure's information page and mark its JSON as not loaded.

        Returns:
            Nothing.

        Example:
            tools = AzurePrefixTools()
        """
        # This page points to Azure's latest raw JSON file.
        self.azure_info_url: str = (
            "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
        )

        # This holds the full JSON response, or None before it is loaded.
        self.json_data = None

    def get_json_data(self):
        """Return Azure JSON, loading it from the shared cache when possible.

        Returns:
            The full Azure JSON response, or None if it could not be loaded.

        Example:
            json_data = tools.get_json_data()
        """
        if self.json_data is None:
            self.json_data = get_or_fetch(
                "azure_prefix_data",
                self._fetch_json_data,
            )

        return self.json_data

    def _fetch_json_data(self):
        """Find and download Azure's latest JSON file.

        Returns:
            The full Azure JSON response, or None if a request failed.

        Example:
            json_data = tools._fetch_json_data()
        """
        information_page = self._get_information_page()
        if information_page is None:
            return None

        download_url = self._find_json_download_url(information_page)
        if download_url is None:
            return None

        return self._download_json(download_url)

    def _get_information_page(self):
        """Download Azure's page that contains the current JSON link.

        Returns:
            The page text, or None if Azure's page could not be downloaded.

        Example:
            page_text = tools._get_information_page()
        """
        try:
            response = requests.get(
                self.azure_info_url,
                timeout=10,
                headers={"User-Agent": "Demo App"},
            )
        except requests.RequestException:
            logger.exception("Could not download the Azure IP ranges page.")
            return None

        if response.status_code != HTTPStatus.OK:
            logger.warning(
                "Azure IP ranges page returned status %s.",
                response.status_code,
            )
            return None

        return response.text

    def _find_json_download_url(self, page_text: str):
        """Find Azure's changing JSON download link in page text.

        Args:
            page_text: The contents of Azure's information page.

        Returns:
            The download URL, or None if the page has no matching link.

        Example:
            download_url = tools._find_json_download_url(page_text)
        """
        url_pattern = (
            r"https://download\.microsoft\.com/[^\s\"']+/"
            r"ServiceTags_Public_[0-9]+\.json"
        )
        download_url_match = re.search(url_pattern, page_text)

        if download_url_match is None:
            logger.warning("Could not find the Azure JSON download link.")
            return None

        return download_url_match.group(0)

    def _download_json(self, download_url: str):
        """Download Azure's JSON response from a URL.

        Args:
            download_url: The current Azure JSON download link.

        Returns:
            The full Azure JSON response, or None if the request failed.

        Example:
            json_data = tools._download_json(download_url)
        """
        try:
            response = requests.get(
                download_url,
                timeout=10,
                headers={"User-Agent": "Demo App"},
            )
        except requests.RequestException:
            logger.exception("Could not download Azure IP range JSON.")
            return None

        if response.status_code != HTTPStatus.OK:
            logger.warning(
                "Azure IP range download returned status %s.",
                response.status_code,
            )
            return None

        return response.json()

    def _get_service_tags(self):
        """Return Azure service-tag records, or an empty list after a failure.

        Returns:
            A list of Azure service-tag records.

        Example:
            service_tags = tools._get_service_tags()
        """
        json_data = self.get_json_data()
        if json_data is None:
            return []

        return json_data.get("values", [])

    def _get_ipv4_prefixes(self, service_tag: dict) -> list:
        """Return the IPv4 prefixes listed in one service tag.

        Args:
            service_tag: One service record from Azure's JSON response.

        Returns:
            IPv4 network prefixes. IPv6 prefixes are left out.

        Example:
            prefixes = tools._get_ipv4_prefixes(service_tag)
        """
        service_properties = service_tag.get("properties") or {}
        address_prefixes = service_properties.get("addressPrefixes") or []
        ipv4_prefixes = []

        for network_prefix in address_prefixes:
            if ":" not in network_prefix:
                ipv4_prefixes.append(network_prefix)

        return ipv4_prefixes

    def build_service_names_list(self) -> list:
        """Return the alphabetized Azure service names.

        Returns:
            Unique service names from Azure's JSON.

        Example:
            service_names = tools.build_service_names_list()
        """
        service_names = set()

        for service_tag in self._get_service_tags():
            service_name = service_tag.get("name")
            if service_name is not None:
                service_names.add(service_name)

        return sorted(service_names)

    def build_region_names_list(self) -> list:
        """Return the alphabetized Azure region names.

        Returns:
            Unique, non-empty region names from Azure's JSON.

        Example:
            region_names = tools.build_region_names_list()
        """
        region_names = set()

        for service_tag in self._get_service_tags():
            service_properties = service_tag.get("properties") or {}
            region_name = service_properties.get("region")
            if region_name:
                region_names.add(region_name)

        return sorted(region_names)

    def lookup_ip_address_service_usage(self, ip_address: str) -> list:
        """Find Azure prefixes that contain an IP address.

        Args:
            ip_address: The IP address to look for.

        Returns:
            Matching service, region, and prefix details.

        Example:
            matches = tools.lookup_ip_address_service_usage("192.0.2.1")
        """
        address_tools = IPAddressTools()
        matching_prefixes = []

        for service_tag in self._get_service_tags():
            service_properties = service_tag.get("properties") or {}
            service_name = service_tag.get("name")
            region_name = service_properties.get("region")

            for network_prefix in self._get_ipv4_prefixes(service_tag):
                address_is_in_prefix = address_tools.check_if_ip_address_in_network_prefix(
                    ip_address,
                    network_prefix,
                )
                if not address_is_in_prefix:
                    continue

                matching_prefix = {
                    "service": service_name,
                    "region": region_name,
                    "ip_prefix": network_prefix,
                }
                matching_prefixes.append(matching_prefix)

        matching_prefixes.sort(key=itemgetter("service"))
        return matching_prefixes

    def lookup_prefixes_by_service_names(self, service_name: str) -> list:
        """Return the sorted IPv4 prefixes used by an Azure service.

        Args:
            service_name: The Azure service name to look for.

        Returns:
            Unique network prefixes used by that service.

        Example:
            prefixes = tools.lookup_prefixes_by_service_names("AzureCloud")
        """
        matching_prefixes = set()

        for service_tag in self._get_service_tags():
            service_tag_name = service_tag.get("name")
            if service_tag_name != service_name:
                continue

            for network_prefix in self._get_ipv4_prefixes(service_tag):
                matching_prefixes.add(network_prefix)

        return sorted(matching_prefixes, key=ipaddress.ip_network)
    def lookup_prefixes_by_region_names(self, region_name: str) -> list:
        """Return the sorted IPv4 prefixes used by an Azure region.

        Args:
            region_name: The Azure region name to look for.

        Returns:
            Unique network prefixes used by that region.

        Example:
            prefixes = tools.lookup_prefixes_by_region_names("eastus")
        """
        matching_prefixes = set()

        for service_tag in self._get_service_tags():
            service_properties = service_tag.get("properties") or {}
            service_region_name = service_properties.get("region")
            if service_region_name != region_name:
                continue

            for network_prefix in self._get_ipv4_prefixes(service_tag):
                matching_prefixes.add(network_prefix)

        return sorted(matching_prefixes, key=ipaddress.ip_network)


def main():
    """Provide a place to work through methods during development.
    Example:
        tools = AzurePrefixTools()
        service_names = tools.build_service_names_list()
    """
    pass


if __name__ == "__main__":
    main()