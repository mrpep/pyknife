import boto3
import tqdm
from pathlib import Path

def get_instances_info(region='us-east-1',input_credentials=False):
    if input_credentials:       
        key_id = input('aws_access_key_id')
        secret_key = input('aws_secret_access_key')
        ec2 = boto3.client('ec2',region,aws_access_key_id=key_id,aws_secret_access_key=secret_key)
    else:
        ec2 = boto3.client('ec2',region)

    response = ec2.describe_instances()
    info_instances = []
    for group in response['Reservations']: 
        for instance in group['Instances']: 
            instance_i = { 
                'id': instance['InstanceId'], 
                'name': [tag['Value'] for tag in instance['Tags'] if tag['Key']=='Name'][0], 
                'PublicDnsName': instance['PublicDnsName']
                } 
            info_instances.append(instance_i)

    return info_instances 

def download_s3(bucket_name, bucket_path, download_path, exclude=None, if_exists='abort',input_credentials=False):
    if input_credentials:
        key_id = input('aws_access_key_id')
        secret_key = input('aws_secret_access_key')
        s3_client = boto3.client('s3',aws_access_key_id=key_id,aws_secret_access_key=secret_key)
    else:
        s3_client = boto3.client('s3')

    all_keys = s3_client.list_objects_v2(Bucket=bucket_name,Prefix=bucket_path)
    keys = [k['Key'] for k in all_keys['Contents'] if k['Key'] not in exclude]

    download_path = Path(download_path)

    if not download_path.exists():
        download_path.mkdir(parents=True)

    for key in tqdm.tqdm(keys):
        relative_key = str(Path(key).relative_to(bucket_path))
        destination_path = Path(download_path,relative_key)
        download = False
        if destination_path.exists():
            if if_exists == 'abort':
                print('Skipping {} as it already exists'.format(key))
            elif if_exists == 'replace':
                download = True
            else:
                raise Exception('Unknown if_exists value {}'.format(if_exists))
        else:
            download = True

        if download:
            print('Downloading {}'.format(key))
            s3_client.download_file(Bucket=bucket_name,Key=key,Filename=str(destination_path))
