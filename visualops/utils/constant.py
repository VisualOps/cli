
# AppService Error Code

ERROR = {
    #legacy
    "E_OK"        : 0,
    "E_NONE"      : 1,
    "E_INVALID"   : 2,
    "E_FULL"      : 3,
    "E_EXIST"     : 4,
    "E_EXTERNAL"  : 5,
    "E_FAILED"    : 6,
    "E_BUSY"      : 7,
    "E_NORSC"     : 8,
    "E_NOPERM"    : 9,
    "E_NOSTOP"    : 10,
    "E_NOSTART"   : 11,
    "E_ERROR"     : 12,
    "E_LEFTOVER"  : 13,
    "E_TIMEOUT"   : 14,
    "E_UNKNOWN"   : 15,
    "E_CONN"      : 16,
    "E_EXPIRED"   : 17,
    "E_PARAMS"    : 18,
    "E_SESSION"   : 19,
    "E_END"       : 20,
    "E_BLOCKED_USER"   : 21,
    "E_IDEM"      : 22,
    "E_REMOVED_USER"   : 23,

    # common:  1*
    "GlobalErrorInit"       : 100, # Sorry, we are suffering from some technical issue, please try again later
    "GlobalErrorApi"        : 101, # Invalid API Parameters
    "GlobalErrorSession"    : 102, # Invalid session, please login again
    "GlobalErrorDb"         : 103, # DB operation failed
    "GlobalErrorRegion"     : 104, # Region mismatched
    "GlobalErrorId"         : 105, # Id mismatched
    "GlobalErrorUsername"   : 106, # Username mismatched
    "GlobalErrorIntercom"   : 107, # Failed to generate intercom secret hash
    "GlobalErrorUnknown"    : 109, #
    "UserInvalidUser"       : 110, # Invalid username or password
    "UserInvalidUsername"   : 111, # Invalid username {0}
    "UserErrorUser"         : 112, # user {0} missing {1}
    "UserBlockedUser"       : 113, # User {0} blocked
    "UserRemovedUser"       : 114, # User {0} removed
    "UserNoUser"            : 115, # User {0} not existed
    "UserInvalidEmail"      : 116, # Invalid email {0}
    "SessionInvalidSessio"  : 120, # Invalid session {0}/{1}
    "SessionInvalidId"      : 121, # Invalid session {0}
    "SessionFailedCreate"   : 122, # Can not create session {0} - {1}
    "SessionFailedUpdate"   : 123, # Can not update session {0} - {1}
    "SessionFailedDelete"   : 124, # Can not delete session {0} - {1}
    "SessionFailedGet"      : 125, # Can not get session {0}
    "SessionErrorSession"   : 126, # Mismatched username {0} and session id {1}
    "SessionNotConnected"   : 127, # Cannot connect with session manager
    "RequestErrorRequest"   : 130, # Cannot submit request
    "RequestInvalidId"      : 131, # Invalid request id {0}
    "RequestNoPending"      : 132, # Request {0} is no longer pending
    "RequestErrorEmail"     : 133, # Submit email request failed
    "RequestOnProcess"      : 134, # Request is processing and please submit request later
    "IdConstrain"           : 134, # Request is processing and please submit request later

    # forge:  2*
    "AppInvalidFormat"      : 210, # Missing parameter {0}
    "AppNotStop"            : 211, # Invalid parameter: stack is not stoppable but the lease action is set to Stop
    "AppBeingOperated"      : 212, # App {0} is being operated
    "AppNotRename"          : 213, # Can not rename app {0}
    "AppInvalidId"          : 214, # Invalid app id {0}
    "AppInvalidState"       : 214, # Invalid app state {0}
    "AppIsRunning"          : 215, # {0} is currently running
    "AppIsStopped"          : 216, # {0} is currently stopped
    "AppNotStoppable"       : 217, # {0} is not stoppable
    "StackInvalidFormat"    : 250, # Missing parameter {0}
    "StackNotStop"          : 251, # Invalid parameter: stack is not stoppable but the lease action is set to Stop
    "StackRepeatedStack"    : 252, # Repeated stack {0}
    "StackInvalidId"        : 253, # Invalid stack id {0}
    "StackIsRemoved"        : 254, # Stack {0} is already removed
    "StackIsDisabled"       : 255, # Stack {0} is already disabled
    "StackVerifyFailed"     : 256, # Verify stack {0} exception {1}
    "StateErrorModule"      : 260, # The version of this stack is no longer supported, please contact with our support for details

}

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