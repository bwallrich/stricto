# pylint: disable=duplicate-code
"""
Module for ip network addresses in CIDR notation
"""
import ipaddress
from stricto.extend import Extend
from stricto import STypeError


class Ipnetwork(Extend):
    """
    A specific class to play with ipnetwork
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must pass the type (ipaddress)

        """

        super().__init__(ipaddress, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        to encode the ip address
        """
        v = self.get_value()
        if v is None:
            return None
        return str(self.get_value())

    def __json_decode__(
        self, value: str
    ) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
        """
        Called by the specific Decoder
        to decode an ip address
        """
        return ipaddress.ip_network(value)

    def check_type(
        self,
        value,
    ):
        if isinstance(value, (ipaddress.IPv4Network, ipaddress.IPv6Network, Ipnetwork)):
            return True

        fault = False
        try:
            ipaddress.ip_network(value)
        except ValueError:
            fault = True

        if fault is True:
            raise STypeError(
                '{0}: Must be a ipnetwork (value="{value}")',
                self.path_name(),
                value=value,
            )
        return True
