import ipaddress

from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom, StructuredRel)

from analyzer.models.relation_name import FROM_ADDRESS, TO_ADDRESS

from analyzer.models.node import upsert_decorator

# ----------------------------------------------------------------
# network base structures
# ----------------------------------------------------------------


class Cidr(StructuredNode):
    cidr = StringProperty(unique_index=True, required=True)
    start_ip_int = IntegerProperty()
    end_ip_int = IntegerProperty()
    name = StringProperty()
    security_zone = StringProperty()

    @upsert_decorator("cidr")
    def save(self):
        return super().save()


class IP(StructuredNode):
    ip = StringProperty(unique_index=True, required=True)
    ip_int = IntegerProperty()

    @upsert_decorator("ip")
    def save(self):
        return super().save()


DENY = "deny"
ALLOW = "allow"


class ACL(StructuredNode):
    acl_id = StringProperty(unique_index=True, required=True)
    priority = IntegerProperty()
    last_used = DateTimeProperty()

    from_port = IntegerProperty()
    to_port = IntegerProperty()

    protocol = StringProperty()
    action = StringProperty()

    from_addr = RelationshipFrom(Cidr, FROM_ADDRESS)
    to_addr = RelationshipTo(Cidr, TO_ADDRESS)

    from_ip = RelationshipFrom(IP, FROM_ADDRESS)
    to_ip = RelationshipTo(IP, TO_ADDRESS)

    @upsert_decorator("acl_id")
    def save(self):
        return super().save()


class ACLRel(StructuredRel):
    acl_id = StringProperty()
    priority = IntegerProperty()
    last_used = DateTimeProperty()

    from_port = IntegerProperty()
    to_port = IntegerProperty()

    protocol = StringProperty()
    action = StringProperty()

    from_addr = RelationshipFrom(Cidr, FROM_ADDRESS)
    to_addr = RelationshipTo(Cidr, TO_ADDRESS)

    from_ip = RelationshipFrom(IP, FROM_ADDRESS)
    to_ip = RelationshipTo(IP, TO_ADDRESS)


class PermissionRel(StructuredRel):
    perm_id = StringProperty()
    from_port = IntegerProperty()
    to_port = IntegerProperty()
    protocol = StringProperty()
    action = StringProperty()


class RouteRel(StructuredRel):
    cidr = StringProperty()
    start_ip_int = IntegerProperty()
    end_ip_int = IntegerProperty()


def new_cidr(cidr: str) -> Cidr:
    net = ipaddress.ip_network(cidr)

    return Cidr(
        cidr=cidr,
        start_ip_int=int(net[0]),
        end_ip_int=int(net[-1])
    )


def new_ip(ip: str) -> IP:
    addr = ipaddress.ip_address(ip)
    return IP(
        ip=ip,
        ip_int=int(addr)
    )


def new_route(cidr: str) -> dict:
    net = ipaddress.ip_network(cidr)

    return {
        "cidr": cidr,
        "start_ip_int": int(net[0]),
        "end_ip_int": int(net[-1])
    }
