import boto3

def get_policy_actions(policy_arn):
    """Retrieve all actions from the given AWS managed policy ARN."""
    iam_client = boto3.client('iam')

    # Get default version ID of the policy
    policy_info = iam_client.get_policy(PolicyArn=policy_arn)
    default_version_id = policy_info['Policy']['DefaultVersionId']

    # Get the actual policy version document
    version = iam_client.get_policy_version(
        PolicyArn=policy_arn,
        VersionId=default_version_id
    )
    document = version['PolicyVersion']['Document']

    # Collect all actions from policy statements
    actions = set()
    for statement in document.get('Statement', []):
        action = statement.get('Action', [])
        if isinstance(action, str):
            actions.add(action)
        elif isinstance(action, list):
            actions.update(action)
    return sorted(actions)

def print_policy_actions(policy_name, policy_arn):
    """Prints the actions for a specific policy."""
    print(f"\nPermissions in '{policy_name}':")
    actions = get_policy_actions(policy_arn)
    for act in actions:
        print(act)

def main():
    policies = {
        'SecurityAudit': 'arn:aws:iam::aws:policy/SecurityAudit',
        'ViewOnlyAccess': 'arn:aws:iam::aws:policy/job-function/ViewOnlyAccess'
    }

    for name, arn in policies.items():
        print_policy_actions(name, arn)

if __name__ == '__main__':
    main()
