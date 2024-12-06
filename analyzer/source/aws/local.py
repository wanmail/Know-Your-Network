import os
import json

from analyzer.source.aws import parse

from mypy_boto3_ec2.client import EC2Client

EXPORT_DIR = "./export"

VPC = "vpcs"
SUBNET = "subnets"
PEERING = "peerings"
EC2_ROUTE = "route_tables"
ENI = "enis"
SECURITY_GROUP = "security_groups"
TGW = "tgws"
TGW_ATTACHMENT = "tgw_attachments"
TGW_RTB = "tgw_route_tables"


def load(resource):
    for fn in os.listdir(EXPORT_DIR):
        if fn.endswith(".json") and fn.startswith(resource):
            with open(os.path.join(EXPORT_DIR, fn)) as f:
                data = json.load(f)
                for item in data:
                    yield item


def load_ec2_route_tables():
    for data in load(EC2_ROUTE):
        parse.parse_ec2_route(data)


def load_vpcs():
    for data in load(VPC):
        parse.parse_vpc(data)


def load_enis():
    for data in load(ENI):
        parse.parse_eni(data)


def load_subnets():
    for data in load(SUBNET):
        parse.parse_subnet(data)


def load_peerings():
    for data in load(PEERING):
        parse.parse_peering(data)


def load_security_groups():
    for data in load(SECURITY_GROUP):
        parse.parse_sg(data)


def load_tgws():
    for data in load(TGW):
        parse.parse_tgw(data)


def load_tgw_attachments():
    for data in load(TGW_ATTACHMENT):
        parse.parse_tgw_attachment(data)


def load_tgw_rtbs(client: EC2Client):
    for data in load(TGW_RTB):
        parse.parse_tgw_rtb(data, client)
