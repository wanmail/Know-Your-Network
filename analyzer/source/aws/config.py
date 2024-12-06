
import boto3

from mypy_boto3_ec2.client import EC2Client

from analyzer.source.aws import local
from analyzer.source.aws import api
from analyzer.source.aws import sso



def collect_boto3(client: EC2Client, suffix: str = "", debug: bool = False):
    if debug:
        api.get_vpcs(
            client, f"{local.EXPORT_DIR}/{local.VPC}{suffix}.json")
        api.get_subnets(
            client, f"{local.EXPORT_DIR}/{local.SUBNET}{suffix}.json")
        api.get_peerings(
            client, f"{local.EXPORT_DIR}/{local.PEERING}{suffix}.json")
        api.get_ec2_route_tables(
            client, f"{local.EXPORT_DIR}/{local.EC2_ROUTE}{suffix}.json")
        api.get_enis(
            client, f"{local.EXPORT_DIR}/{local.ENI}{suffix}.json")
        api.get_security_groups(
            client, f"{local.EXPORT_DIR}/{local.SECURITY_GROUP}{suffix}.json")
        api.get_tgws(
            client, f"{local.EXPORT_DIR}/{local.TGW}{suffix}.json")
        api.get_tgw_attachments(
            client, f"{local.EXPORT_DIR}/{local.TGW_ATTACHMENT}{suffix}.json")
        api.get_tgw_rtbs(
            client, f"{local.EXPORT_DIR}/{local.TGW_RTB}{suffix}.json")
    else:
        api.get_vpcs(client)
        api.get_subnets(client)
        api.get_peerings(client)
        api.get_ec2_route_tables(client)
        api.get_enis(client)
        api.get_security_groups(client)
        api.get_tgws(client)
        api.get_tgw_attachments(client)
        api.get_tgw_rtbs(client)


def collect_local():
    local.load_vpcs()
    local.load_subnets()
    local.load_peerings()
    local.load_ec2_route_tables()
    local.load_enis()
    local.load_security_groups()
    local.load_tgws()
    local.load_tgw_attachments()
    # local.load_tgw_rtbs()


def collect(config: dict, debug: bool = False):
    typ = config.get('type')

    if typ == 'local':
        collect_local()
        return

    credentials = config.get('credentials', {})

    if typ == 'configservice':
        pass
    if typ == 'configserviceS3':
        pass
    elif typ == 'boto3':
        if credentials.get("ssostarturl"):
            token = sso.get_sso_access_token(credentials.get("ssostarturl"))
            for credential in sso.get_credentials(credentials.get("role"), token):
                for region in credentials.get("regions", []):
                    client = boto3.client('ec2', region_name=region, aws_access_key_id=credential.access_key,
                                          aws_secret_access_key=credential.secret_key, aws_session_token=credential.session_token)
                    try:
                        collect_boto3(
                            client, suffix=f"-{credential.account_id}-{region}", debug=debug)
                    except Exception as e:
                        print(
                            f"Error in {credential.account_id}-{credential.account_name} {region}: {e}")
            return
        session = boto3.Session(**credentials)
        client = session.client('ec2')
        collect_boto3(client, debug=debug)
        return
    else:
        raise ValueError(f"Unknown type {typ}")
