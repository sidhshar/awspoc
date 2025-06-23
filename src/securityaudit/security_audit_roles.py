import boto3
from botocore.exceptions import ClientError

def get_current_identity():
    sts = boto3.client("sts")
    identity = sts.get_caller_identity()
    print("Current IAM Identity:")
    print(f"  Account: {identity['Account']}")
    print(f"  ARN:     {identity['Arn']}")
    print(f"  UserId:  {identity['UserId']}")
    return identity['Arn']

def get_iam_details(arn):
    iam = boto3.client("iam")

    if ":user/" in arn:
        user_name = arn.split("/")[-1]
        print(f"\n[+] User: {user_name}")
        try:
            response = iam.list_attached_user_policies(UserName=user_name)
            print("  Attached User Policies:")
            for policy in response['AttachedPolicies']:
                print(f"    - {policy['PolicyName']}")
            
            groups = iam.list_groups_for_user(UserName=user_name)
            print("  Groups and Their Policies:")
            for group in groups['Groups']:
                print(f"    - Group: {group['GroupName']}")
                gp_policies = iam.list_attached_group_policies(GroupName=group['GroupName'])
                for policy in gp_policies['AttachedPolicies']:
                    print(f"      * Policy: {policy['PolicyName']}")
        except ClientError as e:
            print(f"  Error: {e}")

    elif ":role/" in arn:
        role_name = arn.split("/")[-1]
        print(f"\n[+] Role: {role_name}")
        try:
            response = iam.list_attached_role_policies(RoleName=role_name)
            print("  Attached Role Policies:")
            for policy in response['AttachedPolicies']:
                print(f"    - {policy['PolicyName']}")
        except ClientError as e:
            print(f"  Error: {e}")
    else:
        print("\n[!] Unable to determine if the ARN is a user or role.")

if __name__ == "__main__":
    arn = get_current_identity()
    get_iam_details(arn)
