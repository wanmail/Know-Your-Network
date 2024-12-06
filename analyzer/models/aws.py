from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, ArrayProperty, BooleanProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom, StructuredRel)

from analyzer.models.network import Cidr, IP, ACL, RouteRel, PermissionRel

from analyzer.models.relation_name import ROUTE_TO, BELONG_TO, HAS, CIDR_ASSIGNED, IP_ASSIGNED, WITH_POLICY, PEERING, TGW_ATTACH, INGRESS, EGRESS

from analyzer.models.node import upsert_decorator

# ----------------------------------------------------------------
# AWS base structures
# ----------------------------------------------------------------


class AWSNode(StructuredNode):
    resource_id = StringProperty(unique_index=True, required=True)
    resource_type = StringProperty()
    resource_name = StringProperty()

    arn = StringProperty()

    state = StringProperty()

    owner_id = StringProperty()
    region = StringProperty()
    availability_zone = StringProperty()

    created_at = DateTimeProperty()

    tags = ArrayProperty()

    @upsert_decorator("resource_id")
    def save(self):
        return super().save()


# ----------------------------------------------------------------
# AWS network structures
# Refer to https://aws.amazon.com/cn/blogs/networking-and-content-delivery/using-vpc-reachability-analyzer-to-discover-network-paths-across-multiple-aws-regions/
# ENI(SG) -> Subnet/VPC(NACL) -> VPC Peering/TGW(EC2 RouteTable) -> Subnet/VPC(NACL) -> ENI(SG)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# TGW
class TGWAttachment(AWSNode):
    route_to = RelationshipTo("TGWRouteTable", ROUTE_TO, model=RouteRel)
    belong_to = RelationshipTo("TGW", BELONG_TO)

    attach_to_vpc = RelationshipTo("VPC", TGW_ATTACH)
    attach_to_vpn = RelationshipTo(AWSNode, TGW_ATTACH)


class TGW(AWSNode):
    contain = RelationshipTo("TGWAttachment", HAS)


class TGWRouteTable(AWSNode):
    route_to = RelationshipTo("TGWAttachment", ROUTE_TO, model=RouteRel)
    belong_to = RelationshipTo("TGW", BELONG_TO)

# ----------------------------------------------------------------


# ----------------------------------------------------------------
# VPC
class NACL(AWSNode):
    ingress = RelationshipTo(Cidr, INGRESS, model=PermissionRel)
    egress = RelationshipTo(Cidr, EGRESS, model=PermissionRel)


class VPC(AWSNode):
    cidr_block = StringProperty()

    cidr = RelationshipTo(Cidr, CIDR_ASSIGNED)
    tgw_attach = RelationshipTo("TGWAttachment", TGW_ATTACH)

    route = RelationshipTo("EC2RouteTable", ROUTE_TO)


class Subnet(AWSNode):
    # MapPublicIpOnLaunch = BooleanProperty()
    # AvailableIpAddressCount = IntegerProperty()

    cidr_block = StringProperty()

    cidr = RelationshipTo(Cidr, CIDR_ASSIGNED)

    vpc = RelationshipTo(VPC, BELONG_TO)

    with_nacl = RelationshipTo(NACL, WITH_POLICY)

    route = RelationshipTo("EC2RouteTable", ROUTE_TO)


class PeeringConnection(AWSNode):
    accepter = RelationshipTo("VPC", PEERING)
    requester = RelationshipTo("VPC", PEERING)


class EC2RouteTable(AWSNode):
    route_to_peering = RelationshipTo(
        "PeeringConnection", ROUTE_TO, model=RouteRel)
    route_to_tgw = RelationshipTo(
        "TGW", ROUTE_TO, model=RouteRel)

    route_to_gateway = RelationshipTo(AWSNode, ROUTE_TO, model=RouteRel)

    vpc = RelationshipTo(VPC, BELONG_TO)

# ----------------------------------------------------------------


# ----------------------------------------------------------------
# Security Group
class SecurityGroup(AWSNode):
    ingress_cidr = RelationshipTo(Cidr, INGRESS, model=PermissionRel)
    ingress_security_group = RelationshipTo(
        "SecurityGroup", INGRESS, model=PermissionRel)
    ingress_prefix_list = RelationshipTo(
        "PrefixList", INGRESS, model=PermissionRel)

    egress_cidr = RelationshipTo(Cidr, EGRESS, model=PermissionRel)
    egress_security_group = RelationshipTo(
        "SecurityGroup", EGRESS, model=PermissionRel)
    egress_prefix_list = RelationshipTo(
        "PrefixList", EGRESS, model=PermissionRel)

    vpc = RelationshipTo("VPC", BELONG_TO)
# ----------------------------------------------------------------


# ----------------------------------------------------------------
# Prefix List / VPC Endpoint
class VPCEndpoint(AWSNode):
    service_name = StringProperty()


class PrefixList(AWSNode):
    contain = RelationshipTo(Cidr, HAS)


# ----------------------------------------------------------------
# ENI
class ENI(AWSNode):
    interface_type = StringProperty()
    mac_address = StringProperty()

    private_ip_addr = StringProperty()
    public_ip_addr = StringProperty()

    private_ip = RelationshipTo(IP, IP_ASSIGNED)
    public_ip = RelationshipTo(IP, IP_ASSIGNED)

    subnet = RelationshipTo(Subnet, BELONG_TO)
    vpc = RelationshipTo(VPC, BELONG_TO)
    security_group = RelationshipTo(SecurityGroup, WITH_POLICY)

# ----------------------------------------------------------------

# ----------------------------------------------------------------
# ELB


class TargetGroup(AWSNode):
    pass
# ----------------------------------------------------------------
