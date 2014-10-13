#Copyright 2014 MadeiraCloud LTD.

import os

#IDE URL
IDE_URL = 'http://ide.visualops.io/ops/'
API_URL = 'http://api.visualops.io'
DB_FILE = os.path.expanduser("~/.visualops/db")

#app state
#STATE_APP_INITIALIZING = "Initializing"
STATE_APP_RUNNING      = "Running"
STATE_APP_STOPPING     = "Stopping"
STATE_APP_STOPPED      = "Stopped"
STATE_APP_STARTING     = "Starting"
STATE_APP_REBOOTING    = "Rebooting"
#STATE_APP_CLONING      = "Cloning"
STATE_APP_TERMINATING  = "Terminating"
STATE_APP_TERMINATED   = "Terminated"

# AppService Error Code
ERROR = {
    #legacy
    0  : 'E_OK',
    1  : 'E_NONE',
    2  : 'E_INVALID',
    3  : 'E_FULL',
    4  : 'E_EXIST',
    5  : 'E_EXTERNAL',
    6  : 'E_FAILED',
    7  : 'E_BUSY',
    8  : 'E_NORSC',
    9  : 'E_NOPERM',
    10 : 'E_NOSTOP',
    11 : 'E_NOSTART',
    12 : 'E_ERROR',
    13 : 'E_LEFTOVER',
    14 : 'E_TIMEOUT',
    15 : 'E_UNKNOWN',
    16 : 'E_CONN',
    17 : 'E_EXPIRED',
    18 : 'E_PARAMS',
    19 : 'E_SESSION',
    20 : 'E_END',
    21 : 'E_BLOCKED_USER',
    22 : 'E_IDEM',
    23 : 'E_REMOVED_USER',

    100 : 'Sorry, we are suffering from some technical issue, please try again later'  ,   # GlobalErrorInit
    101 : 'Invalid API Parameters'  ,                   # GlobalErrorApi
    102 : 'Invalid session, please login again with "visualops login"'  ,      # GlobalErrorSession
    103 : 'DB operation failed'  ,                      # GlobalErrorDb
    104 : 'Region mismatched'  ,                        # GlobalErrorRegion
    105 : 'Id mismatched'  ,                            # GlobalErrorId
    106 : 'Username mismatched'  ,                      # GlobalErrorUsername
    107 : 'Failed to generate intercom secret hash'  ,  # GlobalErrorIntercom
    109 : 'Unknown Error'  ,                            # GlobalErrorUnknown
    110 : 'Invalid username or password' ,      # UserInvalidUser
    111 : 'Invalid username' ,                  # UserInvalidUsername
    112 : 'User missing' ,                      # UserErrorUser
    113 : 'User has been blocked'  ,            # UserBlockedUser
    114 : 'User has been removed'  ,            # UserRemovedUser
    115 : 'User does not existed'  ,            # UserNoUser
    116 : 'Invalid email' ,                     # UserInvalidEmail
    120 : 'Invalid session' ,                       # SessionInvalidSession
    121 : 'Invalid session' ,                       # SessionInvalidId
    122 : 'Can not create session' ,                # SessionFailedCreate
    123 : 'Session is invalid, no need logout' ,    # SessionFailedUpdate
    124 : 'Can not delete session' ,                # SessionFailedDelete
    125 : 'Can not get session' ,                   # SessionFailedGet
    126 : 'Mismatched username and session id' ,    # SessionErrorSession
    127 : 'Cannot connect with session manager'  ,  # SessionNotConnected
    130 : 'Cannot submit request'  ,                                    # RequestErrorRequest
    131 : 'Invalid request id' ,                                        # RequestInvalidId
    132 : 'Request is no longer pending'  ,                             # RequestNoPending
    133 : 'Submit email request failed'  ,                              # RequestErrorEmail
    134 : 'Request is processing and please submit request later'  ,    # RequestOnProcess
    134 : 'Request is processing and please submit request later'  ,    # IdConstrain
    210 : 'Missing parameter' ,                                                             # AppInvalidFormat
    211 : 'Invalid parameter: stack is not stoppable but the lease action is set to Stop' , # AppNotStop
    212 : 'App is being operated'  ,                                                        # AppBeingOperated
    213 : 'Can not rename app' ,                                                            # AppNotRename
    214 : 'Invalid app id' ,                                                                # AppInvalidId
    214 : 'Invalid app state' ,                                                             # AppInvalidState
    215 : 'App is currently running'  ,                                                     # AppIsRunning
    216 : 'App is currently stopped'  ,                                                     # AppIsStopped
    217 : 'App is not stoppable'  ,                                                         # AppNotStoppable
    250 : 'Missing parameter' ,                                                                             # StackInvalidFormat
    251 : 'Invalid parameter: stack is not stoppable but the lease action is set to Stop'  ,                # StackNotStop
    252 : 'Repeated stack' ,                                                                                # StackRepeatedStack
    253 : 'Invalid stack id' ,                                                                              # StackInvalidId
    254 : 'Stack has already removed'  ,                                                                    # StackIsRemoved
    255 : 'Stack has already disabled'  ,                                                                   # StackIsDisabled
    256 : 'Verify stack exception' ,                                                                        # StackVerifyFailed
    260 : 'The version of this stack is no longer supported, please contact with our support for details' , # StateErrorModule

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
