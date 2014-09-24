
# Error Code
E_OK		= 0
E_NONE		= 1
E_INVALID	= 2
E_FULL		= 3
E_EXIST		= 4
E_EXTERNAL	= 5			# external opertion failure
E_FAILED	= 6
E_BUSY		= 7
E_NORSC		= 8
E_NOPERM	= 9
E_NOSTOP	= 10
E_NOSTART	= 11
E_ERROR		= 12
E_LEFTOVER	= 13
E_TIMEOUT   = 14
E_UNKNOWN	= 15
E_CONN		= 16
E_EXPIRED	= 17
E_PARAMS	= 18
E_SESSION	= 19
E_END		= 20
E_BLOCKED_USER   = 21
E_IDEM		= 22
E_REMOVED_USER   = 23


RESTYPE ={
    'AZ'           : 'AWS.EC2.AvailabilityZone',
    'INSTANCE'     : 'AWS.EC2.Instance',
    'KP'           : 'AWS.EC2.KeyPair',
    'SG'           : 'AWS.EC2.SecurityGroup',
    'EIP'          : 'AWS.EC2.EIP',
    'AMI'          : 'AWS.EC2.AMI',
    'VOL'          : 'AWS.EC2.EBS.Volume',
    'SNAP'         : 'AWS.EC2.EBS.Snapshot',
    'ELB'          : 'AWS.ELB',
    'VPC'          : 'AWS.VPC.VPC',
    'SUBNET'       : 'AWS.VPC.Subnet',
    'IGW'          : 'AWS.VPC.InternetGateway',
    'RT'           : 'AWS.VPC.RouteTable',
    'VGW'          : 'AWS.VPC.VPNGateway',
    'CGW'          : 'AWS.VPC.CustomerGateway',
    'ENI'          : 'AWS.VPC.NetworkInterface',
    'DHCP'         : 'AWS.VPC.DhcpOptions',
    'VPN'          : 'AWS.VPC.VPNConnection',
    'ACL'          : 'AWS.VPC.NetworkAcl',
    'IAM'          : 'AWS.IAM.ServerCertificate',
    'ASG'          : 'AWS.AutoScaling.Group',
    'LC'           : 'AWS.AutoScaling.LaunchConfiguration',
    'NC'           : 'AWS.AutoScaling.NotificationConfiguration',
    'SP'           : 'AWS.AutoScaling.ScalingPolicy',
    'SA'           : 'AWS.AutoScaling.ScheduledActions',
    'CW'           : 'AWS.CloudWatch.CloudWatch',
    'SUBSCRIPTION' : 'AWS.SNS.Subscription',
    'TOPIC'        : 'AWS.SNS.Topic',
    'TAG'          : 'AWS.EC2.Tag',
    'ASGTAG'       : 'AWS.AutoScaling.Tag',
    'DBSBG'        : 'AWS.RDS.DBSubnetGroup',
    'DBINSTANCE'   : 'AWS.RDS.DBInstance',
    'DBPARAM'      : 'AWS.RDS.Parameter',
    'DBPG'         : 'AWS.RDS.ParameterGroup',
    'DBSNAP'       : 'AWS.RDS.Snapshot',
    'DBES'         : 'AWS.RDS.EventSubscription',
    'DBOG'         : 'AWS.RDS.OptionGroup',
    'DBENGINE'     : 'AWS.RDS.DBEngineVersion',
}