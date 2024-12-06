
from analyzer.models.network import new_cidr, new_ip, new_route, ALLOW, DENY
from analyzer.models.aws import AWSNode, VPC, Subnet, \
    EC2RouteTable, PeeringConnection, ENI, SecurityGroup, PrefixList, \
    TGW, TGWAttachment, TGWRouteTable

import logging

from mypy_boto3_ec2.type_defs import VpcTypeDef, SubnetTypeDef, TagTypeDef, \
    VpcPeeringConnectionTypeDef, NetworkInterfaceTypeDef, SecurityGroupTypeDef, \
    RouteTableTypeDef, \
    TransitGatewayAttachmentTypeDef, TransitGatewayTypeDef, TransitGatewayRouteTableTypeDef

from mypy_boto3_ec2.client import EC2Client


def parse_tags(tags: TagTypeDef):
    l = []
    name = ""

    for tag in tags:
        if tag["Key"] == "Name":
            name = tag["Value"]
        else:
            l.append("{}={}".format(tag["Key"], tag["Value"]))

    return name, l

# refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_vpc_peering_connections.html


def parse_peering(data: VpcPeeringConnectionTypeDef):
    name, tags = parse_tags(data.get("Tags", []))
    peering = PeeringConnection(
        resource_id=data["VpcPeeringConnectionId"],
        resource_name=name,
        state=data["Status"]["Code"],
        tags=tags
    ).save()

    vpc1 = VPC(
        resource_id=data["AccepterVpcInfo"]["VpcId"],
        region=data["AccepterVpcInfo"]["Region"],
        owner_id=data["AccepterVpcInfo"]["OwnerId"]).save()

    # vpc1_net = new_cidr(data["AccepterVpcInfo"]["CidrBlock"]).save()
    # vpc1.cidr.connect(vpc1_net)

    vpc2 = VPC(
        resource_id=data["RequesterVpcInfo"]["VpcId"],
        region=data["RequesterVpcInfo"]["Region"],
        owner_id=data["RequesterVpcInfo"]["OwnerId"]).save()
    # vpc2_net = new_cidr(data["RequesterVpcInfo"]["CidrBlock"]).save()
    # vpc2.cidr.connect(vpc2_net)

    peering.accepter.connect(vpc1)
    peering.requester.connect(vpc2)


