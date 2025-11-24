#!/usr/bin/env python3
"""
Final upgraded Subnet Calculator
Combines:
- Jaskaran's professional CLI version with JSON, overlap check, subnet splitting, binary/wildcard info
- Harshitha's system IP detection and interactive prompts
Author: Team OS-project
"""

from __future__ import annotations
import ipaddress
import argparse
import os
import re
import sys
import json
from typing import List, Optional, Dict


# ---------------- Utility Functions ---------------- #

def to_bin(ip: str) -> str:
    """Convert dotted-decimal IP to binary"""
    return '.'.join(f'{int(o):08b}' for o in ip.split('.'))


def ip_class_from_first_octet(octet: int) -> str:
    if 0 <= octet <= 127:
        return "A"
    if 128 <= octet <= 191:
        return "B"
    if 192 <= octet <= 223:
        return "C"
    if 224 <= octet <= 239:
        return "D (Multicast)"
    if 240 <= octet <= 255:
        return "E (Reserved)"
    return "Unknown"


def wildcard_from_netmask(mask: str) -> str:
    parts = mask.split('.')
    return '.'.join(str(255 - int(p)) for p in parts)


def hosts_usable_from_prefix(prefix: int) -> int:
    total = 2 ** (32 - prefix)
    return total if prefix >= 31 else max(0, total - 2)


# ---------------- Subnet Info Functions ---------------- #

def info(cidr: str) -> Dict[str, Optional[str]]:
    """Return detailed subnet information"""
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except Exception as e:
        raise ValueError(f"Invalid CIDR '{cidr}': {e}")

    network = str(net.network_address)
    prefix = net.prefixlen
    mask = str(net.netmask)
    broadcast = str(net.broadcast_address)

    first_usable = last_usable = None
    if prefix <= 30:
        hosts = list(net.hosts())
        if hosts:
            first_usable = str(hosts[0])
            last_usable = str(hosts[-1])

    total_addrs = net.num_addresses
    usable = hosts_usable_from_prefix(prefix)

    wildcard = wildcard_from_netmask(mask)
    first_octet = int(network.split('.')[0])
    cls = ip_class_from_first_octet(first_octet)
    is_private = net.network_address.is_private
    is_global = net.network_address.is_global
    block_size = total_addrs

    return {
        "input": cidr,
        "network": network,
        "prefix": prefix,
        "mask": mask,
        "wildcard": wildcard,
        "broadcast": broadcast,
        "usable_first": first_usable,
        "usable_last": last_usable,
        "hosts_usable": usable,
        "total_addresses": total_addrs,
        "class": cls,
        "is_private": bool(is_private),
        "is_global": bool(is_global),
        "block_size": block_size,
        "network_bin": to_bin(network),
        "mask_bin": to_bin(mask),
        "broadcast_bin": to_bin(broadcast),
        "wildcard_bin": to_bin(wildcard),
    }


def smallest_prefix_for_hosts(hosts_per_subnet: int) -> int:
    if hosts_per_subnet <= 0:
        raise ValueError("hosts_per_subnet must be a positive integer")
    for p in range(32, -1, -1):
        if hosts_usable_from_prefix(p) >= hosts_per_subnet:
            return p
    raise ValueError("Cannot find a prefix to satisfy the requested hosts")


def split_for_hosts(cidr: str, hosts_per_subnet: int) -> List[str]:
    net = ipaddress.ip_network(cidr, strict=False)
    target_prefix = smallest_prefix_for_hosts(hosts_per_subnet)

    if target_prefix < net.prefixlen:
        return []
    if target_prefix == net.prefixlen:
        return [str(net)]

    subnets = list(net.subnets(new_prefix=target_prefix))
    return [str(s) for s in subnets]


def overlap(cidr1: str, cidr2: str) -> bool:
    n1 = ipaddress.ip_network(cidr1, strict=False)
    n2 = ipaddress.ip_network(cidr2, strict=False)
    return n1.overlaps(n2)


# ---------------- System IP Detection ---------------- #

