#### AWS Data Collection Methods
##### AWS API (Boto3)
Supports both standard AWS credentials and SSO.
> If you don't config any credentials, it will use your AWS CLI configuration in `.aws`
```yaml
aws:
    type: "boto3"
    credentials:
    # For SSO authentication
    ssostarturl: "https://your-sso-url.awsapps.com/start/#"
    role: "YourRole"
    regions: ["ap-east-1"]
    # For standard AWS credentials
    aws_access_key_id: "your_access_key"
    aws_secret_access_key: "your_secret_key"
    region: "ap-east-1"
```

##### Local File Analysis
Uses previously exported AWS data if you have set debug
```yaml
aws:
    type: "boto3"
    credentials:
    # For SSO authentication
    ssostarturl: "https://your-sso-url.awsapps.com/start/#"
    role: "YourRole"
    regions: ["ap-east-1"]
    # For standard AWS credentials
    aws_access_key_id: "your_access_key"
    aws_secret_access_key: "your_secret_key"
    regions: ["ap-east-1"]
```
