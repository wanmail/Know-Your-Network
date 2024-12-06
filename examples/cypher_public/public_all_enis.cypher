MATCH (e:ENI) - [:`belong_to`] - (s:Subnet)
WHERE e.public_ip_addr IS NOT NULL AND e.public_ip_addr <> ''

MATCH (e) - [:`with_policy`] - (:SecurityGroup) - [i:ingress] - (c:Cidr)
WHERE c.cidr='0.0.0.0/0'
// AND i.`from_port`=i.`to_port`
// AND NOT (i.`from_port`=80 OR i.`from_port`=443 OR i.`from_port`=-1)
RETURN e.`resource_id` AS eni_id, e.`resource_name` AS eni_name, e.`owner_id` AS account_id,
    i.`from_port` AS from_port, i.`to_port` AS to_port, e.`private_ip_addr` AS private_ip, e.`public_ip_addr` AS public_ip, 
    s.`resource_id` AS subnet_id, s.`resource_name` AS subnet_name