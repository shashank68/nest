# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""Plot ss results"""

import logging
import matplotlib.pyplot as plt

from ..pack import Pack
from .common import simple_plot, mix_plot

logger = logging.getLogger(__name__)


def _get_list_of_ss_params():
    """
    Return list of params parsed by ss
    """
    return ["cwnd", "rtt", "dev_rtt", "ssthresh", "rto", "delivery_rate", "pacing_rate"]


def _get_ss_params_units():
    """
    Obtain the units of each ss parameters
    """
    units = {
        "cwnd": None,
        "rtt": "ms",
        "dev_rtt": "ms",
        "ssthresh": None,
        "rto": "ms",
        "delivery_rate": "Mbps",
        "pacing_rate": "Mbps",
    }
    return units


def _get_nicer_param_names():
    """
    For example,
    'rtt' -> 'RTT'
    'delivery_rate' -> 'Delivery rate'
    """
    nice_names = {
        "cwnd": "CWND",
        "rtt": "RTT",
        "dev_rtt": "DevRTT",
        "ssthresh": "ssthresh",
        "rto": "RTO",
        "delivery_rate": "Delivery rate",
        "pacing_rate": "Pacing rate",
    }
    return nice_names


def _get_ylabel(param):
    """
    Obtain y label for plots for a given parameter.

    For example, 'delivery_rate' -> 'Delivery rate (Mbps)'

    Arguments
    ---------
        param : str
            parameter

    Returns
    -------
        str
    """
    # Get ss param units
    units = _get_ss_params_units()
    # Get "nicer" param names
    nicer_param_names = _get_nicer_param_names()

    ylabel = nicer_param_names[param]
    if units[param] is not None:
        ylabel += f" ({units[param]})"

    return ylabel


def _extract_from_ss_flow(flow, node, dest_ip, dest_port):
    """
    Extract information from flow data and convert it to
    conveniently plottable data format

    Parameters
    ----------
    flow : List
        List with timestamps and stats
    node : string
        Node from which ss results were obtained from
    dest_ip : string
        Destination ip address of the flow
    dest_port : string
        Destination port of the flow

    Returns
    -------
    (timestamp, flow_params) or None
        Return timestamp and flow parameters
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "Flow from %s to destination %s:%s " "doesn't have any parsed ss result.",
            node,
            dest_ip,
            dest_port,
        )
        return None

    # First item is the "meta" item with user given information
    user_given_start_time = float(flow[0]["start_time"])

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - user_given_start_time

    timestamp = []
    flow_params = {}

    for param in _get_list_of_ss_params():
        flow_params[param] = []

    for data in flow[1:]:
        for stat in flow_params:
            if stat in data:
                flow_params[stat].append(float(data[stat]))
            else:
                flow_params[stat].append(None)
        relative_time = float(data["timestamp"]) - start_time
        timestamp.append(relative_time)

    return (timestamp, flow_params)


def _plot_ss_flow(flow, node, dest_ip, dest_port):
    """
    Plot ss stats of the flow

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : string
        Node from which ss results were obtained from
    dest_ip : string
        Destination ip address of the flow
    dest_port : string
        Destination port of the flow
    """
    values = _extract_from_ss_flow(flow, node, dest_ip, dest_port)
    if values is None:
        return None
    (timestamp, flow_params) = values

    for param in flow_params:
        fig = simple_plot(
            "Socket Stats (ss)",
            timestamp,
            flow_params[param],
            "Time (s)",
            _get_ylabel(param),
            legend_string=f"{node} to {dest_ip}:{dest_port}",
        )

        filename = f"{node}_{dest_ip}:{dest_port}_{param}.png"
        Pack.dump_plot("ss", filename, fig)
        plt.close(fig)

    return (timestamp, flow_params)


# pylint: disable=too-many-locals
def plot_ss(parsed_data):
    """
    Plot statistics obtained from ss

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """

    # pylint: disable=too-many-nested-blocks
    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for dest_ip in connection:

                all_flow_data = []

                flow_data = connection[dest_ip]
                for dest_port in flow_data:
                    flow = flow_data[dest_port]
                    values = _plot_ss_flow(flow, node, dest_ip, dest_port)
                    if values is not None:
                        all_flow_data.append(
                            {
                                "values": values,
                                "label": f"{node} to {dest_ip}:{dest_port}",
                            }
                        )

                if len(all_flow_data) > 1:

                    x_vals = []
                    labels = []

                    for flow_data in all_flow_data:
                        x_vals.append(flow_data["values"][0])
                        labels.append(flow_data["label"])

                    for param in all_flow_data[0]["values"][1]:
                        y_vals = []
                        for flow_data in all_flow_data:
                            y_vals.append(flow_data["values"][1][param])

                        data = []

                        for i in range(len(labels)):
                            data.append(
                                {"values": (x_vals[i], y_vals[i]), "label": labels[i]}
                            )

                        fig = mix_plot(
                            "Socket Stats (ss)", data, "Time (s)", _get_ylabel(param)
                        )
                        filename = f"{node}_{dest_ip}_{param}.png"
                        Pack.dump_plot("ss", filename, fig)
                        plt.close(fig)
