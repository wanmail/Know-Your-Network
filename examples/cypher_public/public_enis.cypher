MATCH (e:ENI) 
WHERE e.public_ip_addr IS NOT NULL AND e.public_ip_addr <> ''

MATCH (e) - [:`with_policy`] - (:SecurityGroup) - [i:ingress] - (c:Cidr)
WHERE NOT ( (c.`start_ip_int`>=167772160 AND c.`start_ip_int` <= 184549375)
OR (c.`start_ip_int`>=2886729728 AND c.`start_ip_int` <= 2887778303)
OR (c.`start_ip_int`>=3232235520 AND c.`start_ip_int` <= 3232301055))
// AND NOT (c.`start_ip_int` = c.`end_ip_int`) 

RETURN e