"""An AWS Python Pulumi Program for Creating OIDC for GitHub Actions"""

import pulumi
import pulumi_aws as aws
from pulumi_aws import iam
import requests
import subprocess
import OpenSSL
import json
import yaml

# Define audience, idp_url, and base_url
audience = 'sts.amazonaws.com'
idp_url = 'https://token.actions.githubusercontent.com'
base_url = 'token.actions.githubusercontent.com'

# Create arn for GitHub Actions OIDC
getCallerIdentity = aws.get_caller_identity()
arn = f'arn:aws:iam:{getCallerIdentity.account_id}:oidc-provider/token.actions.githubusercontent.com'



# Run OpenSSL command to get certificates
print("Retrieving certificates...")
command = f'openssl s_client -servername {base_url} -showcerts -connect {base_url}:443'
result = subprocess.run(command, shell=True, capture_output=True, text=True)
certificates = result.stdout.split('-----END CERTIFICATE-----')

#Get the last certificates from the output
last_certificate = certificates[-2] + '-----END CERTIFICATE-----'

# Get thumbprint of certificate
print("Retreiving certificate thumbprint...")
x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, last_certificate)
thumbprint = (x509.digest('sha1').decode()).replace(":","")

# Create an OIDC identity provider
print("Creating OIDC provider....")
oidc_provider = iam.OpenIdConnectProvider("oidcProvider", 
    client_id_lists = [audience],
    thumbprint_lists = [thumbprint],
    url = idp_url
)

# Create an IAM role with a trust policy that trust the OIDC operator
print('Create provider IAM role...')
def create_assume_role_policy(args):
    url, arn, audience = args
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Federated": arn},
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringLike": {
                    f"{url}:sub": "repo:OWNER/*:*"
                    },
                "StringEquals": {
                    f"{url}:aud": audience
                }
            }
        }]
    }
    return json.dumps(policy)

oidc_role = iam.Role("oidcProviderRole",
    assume_role_policy=pulumi.Output.all(oidc_provider.url, oidc_provider.arn, audience).apply(create_assume_role_policy)
)
cur_region = aws.get_region()

print("OIDC configuration complete!")

# Get all information that needed for configuration OIDC at GitHub Action
pulumi.export('arn',oidc_role.arn)
pulumi.export('role_name',oidc_role.name)
pulumi.export('region',cur_region.name)