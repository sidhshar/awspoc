import boto3
import csv
from botocore.exceptions import ClientError

def get_all_regions_dynamic():
    """Fetch all AWS regions where EC2 is available."""
    ec2 = boto3.client("ec2", region_name="us-east-1")  # Any global region works
    regions = ec2.describe_regions()["Regions"]
    return [region["RegionName"] for region in regions]

def get_all_regions():
    """Return a hardcoded list of all commercial AWS regions (excluding GovCloud and China)."""
    return [
        "us-east-1",       # N. Virginia
        "us-east-2",       # Ohio
        "us-west-1",       # N. California
        "us-west-2",       # Oregon
        "af-south-1",      # Cape Town
        "ap-east-1",       # Hong Kong
        "ap-south-1",      # Mumbai
        "ap-south-2",      # Hyderabad
        "ap-southeast-1",  # Singapore
        "ap-southeast-2",  # Sydney
        "ap-southeast-3",  # Jakarta
        "ap-southeast-4",  # Melbourne
        "ap-northeast-1",  # Tokyo
        "ap-northeast-2",  # Seoul
        "ap-northeast-3",  # Osaka
        "ca-central-1",    # Canada Central
        "eu-central-1",    # Frankfurt
        "eu-central-2",    # Zurich
        "eu-west-1",       # Ireland
        "eu-west-2",       # London
        "eu-west-3",       # Paris
        "eu-north-1",      # Stockholm
        "eu-south-1",      # Milan
        "eu-south-2",      # Spain
        "il-central-1",    # Tel Aviv
        "me-south-1",      # Bahrain
        "me-central-1",    # UAE
        "sa-east-1"        # São Paulo
    ]


def get_resources_in_region(region):
    """Fetch all resources in a given region using the Resource Groups Tagging API."""
    print(f"Scanning region: {region}")
    session = boto3.session.Session(region_name=region)
    client = session.client("resourcegroupstaggingapi")

    all_resources = []

    try:
        paginator = client.get_paginator("get_resources")
        for page in paginator.paginate(ResourcesPerPage=50):
            for resource in page["ResourceTagMappingList"]:
                resource_data = {
                    "Region": region,
                    "ResourceARN": resource["ResourceARN"],
                    "Tags": ", ".join(f"{tag['Key']}={tag['Value']}" for tag in resource.get("Tags", [])),
                }
                all_resources.append(resource_data)
    except ClientError as e:
        print(f"Error in region {region}: {e}")
    return all_resources

def export_to_csv(resource_list, filename="aws_inventory.csv"):
    """Export a list of resource dictionaries to a CSV file."""
    print(f"Exporting {len(resource_list)} resources to {filename}")
    keys = ["Region", "ResourceARN", "Tags"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(resource_list)

def main():
    all_resources = []
    regions = get_all_regions()

    for region in regions:
        resources = get_resources_in_region(region)
        all_resources.extend(resources)

    export_to_csv(all_resources)

if __name__ == "__main__":
    main()