# refer to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_vpcs.html
def parse_vpc(data: VpcTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    vpc = VPC(
        resource_id=data["VpcId"],
        owner_id=data["OwnerId"],
        resource_name=name,
        cidr_block=data["CidrBlock"],
        state=data["State"],
        tags=tags).save()

    net = new_cidr(data["CidrBlock"]).save()

    vpc.cidr.connect(net)


def parse_subnet(data: SubnetTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    subnet = Subnet(
        resource_id=data["SubnetId"],
        owner_id=data["OwnerId"],
        availability_zone=data["AvailabilityZone"],
        state=data["State"],
        resource_name=name,
        cidr_block=data["CidrBlock"],
        tags=tags).save()

    net = new_cidr(data["CidrBlock"]).save()

    subnet.cidr.connect(net)

    vpc = VPC(resource_id=data["VpcId"]).save()

    subnet.vpc.connect(vpc)


def parse_ec2_route(data: RouteTableTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    rtb = EC2RouteTable(
        resource_id=data["RouteTableId"],
        owner_id=data["OwnerId"],
        resource_name=name,
        tags=tags).save()

    vpc = VPC(resource_id=data["VpcId"]).save()
    rtb.vpc.connect(vpc)

    for rt in data.get("Routes", []):
        cidr = rt.get("DestinationCidrBlock")
        if cidr == None or cidr == "":
            logging.info(f"No destination cidr block found for route table {data['RouteTableId']}")
            continue

        route = new_route(cidr)

        gatewayId = rt.get("GatewayId", "")
        if gatewayId != "":
            if gatewayId == "local":
                rtb.route_to_gateway.connect(vpc, route)
            else:
                node = AWSNode(
                    resource_id=gatewayId
                ).save()
                rtb.route_to_gateway.connect(node, route)
            continue

        # connect to transit gateway attachment
        tgwId = rt.get("TransitGatewayId", "")
        if tgwId != "":
            # resp = client.describe_transit_gateway_attachments(
            #     Filters=[
            #         {
            #             "Name": "resource-id",
            #             "Values": [data["VpcId"]]
            #         }
            #     ]
            # )

            # if resp["TransitGatewayAttachments"] == []:
            #     logging.info(f"No attachment found for route table {
            #                  data['RouteTableId']}")
            #     continue

            # node = TGWAttachment(
            #     resource_id=resp["TransitGatewayAttachments"][0]["TransitGatewayAttachmentId"]
            # ).save()
            # rtb.route_to_tgw.connect(node, route)

            node = TGW(
                resource_id=tgwId
            ).save()
            rtb.route_to_tgw.connect(node, route)
            continue

        peeringId = rt.get("VpcPeeringConnectionId", "")
        if peeringId != "":
            # resp = client.describe_vpc_peering_connections(
            #     VpcPeeringConnectionIds=[peeringId]
            # )
            # if resp["VpcPeeringConnections"] == []:
            #     logging.info(f"No peering connection found for route table {
            #                  data['RouteTableId']}")
            #     continue

            # peering = resp["VpcPeeringConnections"][0]

            # if peering["AccepterVpcInfo"]["VpcId"] == data["VpcId"]:
            #     node = VPC(
            #         resource_id=peering["RequesterVpcInfo"]["VpcId"]).save()
            # else:
            #     node = VPC(
            #         resource_id=peering["AccepterVpcInfo"]["VpcId"]).save()
            node = PeeringConnection(resource_id=peeringId).save()
            rtb.route_to_peering.connect(node, route)
            continue

        logging.info(f"Unsupported route type for route table {data['RouteTableId']}")

    for association in data.get("Associations", []):
        if association["Main"] == True:
            vpc.route.connect(rtb)
            continue

        subnetId = association.get("SubnetId", "")
        if subnetId == "":
            logging.info(f"No subnet id found for route table {data['RouteTableId']}")
            continue

        subnet = Subnet(resource_id=subnetId).save()
        subnet.route.connect(rtb)


def parse_eni(data: NetworkInterfaceTypeDef):
    name, tags = parse_tags(data.get("TagSet", []))

    eni = ENI(
        resource_id=data["NetworkInterfaceId"],
        owner_id=data["OwnerId"],
        availability_zone=data["AvailabilityZone"],
        state=data["Status"],
        private_ip_addr=data["PrivateIpAddress"],
        public_ip_addr=data.get("Association", {}).get("PublicIp", ""),
        interface_type=data["InterfaceType"],
        mac_address=data["MacAddress"],
        resource_name=name,
        tags=tags
    ).save()

    private_ip = new_ip(data["PrivateIpAddress"]).save()
    eni.private_ip.connect(private_ip)

    pub = data.get("Association", {}).get("PublicIp", "")
    if pub != "":
        public_ip = new_ip(pub).save()
        eni.public_ip.connect(public_ip)

    subnet = Subnet(resource_id=data["SubnetId"]).save()
    eni.subnet.connect(subnet)

    vpc = VPC(resource_id=data["VpcId"]).save()
    eni.vpc.connect(vpc)

    for sg in data.get("Groups", []):
        sg = SecurityGroup(resource_id=sg["GroupId"]).save()
        eni.security_group.connect(sg)


def parse_sg(data: SecurityGroupTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    sg = SecurityGroup(
        resource_id=data["GroupId"],
        owner_id=data["OwnerId"],
        resource_name=name,
        tags=tags).save()

    vpc = VPC(resource_id=data["VpcId"]).save()
    sg.vpc.connect(vpc)

    for i, perm in enumerate(data.get("IpPermissions", [])):
        rel = {
            "from_port": perm.get("FromPort", 0),
            "to_port": perm.get("ToPort", 0),
            "protocol": perm.get("IpProtocol", ""),
            "perm_id": f"{i}",
            "action": ALLOW
        }

        if len(perm["UserIdGroupPairs"]) > 0:
            for pair in perm["UserIdGroupPairs"]:
                if pair["GroupId"] == data["GroupId"]:
                    sg.ingress_security_group.connect(sg, rel)
                    continue
                sg2 = SecurityGroup(resource_id=pair["GroupId"]).save()
                sg.ingress_security_group.connect(sg2, rel)

        if len(perm["IpRanges"]) > 0:
            for r in perm["IpRanges"]:
                cidr = new_cidr(r["CidrIp"]).save()
                sg.ingress_cidr.connect(cidr, rel)

        if len(perm["Ipv6Ranges"]) > 0:
            logging.info(f"IPv6 range found for security group {data['GroupId']}")

        if len(perm["PrefixListIds"]) > 0:
            for p in perm["PrefixListIds"]:
                pl = PrefixList(resource_id=p["PrefixListId"]).save()
                sg.ingress_prefix_list.connect(pl, rel)

    for i, perm in enumerate(data.get("IpPermissionsEgress", [])):
        rel = {
            "from_port": perm.get("FromPort", 0),
            "to_port": perm.get("ToPort", 0),
            "protocol": perm.get("IpProtocol", ""),
            "perm_id": f"{i}",
            "action": ALLOW
        }

        if len(perm["UserIdGroupPairs"]) > 0:
            for pair in perm["UserIdGroupPairs"]:
                sg2 = SecurityGroup(resource_id=pair["GroupId"]).save()
                sg.egress_security_group.connect(sg2, rel)

        if len(perm["IpRanges"]) > 0:
            for r in perm["IpRanges"]:
                cidr = new_cidr(r["CidrIp"]).save()
                sg.egress_cidr.connect(cidr, rel)

        if len(perm["PrefixListIds"]) > 0:
            for p in perm["PrefixListIds"]:
                pl = PrefixList(resource_id=p["PrefixListId"]).save()
                sg.egress_prefix_list.connect(pl, rel)


def parse_tgw(data: TransitGatewayTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    TGW(
        resource_id=data["TransitGatewayId"],
        owner_id=data["OwnerId"],
        resource_name=name,
        state=data["State"],
        tags=tags).save()


def parse_tgw_attachment(data: TransitGatewayAttachmentTypeDef):
    name, tags = parse_tags(data.get("Tags", []))

    attachment = TGWAttachment(
        resource_id=data["TransitGatewayAttachmentId"],
        owner_id=data["TransitGatewayOwnerId"],
        resource_name=name,
        state=data["State"],
        tags=tags).save()

    tgw = TGW(resource_id=data["TransitGatewayId"]).save()
    attachment.belong_to.connect(tgw)

    # "connect", "direct-connect-gateway", "peering", "tgw-peering", "vpc", "vpn"
    t = data.get("ResourceType", "")

    if t == "vpc":
        vpc = VPC(resource_id=data["ResourceId"],
                  owner_id=data["ResourceOwnerId"]).save()
        attachment.attach_to_vpc.connect(vpc)
    elif t == "vpn":
        vpn = AWSNode(resource_id=data["ResourceId"],
                      owner_id=data["ResourceOwnerId"]).save()
        attachment.attach_to_vpn.connect(vpn)
    else:
        logging.info(f"Unsupported resource type for attachment {data['TransitGatewayAttachmentId']}")

    rtb = TGWRouteTable(
        resource_id=data["Association"]["TransitGatewayRouteTableId"]).save()
    attachment.route_to.connect(rtb)


def parse_tgw_rtb(data: TransitGatewayRouteTableTypeDef, client: EC2Client):
    name, tags = parse_tags(data.get("Tags", []))

    rtb = TGWRouteTable(
        resource_id=data["TransitGatewayRouteTableId"],
        resource_name=name,
        state=data["State"],
        tags=tags).save()

    resp = client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=data["TransitGatewayRouteTableId"],
        Filters=[
            {
                'Name': 'state',
                        'Values': [
                            'active',
                        ]
            },
        ]
    )

    for route in resp["Routes"]:
        cidr = route.get("DestinationCidrBlock")
        if cidr == None or cidr == "":
            logging.info(f"No destination cidr block found for route table {data['Association']['TransitGatewayRouteTableId']}")
            continue

        rel = new_route(cidr)

        for target in route.get("TransitGatewayAttachments", []):
            attachment = TGWAttachment(
                resource_id=target["TransitGatewayAttachmentId"]).save()

            rtb.route_to.connect(attachment, rel)
