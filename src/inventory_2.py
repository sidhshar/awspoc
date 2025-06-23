import boto3
import csv

# Hardcoded list of commercial AWS regions
def get_all_regions():
    return [
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        "af-south-1", "ap-east-1", "ap-south-1", "ap-south-2",
        "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4",
        "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
        "ca-central-1", "eu-central-1", "eu-central-2",
        "eu-west-1", "eu-west-2", "eu-west-3", "eu-north-1",
        "eu-south-1", "eu-south-2", "il-central-1",
        "me-south-1", "me-central-1", "sa-east-1"
    ]

def get_ec2_instances(region):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        instances = ec2.describe_instances()
        data = []
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                data.append({
                    "Region": region,
                    "Service": "EC2",
                    "ResourceId": instance["InstanceId"],
                    "Details": f"State: {instance['State']['Name']}"
                })
        return data
    except Exception as e:
        print(f"[{region}] EC2 error: {e}")
        return []

def get_rds_instances(region):
    try:
        rds = boto3.client("rds", region_name=region)
        instances = rds.describe_db_instances()
        return [{
            "Region": region,
            "Service": "RDS",
            "ResourceId": db["DBInstanceIdentifier"],
            "Details": f"Engine: {db['Engine']}, Status: {db['DBInstanceStatus']}"
        } for db in instances["DBInstances"]]
    except Exception as e:
        print(f"[{region}] RDS error: {e}")
        return []

def get_s3_buckets():
    try:
        s3 = boto3.client("s3")
        buckets = s3.list_buckets()
        data = []
        for bucket in buckets["Buckets"]:
            # Get the bucket region
            try:
                region = s3.get_bucket_location(Bucket=bucket["Name"])["LocationConstraint"]
                if region is None:
                    region = "us-east-1"
            except:
                region = "unknown"
            data.append({
                "Region": region,
                "Service": "S3",
                "ResourceId": bucket["Name"],
                "Details": "Bucket"
            })
        return data
    except Exception as e:
        print(f"S3 error: {e}")
        return []

def export_to_csv(resource_list, filename="aws_inventory.csv"):
    print(f"\nExporting {len(resource_list)} resources to {filename}")
    keys = ["Region", "Service", "ResourceId", "Details"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(resource_list)

def main():
    all_resources = []

    print("Fetching S3 buckets (global)...")
    all_resources.extend(get_s3_buckets())

    regions = get_all_regions()
    for region in regions:
        print(f"\nScanning region: {region}")
        all_resources.extend(get_ec2_instances(region))
        all_resources.extend(get_rds_instances(region))

    export_to_csv(all_resources)

if __name__ == "__main__":
    main()
