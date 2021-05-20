# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Handle traffic control entities"""

from nest.topology_map import TopologyMap
from .. import engine

# TODO: Improve this module such that the below pylint disables are no
# longer required

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


class TrafficControlHandler:
    """Handles all traffic control related methods for a device

    Attributes
    ----------
    node_id : str
        The id of the namespace to which it belongs
    dev_id : str
        The id of the device to to which it belongs
    qdisc_list : list
        The list of all qdisc on a specific device
    class_list : list
        The list of all class on a specific device
    filter_list : list
        The list of all filters on a specific device
    """

    def __init__(self, node_id, dev_id):
        """
        Constructor for a traffic controller

        Parameters
        ----------
        node_id : str
            The id of the namespace to which the device belongs to
        dev_id : str
            The id of the device to which the traffic controller belongs to
        """
        self.node_id = node_id
        self.dev_id = dev_id
        self.qdisc_list = []
        self.class_list = []
        self.filter_list = []

    def add_qdisc(self, qdisc, parent="root", handle="", **kwargs):
        """
        Add a qdisc (Queueing Discipline) to this device

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the device
        dev : Interface class
            The device to which the qdisc is to be added
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        """
        self.qdisc_list.append(
            Qdisc(self.node_id, self.dev_id, qdisc, parent, handle, **kwargs)
        )

        # Add qdisc to TopologyMap
        TopologyMap.add_qdisc(self.node_id, self.dev_id, qdisc, handle, parent=parent)

    def delete_qdisc(self, handle):
        """
        Delete qdisc (Queueing Discipline) from this device

        Parameters
        ----------
        handle : string
            Handle of the qdisc to be deleted
        """
        # TODO: Handle this better by using the destructor in traffic-control
        counter = 0
        for qdisc in self.qdisc_list:
            if qdisc.handle == handle:
                engine.delete_qdisc(
                    qdisc.node_id, qdisc.dev_id, qdisc.parent, qdisc.handle
                )
                TopologyMap.delete_qdisc(self.node_id, self.dev_id, handle)
                self.qdisc_list.pop(counter)
                break
            counter += 1

    def add_class(self, qdisc, parent="root", classid="", **kwargs):
        """
        Create an object that represents a class

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the device
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        classid : string
            id of the class (Default value = '')
        """
        self.class_list.append(
            Class(self.node_id, self.dev_id, qdisc, parent, classid, **kwargs)
        )

    # pylint: disable=too-many-arguments
    def add_filter(
        self,
        priority,
        filtertype,
        flowid,
        protocol="ip",
        parent="root",
        handle="",
        **kwargs
    ):
        """
        Design a Filter to assign to a Class or Qdisc

        Parameters
        ----------
        protocol : string
            protocol used (Default value = 'ip')
        priority : int
            priority of the filter
        filtertype : string
            one of the available filters
        flowid : Class
            classid of the class where the traffic is enqueued
            if the traffic passes the filter
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        filter : dictionary
            filter parameters
        """
        # TODO: Verify type of parameters
        # TODO: Reduce arguments to the engine functions by finding parent and handle automatically

        self.filter_list.append(
            Filter(
                self.node_id,
                self.dev_id,
                protocol,
                priority,
                filtertype,
                flowid,
                parent,
                handle,
                **kwargs
            )
        )


class Qdisc:
    """Handle Queueing Discipline"""

    def __init__(self, node_id, dev_id, qdisc, parent="root", handle="", **kwargs):
        """
        Constructor to add a qdisc (Queueing Discipline) to an interface (device)

        Parameters
        ----------
        node_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        qdisc : str
            The qdisc which needs to be added to the interface
        dev_id : str
            The id of the interface to which the qdisc is to be added
        node_id : str
            The id of the namespace that the device belongs to
        parent : str
            id of the parent class in major:minor form(optional)
        handle : str
            id of the filter
        """
        self.node_id = node_id
        self.dev_id = dev_id
        self.qdisc = qdisc
        self.parent = parent
        self.handle = handle

        engine.add_qdisc(node_id, dev_id, qdisc, parent, handle, **kwargs)


class Class:
    """Handle classes associated to qdisc"""

    def __init__(self, node_id, dev_id, qdisc, parent="root", classid="", **kwargs):
        """
        Constructor to create an object that represents a class

        Parameters
        ----------
        node_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        node_id : str
            The id of the namespace that the device belongs to
        qdisc : str
            The qdisc which needs to be added to the interface
        parent : str
            id of the parent class in major:minor form(optional)
        classid : str
            id of the class
        """
        self.node_id = node_id
        self.dev_id = dev_id
        self.qdisc = qdisc  # NOTE: should be renamed to knid
        self.parent = parent
        self.classid = classid

        engine.add_class(node_id, dev_id, parent, qdisc, classid, **kwargs)


class Filter:
    """Handle filters to assign to class/qdisc"""

    def __init__(
        self,
        node_id,
        dev_id,
        protocol,
        priority,
        filtertype,
        flowid,
        parent="root",
        handle="",
        **kwargs
    ):
        """
        Constructor to design a Filter to assign to a Class or Qdisc

        Parameters
        ----------
        node_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        protocol : str
            protocol used
        priority : int
            priority of the filter
        filtertype : str
            one of the available filters
        flowid : Class
            classid of the class where the traffic is enqueued
            if the traffic passes the filter
        parent : str
            id of the parent class in major:minor form(optional)
        handle : str
            id of the filter
        filter : dictionary
            filter parameters
        """
        self.node_id = node_id
        self.dev_id = dev_id
        self.protocol = protocol
        self.priority = priority
        self.filtertype = filtertype
        self.flowid = flowid
        self.parent = parent
        self.handle = handle

        engine.add_filter(
            node_id, dev_id, protocol, priority, filtertype, parent, handle, **kwargs
        )
