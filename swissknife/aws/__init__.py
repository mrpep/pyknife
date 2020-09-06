import boto3

def get_instances_info(region='us-east-1'):
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