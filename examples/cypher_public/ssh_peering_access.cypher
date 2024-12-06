MATCH (src:ENI) - [:`with_policy`] - (sg:SecurityGroup) - [i:ingress] - (c:Cidr)
WHERE i.`from_port`=22

MATCH (src:ENI) - [:`ip_assigned`] - (sip:IP)

MATCH (src:ENI) - [:`belong_to`] - (v:VPC)

MATCH (dst:ENI) - [:`ip_assigned`] - (dip:IP)
WHERE c.`start_ip_int` <= dip.`ip_int` AND c.`end_ip_int` >=dip.`ip_int`

MATCH (dst:ENI) - [:`belong_to`] - (:Subnet) - [:`route_to`] - (:`EC2RouteTable`) - [rt:`route_to`] - (:PeeringConnection) - [:peering] - (v:VPC)
WHERE rt.`start_ip_int`<=sip.`ip_int` AND rt.`end_ip_int`>=sip.`ip_int`

// WITH COUNT(src) AS managed_count, dst
// WHERE managed_count > 1

// ORDER BY managed_count DESC
// LIMIT 30

// RETURN dst.`resource_id`, dst.`private_ip_addr`, dst.`owner_id`, managed_count

RETURN src,dst