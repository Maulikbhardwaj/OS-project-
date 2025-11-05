# subnet_simple.py
# Minimal subnet calculator:
# - Show network, mask, broadcast, usable range
# - Optional: split into subnets that can each fit 'hosts_per_subnet' (greedy VLSM)

import ipaddress
from typing import List, Tuple, Optional

def info(cidr: str) -> dict:
    net = ipaddress.ip_network(cidr, strict=False)
    first, last = (None, None)
    if net.prefixlen <= 30:
        hosts = list(net.hosts())
        first = str(hosts[0]) if hosts else None
        last  = str(hosts[-1]) if hosts else None
    return {
        "input": cidr,
        "network": str(net.network_address),
        "prefix": net.prefixlen,
        "mask": str(net.netmask),
        "broadcast": str(net.broadcast_address),
        "usable_first": first,
        "usable_last": last,
        "hosts_usable": max(0, net.num_addresses - (2 if net.prefixlen <= 30 else 0)),
        "total_addresses": net.num_addresses,
    }

def needed_prefix_for_hosts(hosts_per_subnet: int) -> int:
    # For a classic subnet, usable hosts = 2^(32-p) - 2  (except /31,/32)
    # Find smallest p s.t. usable_hosts >= hosts_per_subnet
    for p in range(32, -1, -1):
        total = 2 ** (32 - p)
        usable = total if p >= 31 else total - 2
        if usable >= hosts_per_subnet:
            return p
    return 0

def split_for_hosts(cidr: str, hosts_per_subnet: int) -> List[str]:
    net = ipaddress.ip_network(cidr, strict=False)
    target_p = needed_prefix_for_hosts(hosts_per_subnet)
    if target_p < net.prefixlen:
        # Can't make subnets that are bigger than the original; just return original
        return [str(net)]
    # If target is equal or longer prefix (i.e., smaller subnets), subdivide
    if target_p == net.prefixlen:
        return [str(net)]
    # ipaddress.subnets() splits by +1 prefix at a time; iterate until we reach target
    subnets = [net]
    p = net.prefixlen
    while p < target_p:
        next_level = []
        for s in subnets:
            next_level.extend(list(s.subnets(prefixlen_diff=1)))
        subnets = next_level
        p += 1
    return [str(s) for s in subnets]

def show(cidr: str, hosts_per_subnet: Optional[int] = None) -> None:
    base = info(cidr)
    print(f"Input: {base['input']}")
    print(f"Network:   {base['network']}/{base['prefix']}  Mask: {base['mask']}")
    print(f"Broadcast: {base['broadcast']}")
    print(f"Usable:    {base['usable_first']}  →  {base['usable_last']}")
    print(f"Usable hosts: {base['hosts_usable']}  (total addrs: {base['total_addresses']})")
    if hosts_per_subnet:
        print(f"\nSubnets for ≥{hosts_per_subnet} hosts each:")
        subs = split_for_hosts(cidr, hosts_per_subnet)
        # Show each with usable host count
        for s in subs:
            si = info(s)
            print(f"  {si['network']}/{si['prefix']}  "
                  f"mask={si['mask']}  usable={si['hosts_usable']}  "
                  f"range={si['usable_first']}–{si['usable_last']}")

if __name__ == "__main__":
    # quick demos:
    # python subnet_simple.py
    # or modify below to test different inputs
    show("192.168.10.0/24")
    print("\n---")
    show("192.168.10.0/24", hosts_per_subnet=50)
