"""
IP Netmask calculation utilities for pgpycis
Ported from Perl Net::Netmask
Used for pg_hba.conf authentication rule validation
"""

import ipaddress
from typing import Tuple, Optional


class Netmask:
    """IP netmask utilities for network calculations"""
    
    def __init__(self, netblock):
        """
        Initialize with a netblock specification
        Formats: CIDR (10.0.0.0/24), dotted-quad mask (10.0.0.0 255.255.255.0),
                 range (10.0.0.0-10.0.0.255), single IP (10.0.0.1)
        """
        self.original = netblock
        self.network = None
        self.broadcast = None
        self.first = None
        self.last = None
        self.mask = None
        self.bits = None
        
        self._parse_netblock(netblock)
    
    def _parse_netblock(self, netblock):
        """Parse various netblock formats"""
        netblock = netblock.strip()
        
        # Try CIDR notation first (e.g., 10.0.0.0/24)
        if "/" in netblock:
            try:
                network = ipaddress.ip_network(netblock, strict=False)
                self.network = network.network_address
                self.broadcast = network.broadcast_address
                self.mask = network.netmask
                self.bits = network.prefixlen
                self.first = int(network.network_address)
                self.last = int(network.broadcast_address)
                return
            except ValueError:
                pass
        
        # Try dotted-quad mask (e.g., 10.0.0.0 255.255.255.0)
        if " " in netblock:
            parts = netblock.split()
            if len(parts) == 2:
                try:
                    network = ipaddress.ip_network(f"{parts[0]}/{parts[1]}", strict=False)
                    self.network = network.network_address
                    self.broadcast = network.broadcast_address
                    self.mask = network.netmask
                    self.bits = network.prefixlen
                    self.first = int(network.network_address)
                    self.last = int(network.broadcast_address)
                    return
                except ValueError:
                    pass
        
        # Try range notation (e.g., 10.0.0.0-10.0.0.255)
        if "-" in netblock:
            parts = netblock.split("-")
            if len(parts) == 2:
                try:
                    start_ip = ipaddress.ip_address(parts[0].strip())
                    end_ip = ipaddress.ip_address(parts[1].strip())
                    self.first = int(start_ip)
                    self.last = int(end_ip)
                    # Approximate network and mask
                    self.network = start_ip
                    self.broadcast = end_ip
                    return
                except ValueError:
                    pass
        
        # Try single IP address
        try:
            ip = ipaddress.ip_address(netblock)
            self.network = ip
            self.broadcast = ip
            self.first = int(ip)
            self.last = int(ip)
            self.mask = ipaddress.ip_address("255.255.255.255")
            self.bits = 32 if ip.version == 4 else 128
            return
        except ValueError:
            raise ValueError(f"Invalid netblock specification: {netblock}")
    
    def contains(self, ip_address) -> bool:
        """Check if an IP address is contained in this netblock"""
        try:
            ip = ipaddress.ip_address(ip_address)
            ip_int = int(ip)
            return self.first <= ip_int <= self.last
        except ValueError:
            return False
    
    def to_cidr(self) -> str:
        """Return CIDR notation representation"""
        if self.network and self.bits:
            return f"{self.network}/{self.bits}"
        return self.original
    
    def to_dotted_quad(self) -> str:
        """Return dotted-quad mask notation"""
        if self.network and self.mask:
            return f"{self.network} {self.mask}"
        return self.original
    
    def __str__(self):
        return self.to_cidr()
    
    def __repr__(self):
        return f"Netmask('{self.original}')"


class NetworkValidator:
    """Validate network specifications in pg_hba.conf"""
    
    @staticmethod
    def is_valid_netblock(netblock) -> bool:
        """Check if a netblock specification is valid"""
        try:
            Netmask(netblock)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def parse_pg_hba_network(network_spec) -> Optional[Netmask]:
        """Parse a network specification from pg_hba.conf"""
        # Special cases
        if network_spec.lower() in ("all", "localhost", "127.0.0.1", "::1"):
            return Netmask(network_spec)
        
        try:
            return Netmask(network_spec)
        except ValueError:
            return None
    
    @staticmethod
    def ip_in_hba_range(ip_address, hba_network) -> bool:
        """Check if an IP matches an hba.conf network specification"""
        try:
            netmask = NetworkValidator.parse_pg_hba_network(hba_network)
            if netmask:
                return netmask.contains(ip_address)
        except (ValueError, TypeError):
            pass
        return False


# Test/Demo functions
if __name__ == "__main__":
    # Example usage
    test_cases = [
        "192.168.1.0/24",
        "10.0.0.0 255.255.255.0",
        "172.16.0.1-172.16.0.255",
        "127.0.0.1",
    ]
    
    for spec in test_cases:
        try:
            nm = Netmask(spec)
            print(f"{spec} -> CIDR: {nm.to_cidr()}")
        except ValueError as e:
            print(f"{spec} -> ERROR: {e}")
