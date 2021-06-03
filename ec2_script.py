#!/usr/bin/python3
import yaml
import boto3
import os

'''parsing yaml file and using key as OS Environment '''
file_path = f"{os.getcwd()}/lookup.yaml"
print(file_path)

with open(fr'{file_path}') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    lookup_file = yaml.load(file, Loader=yaml.FullLoader)
    yml_parse = lookup_file["server"]

my_dic = {}


def yaml_parser():
    for key, value in yml_parse.items():
        if type(value) == str:
            my_dic[key] = value
        if type(value) == int:
            string_convert = str(value)
            my_dic[key] = string_convert
        if type(value) == list:
            for ke, val in value[0].items():
                w_convert = str(val)
                my_dic[ke] = w_convert
        if type(value) == list:
            for ke, val in value[1].items():
                w_convert = str(val)
                my_dic[ke] = w_convert


'''setting OS environment '''


def set_os_env():
    for key, value in my_dic.items():
        os.environ[str(key)] = str(value)
        user = os.getenv(str(key))
        # print(key + "=" + user)


yaml_parser()
set_os_env()

client = boto3.client('ec2', region_name='us-east-1')

user_data = '''#!/bin/bash
mkdir /home/ec2-user/patrice
echo 'test' > /home/ec2-user/test
sudo mkfs -t xfs /dev/xvdf
sudo mkdir /data
sudo mount /dev/xvdf /data
sudo useradd user1
sudo passwd -f -u user1
sudo mkdir -p /home/user1/.ssh
sudo cp -R /home/ec2-user/.ssh/authorized_keys /home/user1/.ssh/authorized_keys
sudo chown user1 /home/user1/.ssh/authorized_keys
sudo useradd user2
sudo passwd -f -u user2
sudo mkdir -p /home/user2/.ssh
sudo cp -R /home/ec2-user/.ssh/authorized_keys /home/user2/.ssh/authorized_keys
sudo chown user2 /home/user2/.ssh/authorized_keys'''


def create_volume():
    '''create ebs volume'''
    ebs_vol = client.create_volume(Size=int(os.environ['size_gb2']), AvailabilityZone='us-east-1b')
    volume_id = ebs_vol['VolumeId']

    '''check that the EBS volume has been created successfully'''
    waiter = client.get_waiter('volume_available')

    waiter.wait(
        Filters=[
            {
                'Name': 'status',
                'Values': ['available']
            },
        ],
        VolumeIds=[
            volume_id,
        ]
    )
    if ebs_vol['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Successfully created Volume! " + volume_id)
        print(f'Volume is available for use ')
        return volume_id


volume_ID = create_volume()


def create_key_pair():
    '''create key pair'''
    my_key = 'my-test-key'
    data = client.create_key_pair(KeyName=my_key)
    keypair = data['KeyMaterial']
    key_pair = f'{my_key}.pem'
    key_file = open(key_pair, "w")
    key_file.write(keypair)
    key_file.close()
    return my_key


key_pair = create_key_pair()


def create_sg():
    ''' create security group '''
    sg_name = 'test-sg-fetch'
    sg = boto3.resource('ec2')
    instance = sg.create_security_group(GroupName=sg_name, Description=sg_name)
    ''' get security-group ID '''
    # ec2 = boto3.client('ec2')
    group_name = sg_name
    sgresponse = client.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=[group_name])
        ]
    )

    group_id = sgresponse['SecurityGroups'][0]['GroupId']

    ''' adding rule to SG'''
    sg_id = client.authorize_security_group_ingress(
        GroupId=group_id,
        IpPermissions=[
            {
                'FromPort': 22,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'SSH access from everywhere',
                    },
                ],
                'ToPort': 22,
            },
        ],
    )

    print(f"security-group ID: {group_id}")
    return group_id


sg = create_sg()


def run_instance():
    ''' create instances '''
    ec2_tag = 'fetch-test-server'
    response_instance = client.run_instances(
        BlockDeviceMappings=[{
            'DeviceName': os.environ['device'],
            # 'VirtualName': 'string',
            'Ebs': {
                'DeleteOnTermination': True,
                'VolumeSize': int(os.environ['size_gb']),
                'VolumeType': 'standard'
            }
        }],
        ImageId='ami-0d5eff06f840b45e9',
        InstanceType=(os.environ['instance_type']),
        KeyName=key_pair,
        SecurityGroupIds=[sg],
        MaxCount=int(os.environ['min_count']),
        MinCount=int(os.environ['max_count']),
        UserData=user_data,
        Placement={
            'AvailabilityZone': 'us-east-1b'
        },
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': ec2_tag
                    }
                ]
            }
        ]
    )
    instance_id = response_instance["Instances"][0]["InstanceId"]
    print(f"ec2_instance_Id: {instance_id}")

    '''waiter for ec2 instance '''
    instance_waiter = client.get_waiter('instance_running')
    instance_waiter.wait(
        InstanceIds=[
            instance_id,
        ]
    )
    print("instance in running state")
    '''mount a volume to existing ec2'''
    vol_id_att = client.attach_volume(
        Device=(os.environ['device2']),
        # /dev/sdf
        InstanceId=instance_id,
        VolumeId=volume_ID
    )
    print("instance is provisioning ..... ")


run_instance()