def get_system_ip() -> str:
    """Detect system IP on Linux/Mac"""
    try:
        output = os.popen("ip addr show").read()
        match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', output)
        if match:
            return match.group(1)
        return "Could not detect system IP."
    except Exception as e:
        return f"Error: {e}"


# ---------------- Pretty Print ---------------- #

def print_block(title: str) -> None:
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)


def print_info_table(d: Dict[str, Optional[str]]) -> None:
    print_block(f"Subnet information for {d['input']}")
    print(f"{'Network:':15}{d['network']}/{d['prefix']}")
    print(f"{'Mask:':15}{d['mask']}")
    print(f"{'Wildcard:':15}{d['wildcard']}")
    print(f"{'Broadcast:':15}{d['broadcast']}")
    print(f"{'Usable range:':15}{(d['usable_first'] or '-') + ' → ' + (d['usable_last'] or '-')}")
    print(f"{'Usable hosts:':15}{d['hosts_usable']} (total: {d['total_addresses']})")
    print(f"{'Block size:':15}{d['block_size']}")
    print(f"{'Class:':15}{d['class']}")
    print(f"{'Private network:':15}{'Yes' if d['is_private'] else 'No'}")
    print(f"{'Global routable:':15}{'Yes' if d['is_global'] else 'No'}")
    print("\nBinary representations:")
    print(f"{'Network:':15}{d['network_bin']}")
    print(f"{'Mask:':15}{d['mask_bin']}")
    print(f"{'Broadcast:':15}{d['broadcast_bin']}")
    print(f"{'Wildcard:':15}{d['wildcard_bin']}")


# ---------------- CLI ---------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Enhanced Subnet Calculator")
    p.add_argument("cidr", nargs="?", help="CIDR to analyze (e.g. 192.168.1.0/24)")
    p.add_argument("--hosts", "-H", type=int, help="Show subnets each able to hold at least N hosts")
    p.add_argument("--overlap", "-o", nargs=2, metavar=("CIDR1", "CIDR2"), help="Check overlap between two CIDRs")
    p.add_argument("--json", action="store_true", help="Output the main info as JSON")
    p.add_argument("--examples", action="store_true", help="Run internal examples")
    p.add_argument("--system-ip", action="store_true", help="Show system IP detected on this machine")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.system_ip:
        print(f"System IP: {get_system_ip()}")

    if args.examples:
        examples = [
            "192.168.10.0/24",
            ("192.168.10.0/24", 50),
            ("10.0.0.0/16", 1000),
        ]
        print("Running examples...\n")
        d = info(examples[0])
        print_info_table(d)
        print("\n--- Subnet-splits example (≥50 hosts):")
        splits = split_for_hosts(examples[1][0], examples[1][1])
        for s in splits[:10]:
            print(" ", s)
        return 0

    if args.overlap:
        a, b = args.overlap
        try:
            result = overlap(a, b)
        except ValueError as ve:
            print(f"Error: {ve}")
            return 2
        print(f"Overlap({a}, {b}) = {result}")
        return 0

    if not args.cidr:
        parser.print_help()
        return 1

    try:
        d = info(args.cidr)
    except ValueError as ve:
        print(f"Error: {ve}")
        return 2

    if args.json:
        print(json.dumps(d, indent=2))
    else:
        print_info_table(d)

    if args.hosts:
        try:
            splits = split_for_hosts(args.cidr, args.hosts)
        except ValueError as ve:
            print(f"Error: {ve}")
            return 2

        if not splits:
            print("\nRequested hosts per subnet exceed the capacity of the network.")
            overall_capacity = d["block_size"] if "block_size" in d else "unknown"
            print(f"Network capacity: {overall_capacity} addresses")
        else:
            print_block(f"Subnets for ≥{args.hosts} usable hosts each")
            for s in splits:
                si = info(s)
                print(f"  {si['network']}/{si['prefix']}  mask={si['mask']}  usable={si['hosts_usable']}  "
                      f"range={si['usable_first'] or '-'} → {si['usable_last'] or '-'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())