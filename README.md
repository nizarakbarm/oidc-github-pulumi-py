## Provisioning an OIDC Provider in AWS for GitHub Action using Pulumi

This script is used for provisioning an OIDC provider in AWS for GitHub Action.

I created a reference Python Script based on https://github.com/pulumi/examples/tree/master/aws-py-oidc-provider-pulumi-cloud with a few additions.

### Prerequisites

- Pulumi
- Configure Pulumi to Use AWS
- Install Python 3.x

### How to Deploy

Clone the repository first.

```
git clone https://github.com/nizarakbarm/oidc-github-pulumi-py.git
cd oidc-github-pulumi-py
```

Then you need to depoloy the script by following this steps:

1. Create a new stack:

```
pulumi stack init dev
```

2. Set your desired AWS region:

```
pulumi config set aws:region [region]
```

3. Install requirements:

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

4. Run `pulumi up -y`. After the script execution is completed, you will get arn, role_name, and region that needed for OIDC configuration at GitHub Action.

### Customizing Audience at Trust Policy

If you need to resrict the audience to specific owner, repository, environment. You can check this audience template:

```
            "Condition": {
                "StringLike": {
                    f"{url}:sub": "repo:OWNER/REPOSITORY:environment:NAME"
                    },
                "StringEquals": {
                    f"{url}:aud": audience
                }
            }
```

You can change OWNER to your GitHub account username, REPOSITORY to your repository name, and NAME to the environment of your GitHub Action (production, staging, or development).
