# Automated AMI Backups
#
# Author : <jyoti.bhanot30@gmail.com>
#
# This script will search for all instances with tags from ['backup', 'Backup', 'Backup', 'backUp', 'BACKUP']
# on it. As soon as we have the instances list, we loop through each instance
# and create an AMI of it. Also, it will look for a "Retention" tag key which
# will be used as a retention policy number in days. If there is no tag with
# that name, it will use a 7 days default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function 

import boto3
import collections
import datetime
import sys
import pprint

ec = boto3.client('ec2')
#image = ec.Image('id')

def lambda_handler(event, context):
    
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': ['backup', 'Backup', 'Backup', 'backUp', 'BACKUP']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d instances that need backing up" % len(instances)

    to_tag = collections.defaultdict(list)

    for instance in instances:
        try:
            retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
        except IndexError:
            retention_days = 7
        finally:
            try:
                #create_image(instance_id, name, description=None, no_reboot=False, block_device_mapping=None, dry_run=False)
                # DryRun, InstanceId, Name, Description, NoReboot, BlockDeviceMappings
                create_time = datetime.datetime.now()
                create_fmt = create_time.strftime('%Y-%m-%d')
        
                AMIid = ec.create_image(InstanceId=instance['InstanceId'], \
                                        Name="Lambda - " + instance['InstanceId'] \
                                        + " from " + create_fmt, Description="Lambda created AMI of instance " \
                                        + instance['InstanceId'] + " from " + create_fmt, NoReboot=True, DryRun=False)

                
                pprint.pprint(instance)
                #sys.exit()
                #break
        
                #to_tag[retention_days].append(AMIid)
                # Copying instance tags to AMI tags.
                for tag in instance['Tags']:
                    ec.create_tags(
                        Resources=[AMIid['ImageId']],
                        Tags=[
                            {'Key': tag['Key'], 'Value': tag['Value']},
                        ]
                    )
                to_tag[retention_days].append(AMIid['ImageId'])
                
                print "Retaining AMI %s of instance %s for %d days" % (
                    AMIid['ImageId'],
                    instance['InstanceId'],
                    retention_days,
                )
            except:
               print "Backup for this day already present."

    print to_tag.keys()
    
    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        print "Will delete %d AMIs on %s" % (len(to_tag[retention_days]), delete_fmt)
        
        #break
    
        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )
