Subnet Calculator – Technical Report

Author: Harshitha
Module: Networking – Subnet Calculator
Project: OS & Networking Group Project
Date: 2025

⸻

1. Introduction

Subnetting is a key networking technique that divides a large IP network into smaller, structured subnetworks. It improves routing efficiency, reduces congestion, optimizes address usage, and adds control/security.
This report explains the subnetting concepts, implementation details, functionality of the subnet calculator, sample outputs, and limitations.

⸻

2. Subnetting Concepts

2.1 IPv4 Address Structure

IPv4 addresses contain 32 bits, grouped into four octets:

A.B.C.D

Programs distinguish between:
	•	Network portion
	•	Host portion

Subnetting changes how many bits represent each.

⸻

2.2 CIDR (Classless Inter-Domain Routing)

CIDR represents networks such as:

192.168.1.0/24

/24 → first 24 bits represent the network, last 8 bits represent hosts.

⸻

2.3 Subnet Mask

A subnet mask defines the network portion.
Examples:

Prefix	Mask
/24	255.255.255.0
/16	255.255.0.0
/30	255.255.255.252

Binary for /24:

11111111.11111111.11111111.00000000


⸻

2.4 Wildcard Mask

Used for ACLs.

Wildcard = 255 – mask

Example:

Mask     : 255.255.255.0
Wildcard : 0.0.0.255


⸻

2.5 Network and Broadcast Addresses

For network 192.168.1.0/24:
	•	Network: 192.168.1.0
	•	Broadcast: 192.168.1.255

⸻

2.6 Usable Host Range

Formula:

Usable hosts = 2^(32 - prefix) - 2

For /24 → 254 hosts.

⸻

2.7 IP Classes

Class	Range	Purpose
A	0–127	Large networks
B	128–191	Medium
C	192–223	Small
D	224–239	Multicast
E	240–255	Reserved


⸻

2.8 Private vs Public IP Ranges

Private IP ranges:
	•	10.0.0.0/8
	•	172.16.0.0/12
	•	192.168.0.0/16

The calculator identifies:
	•	is_private
	•	is_global

⸻

2.9 VLSM (Variable Length Subnet Masking)

VLSM assigns different subnet sizes depending on required hosts.

Example:

Need ≥ 50 hosts → prefix /26

The calculator handles VLSM splitting.

⸻

3. Implementation

The subnet calculator is implemented in Python using:
	•	ipaddress for subnet calculations
	•	argparse for command-line interface
	•	json for JSON export
	•	os + re for system IP detection
	•	Custom logic for wildcard, binary, class detection, etc.

The tool acts like a mini networking utility similar to Linux commands.

⸻

3.1 Core Components

3.1.1 info(cidr)

Returns detailed subnet information:
	•	Network, prefix, mask
	•	Wildcard
	•	Broadcast
	•	First & last usable host
	•	Usable host count
	•	Address class
	•	Private/public
	•	Binary representation

Printed using print_info_table().

⸻

3.1.2 smallest_prefix_for_hosts() / split_for_hosts()

Used for VLSM.

Steps:
	1.	Determine prefix that satisfies host requirements
	2.	Divide network into target-sized subnets
	3.	Return subnets list

⸻

3.1.3 overlap(cidr1, cidr2)

Checks whether two networks overlap.

Useful for routing and firewall rule checking.

⸻

3.1.4 get_system_ip()

Runs:

ip addr show

Extracts the host machine’s IP address using regex.

⸻

3.1.5 CLI Arguments

Example usage:

python subnet_calc.py 192.168.1.0/24
python subnet_calc.py 192.168.1.0/24 --hosts 50
python subnet_calc.py --json 192.168.1.0/24
python subnet_calc.py --overlap 10.0.0.0/24 10.0.1.0/24
python subnet_calc.py --system-ip
python subnet_calc.py --examples


⸻

4. Sample Output

Input:

171.1.89.7/24

Output:

------------------------------------------------------------
Subnet information for 171.1.89.7/24
------------------------------------------------------------
Network:       171.1.89.0/24
Mask:          255.255.255.0
Wildcard:      0.0.0.255
Broadcast:     171.1.89.255
Usable range:  171.1.89.1 → 171.1.89.254
Usable hosts:  254 (total: 256)
Block size:    256
Class:         B
Private network: No
Global routable: Yes

Binary representations:
Network:       10101011.00000001.01011001.00000000
Mask:          11111111.11111111.11111111.00000000
Broadcast:     10101011.00000001.01011001.11111111
Wildcard:      00000000.00000000.00000000.11111111


⸻

5. Comparison with OS Networking Tools

Linux and macOS networking tools provide several built-in capabilities, such as detecting the system’s IP address, calculating the network, subnet mask, and broadcast address. Our subnet calculator also performs these core tasks.
However, operating systems generally do not show usable host ranges, do not perform VLSM subnetting, and do not check whether two subnets overlap. These features are fully supported by our subnet calculator, which makes it more useful for detailed subnet analysis and learning.
On the other hand, operating systems can modify routing tables and apply actual network configurations, while our tool is non-destructive and purely computational—meaning it cannot and does not modify any system networking settings.

⸻

6. Limitations
	•	No IPv6 support
	•	No graphical/subnet-tree visualization
	•	Does not scan actual hosts
	•	No integration with routing tables

⸻

7. Future Improvements
	•	IPv6 support
	•	ASCII network diagrams
	•	Real-time host scanning
	•	Web-based UI
	•	Automatic PDF/HTML report generation

⸻

8. Conclusion

The subnet calculator module is a complete, extensively featured networking tool that performs:
	•	IPv4 subnet discovery
	•	Detailed subnet analysis
	•	VLSM calculations
	•	Subnet overlap checks
	•	System IP detection
	•	JSON export

This module complements the project’s OS-related components by focusing on practical, real-world networking computation.
