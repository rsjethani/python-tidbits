import argparse
import math
import re


def _validate_and_split(cidr_str):
    """ Validate CIDR string and return a list of cidr parts

    For e.g. "192.168.12.40/24" -> [192, 168, 12, 40, 24]
    """
    match = re.match(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})$", cidr_str)
    if not match:
        raise Exception("'{}' not a valid cidr notation".format(cidr_str))

    # convert all pieces of notation to a list on integers
    try:
        parts = [int(val) for val in match.groups()]
    except ValueError as err:
        print(err)

    # validate octet values
    for octet in parts[0:4]:
        if octet < 0 or octet > 255:
            raise Exception("ERROR: octet '{}' not in between 0-255".format(octet))

    # validate netmask value
    if parts[-1] < 0 or parts[-1] > 32:
        raise Exception("ERROR: netmask '{}' not in between 0-32".format(parts[-1]))

    return parts


def _number_to_octet_string(num):
    """Convert number to IP like string
    
    For e.g. 4294967295 -> "255.255.255.255"
    """
    # convert integer to a list of separate bytes
    octets = num.to_bytes(math.ceil(num.bit_length() / 8), "big")
    # convert each byte to integer representation
    ints = [int(octet) for octet in octets]
    # create a dot separated string of above integers
    return ".".join([str(val) for val in ints])


def cidr_info(cidr_str):
    *octets, network_bits = _validate_and_split(cidr_str)
    host_bits = 32 - network_bits

    # a base 255.255.255.255(b"\xff\xff\xff\xff") to be used in other calculations
    base = 4294967295

    ## Calculate Total Hosts ##
    total_hosts = 2 ** host_bits

    ## Calculate Netmask ##
    netmask = base << host_bits
    # remove extra leading 1s added due to shifting in above steps
    netmask &= base

    ## Calculate Network ##
    network = int.from_bytes(octets, "big") & netmask

    ## Calculate First IP ##
    first_ip = network

    ## Calculate Last IP ##
    last_ip = network | (netmask ^ base)

    return {
        "network": _number_to_octet_string(network),
        "netmask": _number_to_octet_string(netmask),
        "first_ip": _number_to_octet_string(first_ip),
        "last_ip": _number_to_octet_string(last_ip),
        "total_hosts": total_hosts
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cidr", help="a cidr notation string like a.b.c.d/n")
    args = parser.parse_args()

    try:
        info = cidr_info(args.cidr)
    except Exception as err:
        raise SystemExit(err)

    print("NETWORK: ", info["network"])
    print("NETMASK: ", info["netmask"])
    print("FIRST IP: ", info["first_ip"])
    print("LAST IP: ", info["last_ip"])
    print("TOTAL HOSTS: ", info["total_hosts"])


if __name__ == "__main__":
    main()
