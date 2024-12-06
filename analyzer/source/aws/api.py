import json
from analyzer.source.aws import parse

import logging

from mypy_boto3_ec2.client import EC2Client


def get_vpcs(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_vpcs").paginate(
        Filters=[{
            'Name': 'state',
            'Values': [
                'available',
            ]
        }]
    ):
        for vpc in page["Vpcs"]:
            if output != "":
                data.append(vpc)
            try:
                parse.parse_vpc(vpc)
            except Exception as e:
                logging.error(f"Error in {vpc['VpcId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_subnets(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_subnets").paginate():
        for subnet in page["Subnets"]:
            if output != "":
                data.append(subnet)
            try:
                parse.parse_subnet(subnet)
            except Exception as e:
                logging.error(f"Error in {subnet['SubnetId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_peerings(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_vpc_peering_connections").paginate():
        for peering in page["VpcPeeringConnections"]:
            if output != "":
                data.append(peering)
            try:
                parse.parse_peering(peering)
            except Exception as e:
                logging.error(
                    f"Error in {peering['VpcPeeringConnectionId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_ec2_route_tables(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_route_tables").paginate():
        for route_table in page["RouteTables"]:
            if output != "":
                data.append(route_table)
            try:
                parse.parse_ec2_route(route_table)
            except Exception as e:
                logging.error(f"Error in {route_table['RouteTableId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_security_groups(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_security_groups").paginate():
        for sg in page["SecurityGroups"]:
            if output != "":
                data.append(sg)
            try:
                parse.parse_sg(sg)
            except Exception as e:
                logging.error(f"Error in {sg['GroupId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_enis(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_network_interfaces").paginate():
        for eni in page["NetworkInterfaces"]:
            if output != "":
                data.append(eni)
            try:
                parse.parse_eni(eni)
            except Exception as e:
                logging.error(f"Error in {eni['NetworkInterfaceId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_tgws(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_transit_gateways").paginate():
        for tgw in page["TransitGateways"]:
            if output != "":
                data.append(tgw)
            try:
                parse.parse_tgw(tgw)
            except Exception as e:
                logging.error(f"Error in {tgw['TransitGatewayId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_tgw_attachments(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_transit_gateway_attachments").paginate():
        for attachment in page["TransitGatewayAttachments"]:
            if output != "":
                data.append(attachment)
            try:
                parse.parse_tgw_attachment(attachment)
            except Exception as e:
                logging.error(
                    f"Error in {attachment['TransitGatewayAttachmentId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)


def get_tgw_rtbs(client: EC2Client, output: str = "") -> None:
    data = []

    for page in client.get_paginator("describe_transit_gateway_route_tables").paginate():
        for rtb in page["TransitGatewayRouteTables"]:
            if output != "":
                data.append(rtb)
            try:
                parse.parse_tgw_rtb(rtb, client)
            except Exception as e:
                logging.error(
                    f"Error in {rtb['TransitGatewayRouteTableId']}, {e}")

    if len(data) != 0:
        with open(output, "w") as f:
            json.dump(data, f, default=str)
