# Automated AMI Backup and Cleanup using lambda functions and Cloudwatch events.

Author: Jyoti Bhanot <jyoti.bhanot30@gmail.com>

## lambdaAMIBackup.py
 This script will search for all instances with tags from ['backup', 'Backup', 'Backup', 'backUp', 'BACKUP']
 on it. As soon as we have the instances list, we loop through each instance
 and create an AMI of it. Also, it will look for a "Retention" tag key which
 will be used as a retention policy number in days. If there is no tag with
 that name, it will use a 7 days default value for each AMI.

 After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
 it will be deleted using the Retention value and another Lambda function
 
 Instance tags will be copied over to AMI tags, accordingly.
 
 Points:
 - Retention unit is days. 
 - Only 1 AMI backup will be creadted/retained for one day.
 - Naming convention for AMIs : ```Lambda - <instanceId> from <current date in YYYY-MM-DD>```

## lambdaAMICleanup.py --
 This script will search for all instances with tags from ['backup', 'Backup', 'Backup', 'backUp', 'BACKUP']
 on it. As soon as we have the instances list, we loop through each instance
 and reference the AMIs of that instance. We check that the latest daily backup
 succeeded then we store every image that's reached its DeleteOn tag's date for
 deletion. We then loop through the AMIs, deregister them and remove all the
 snapshots associated with that AMI.

 Points:
 - DeleteOn value convention : "DD-MM-YYYY"
