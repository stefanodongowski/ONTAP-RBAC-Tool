import os, platform
print(os.getenv('HOSTNAME', os.getenv('COMPUTERNAME', platform.node())).split('.')[0])