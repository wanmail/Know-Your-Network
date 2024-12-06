# please use `aws sso login` to get the credentials first

import os
from datetime import datetime

import json

import boto3


class Credential(object):
    def __init__(self, account_id, account_name, access_key, secret_key, session_token):
        self.account_id = account_id
        self.account_name = account_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token


def get_sso_access_token(sso_start_url) -> str:
    cache_dir = os.path.expanduser("~/.aws/sso/cache/")

    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]

    token = None
    for cache_file in cache_files:
        with open(os.path.join(cache_dir, cache_file)) as f:
            data = json.load(f)
            if data.get("startUrl") == sso_start_url:
                expires_at = datetime.fromisoformat(
                    data['expiresAt'].replace('Z', '+00:00'))
                if expires_at > datetime.now(expires_at.tzinfo):
                    token = data["accessToken"]
                    break

    if token is None:
        raise ValueError("SSO access token is None")

    return token


def get_credentials(role_name, token):
    sso = boto3.client("sso")
    for page in sso.get_paginator("list_accounts").paginate(accessToken=token):
        for accounts in page["accountList"]:
            role = role_name
            if role == "":
                role = sso.list_account_roles(
                    accountId=accounts["accountId"],
                    accessToken=token)["roleList"][0]["roleName"]

            response = sso.get_role_credentials(
                roleName=role_name,
                accountId=accounts["accountId"],
                accessToken=token)

            yield Credential(account_id=accounts["accountId"],
                             account_name=accounts["accountName"],
                             access_key=response["roleCredentials"]["accessKeyId"],
                             secret_key=response["roleCredentials"]["secretAccessKey"],
                             session_token=response["roleCredentials"]["sessionToken"])
