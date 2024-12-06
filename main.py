import argparse
from analyzer.source.aws.config import collect as collect_aws
import yaml
import boto3
from neomodel import config as neo_config
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Network Analyzer')

    parser.add_argument('--config', type=str, help='Path to the configuration file',
                        default="config.yml", required=False)

    args = parser.parse_args()

    config = load_config(args.config)

    db = config.get('neo4j', "")
    if db == "":
        db = f'bolt://{os.environ.get("NEO4J_USER","neo4j")}:{os.environ.get("NEO4J_PASSWORD","neo4j")}@neo4j:7687'

    neo_config.DATABASE_URL = db

    debug = config.get('debug', False)
    
    if config.get('aws'):
        collect_aws(config.get('aws'), debug)
