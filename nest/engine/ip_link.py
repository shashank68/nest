# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""IP link commands"""
import logging
from .exec import exec_subprocess

logger = logging.getLogger(__name__)


def create_veth(dev_name1, dev_name2):
    """
    Create a veth pair with endpoint interfaces `dev_name1`
    and `dev_name2`

    Parameters
    ----------
    dev_name1 : str
    dev_name2 : str
    """
    exec_subprocess(f"ip link add {dev_name1} type veth peer name {dev_name2}")


def create_ifb(dev_name):
    """
    Create a IFB

    Parameters
    ----------
    dev_name : str
        interface names
    """

    exec_subprocess(f"ip link add {dev_name} type ifb")


def add_int_to_ns(ns_name, dev_name):
    """
    Add interface to a namespace

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        interface name
    """
    exec_subprocess(f"ip link set {dev_name} netns {ns_name}")


def set_int_up(ns_name, dev_name):
    """
    Set interface mode to up

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        interface name
    """
    exec_subprocess(f"ip netns exec {ns_name} ip link set dev {dev_name} up")


def setup_veth(ns_name1, ns_name2, dev_name1, dev_name2):
    """
    Sets up veth connection between interfaces. The interfaces are
    set up as well.

    The connections are made between `dev_name1` in `ns_name1` and
    `dev_name2` in `ns_name2`

    Parameters
    ----------
    ns_name1 : str
    dev_name1 : str
    dev_name2 : str
    ns_name2 : str
    """
    create_veth(dev_name1, dev_name2)
    add_int_to_ns(ns_name1, dev_name1)
    add_int_to_ns(ns_name2, dev_name2)
    set_int_up(ns_name1, dev_name1)
    set_int_up(ns_name2, dev_name2)


def setup_ifb(ns_name, dev_name):
    """
    Sets up an IFB device. The device is setup as well.

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        name of IFB
    """

    create_ifb(dev_name)
    add_int_to_ns(ns_name, dev_name)
    set_int_up(ns_name, dev_name)


def set_interface_mode(ns_name, dev_name, mode):
    """
    Set interface mode up or down

    Parameters
    ----------
    ns_name : str
    dev_name : str
    mode : str
        'up' or 'down'
    """
    exec_subprocess(f"ip netns exec {ns_name} ip link set dev {dev_name} {mode}")


def set_mtu_interface(ns_name, dev_name, mtu_value):
    """
    Set the MTU for the interface

    Parameters
    ----------
    ns_name : str
    dev_name : str
    mtu_value : int
    """
    exec_subprocess(
        f"ip netns exec {ns_name} ip link set dev {dev_name} mtu {mtu_value}"
    )
    # Verify if the mtu is set
    mtu = int(
        exec_subprocess(
            f" ip netns exec {ns_name} cat /sys/class/net/{dev_name}/mtu", output=True
        )
    )
    if mtu != mtu_value:
        logger.error(
            "MTU of interface %s wasn't set to %s!", str(dev_name), str(mtu_value)
        )
