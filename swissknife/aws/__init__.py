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

def get_all_s3_objects(s3, **base_kwargs):
    #https://stackoverflow.com/questions/54314563/how-to-get-more-than-1000-objects-from-s3-by-using-list-objects-v2/54314628
    continuation_token = None
    while True:
        list_kwargs = dict(MaxKeys=1000, **base_kwargs)
        if continuation_token:
            list_kwargs['ContinuationToken'] = continuation_token
        response = s3.list_objects_v2(**list_kwargs)
        yield from response.get('Contents', [])
        if not response.get('IsTruncated'):  # At the end of the list?
            break
        continuation_token = response.get('NextContinuationToken')

def download_s3(bucket_name, bucket_path, download_path, exclude=None, if_exists='abort',input_credentials=False):
    if input_credentials:
        key_id = input('aws_access_key_id')
        secret_key = input('aws_secret_access_key')
        s3_client = boto3.client('s3',aws_access_key_id=key_id,aws_secret_access_key=secret_key)
    else:
        s3_client = boto3.client('s3')

    if exclude is None:
        exclude = []

    #all_keys = s3_client.list_objects_v2(Bucket=bucket_name,Prefix=bucket_path)
    all_keys = [f for f in get_all_s3_objects(s3_client, Bucket=bucket_name, Prefix=bucket_path)]
    keys = [k['Key'] for k in all_keys if k['Key'] not in exclude and k['Key'][-1] != '/']

    download_path = Path(download_path)

    if not download_path.parent.exists():
        download_path.parent.mkdir(parents=True)

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
            if not destination_path.parent.exists():
                destination_path.parent.mkdir(parents=True)

        if download:
            print('Downloading {}'.format(key))
            s3_client.download_file(Bucket=bucket_name,Key=key,Filename=str(destination_path))
