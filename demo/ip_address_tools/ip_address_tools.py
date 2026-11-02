import ipaddress


class IPAddressTools:

    def __init__(self):
        """Initialize the IP address helper, which currently has no state."""

    def check_if_ipv4_address(self, ipv4_address):
        """
        This method will check input for IPv4 address validation.
        """
        try:
            ipaddress.IPv4Address(ipv4_address)
            return True
        except ValueError:
            return False

    def check_if_ip_address_in_network_prefix(self, ip_address, network_prefix):
        """
        This method will take an IPv4 address and a network prefix as input.
        It will then check if the IP address falls withing the network prefix.
        It will then return True/False based on the result of the check.
        """

        try:
            ip = ipaddress.ip_address(ip_address)
            network = ipaddress.ip_network(network_prefix, strict=False)
            return ip in network
        except ValueError as e:
            raise ValueError(f'Invalid IP address or network prefix: {e}')

    def get_network_information_from_ipv4_address(self, ipv4_address, cidr_prefix):
        """
        Take an IPv4 address and CIDR prefix and return the network information.
        """
        if self.check_if_ipv4_address(ipv4_address) is False:
            raise ValueError(f'Invalid IPv4 address: {ipv4_address}')

        if not isinstance(cidr_prefix, int) or not (0 <= cidr_prefix <= 32):
            raise ValueError(
                f'Invalid CIDR prefix: {cidr_prefix}. '
                'Must be a valid CIDR mask value between 0 and 32).'
            )

        try:
            ip = ipaddress.ip_interface(f'{ipv4_address}/{cidr_prefix}')
            network = ip.network

            if network.prefixlen >= 31:
                first_host = network.network_address
                last_host = network.broadcast_address
            else:
                first_host = network.network_address + 1
                last_host = network.broadcast_address - 1

            return {
                'network_address': str(network.network_address),
                'broadcast_address': str(network.broadcast_address),
                'netmask': str(network.netmask),
                'prefix_length': network.prefixlen,
                'num_addresses': network.num_addresses,
                'hosts': f'{first_host} - {last_host}',
            }

        except ValueError as e:
            raise ValueError(f'Invalid IPv4 address or CIDR prefix: {e}')


def main():
    """Keep a module entry point available for manual development checks.

    Example:
        Run this module directly to execute development-only checks.
    """



if __name__ == '__main__':
    main()