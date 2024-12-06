# Know Your Network

When you join a new company, you will be faced with a complex network architecture left over from history. How to quickly sort out the network architecture and transform it according to the principles of zero trust?

This is a comprehensive tool for analyzing and visualizing hybrid network architectures across multiple cloud providers, accounts, and on-premise data centers. This tool leverages Neo4j graph database to provide insights into complex network relationships and configurations.

## Why Not?
### AWS Reachability Analyzer
Reachability Analyzer can help us to [discover network paths across multiple AWS Regions](https://aws.amazon.com/cn/blogs/networking-and-content-delivery/using-vpc-reachability-analyzer-to-discover-network-paths-across-multiple-aws-regions/).

However, it does not support cross-account and multi-cloud environments.

But we can use its network path to design `neo4j relationships`.

![alt text](./docs/image/reachability-analyzer.png "https://aws.amazon.com/cn/blogs/networking-and-content-delivery/using-vpc-reachability-analyzer-to-discover-network-paths-across-multiple-aws-regions/")

### cartography
[cartography](https://github.com/cartography-cncf/cartography) can help us to consolidates infrastructure assets and the relationships.

However, it does not include network relationships, such as routing tables, ACLs, security groups, etc.


## Features

- Network relationship mapping
- Graph-based network analysis
- Support for multiple resources:
  - AWS
    - VPCs
    - Subnets
    - Network Interfaces (ENIs)
    - Security Groups
    - Transit Gateways
    - VPC Peering Connections
    - Route Tables
    - NACL (TODO)
    - ELB (TODO)
    - Prefix lists (TODO)
    - VPN/Direct Connect (TODO)
    - Route53 (TODO)
  - Fortigate(TODO)
    - IP Addresses
    - Firewall Policies
    - Ipsec tunnels
  - Cloudflare(TODO)
- Support for multiple resource collect methods:
  - AWS
    - API
      - Boto3 Common authentication
      - AWS SSO authentication
    - Config Service(TODO)
      - API collect
      - S3 snapshot collect
  
## How to Use

### Prerequisites
- Docker and Docker Compose
- AWS credentials (if collecting AWS data)
- Python 3.9+ (if running locally)

### Quick Start with Docker
1. Clone the repository
```
git clone https://github.com/wanmail/Know-Your-Network.git
```

2. Create `.env` file with Neo4j credentials
```
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
```

3. Configure your data source in `config.yml`,  see [Configuration Options](#Configuration)

4. Start the services
```
docker-compose up -d
```

5. Access Neo4j browser at http://localhost:7474 to query your network data

6. Start analyzer every time
```
docker-compose up -d analyzer
```

7. Start analyzer in dev mode(Please uncomment in `docker-compose.yml` first)
```
docker-compose up -d analyzer-dev
```

### Local Installation

1. Install dependencies
```
pip install -r requirements.txt
```

2. Install Neo4j labels
```
neomodel_install_labels analyzer.models.network analyzer.models.aws {neo4j_url}
```

1. Configure your data source and neo4j in `config.yml` , see [Configuration Options](#Configuration)

2. Run the analyzer
```
python main.py
```

<a name="Configuration"></a>
### Configuration Options

```yaml
# If set debug, API call will save response in `export` directory, and you can load data directly from local instead of pulling it through API.
debug: true

# neo4j url
neo4j: "bolt://neo4j:neo4j@localhost:7687"

# Data source config
```
- [AWS Source](./docs/aws.md)

## Example Cypher
Refer to `examples` directory.

### Discover vpc peering connect
```
MATCH p=()-[r:peering]->() RETURN p limit 25
```

![alt text](./docs/image/peering.png)

### Discover tgw connect
```
MATCH (t:TGW) <- [:belong_to] - (a:TGWAttachment) - [:tgw_attach]-(v:VPC) RETURN t,a,v limit 25
```
![alt text](./docs/image/tgw.png)

### Find public eni
Which has a public ip address and security group has a ingress permission to internet address. 

```
MATCH (e:ENI) 
WHERE e.public_ip_addr IS NOT NULL AND e.public_ip_addr <> ''

MATCH (e) - [:`with_policy`] - (:SecurityGroup) - [i:ingress] - (c:Cidr)
WHERE NOT ( (c.`start_ip_int`>=167772160 AND c.`start_ip_int` <= 184549375)
OR (c.`start_ip_int`>=2886729728 AND c.`start_ip_int` <= 2887778303)
OR (c.`start_ip_int`>=3232235520 AND c.`start_ip_int` <= 3232301055))
// AND NOT (c.`start_ip_int` = c.`end_ip_int`) 

RETURN e limit 25
```

### Find SSH access via VPC peering
```
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

RETURN src,dst limit 25
```

> Please note that the `src` here refers to the `src` we started querying instead of the `src` accessed by the network. We start from the ingress rule, so `src` refers to the accessed eni, and `dst` refers to the visitor.
> That means, `dst` -> 22 -> `src` .