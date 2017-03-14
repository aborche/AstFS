# AstFS
Asterisk Virtual FileSystem

Asterisk configuration wrapper to virtual file system

basicfuse.py - basic demo class for make vfs
mpfuse.py - multiprocessing astfs daemon


Just enable AMI in Asterisk and add next lines to manager.conf:

```
[general]
enabled = yes
port = 5038
bindaddr = 127.0.0.1
timestampevents = yes
debug=on

[agiadmin]
secret=Agi02022016
read = all,system,call,log,verbose,agent,user,config,dtmf,reporting,cdr,dialplan,test
write = all,system,call,agent,user,config,command,reporting,originate,message,test
```


Change config directory path, mount path, debug and daemon options if you need in mpfuse.py.
Then run 'python mpfuse.py'

For stop process just run 'umount <mountpoint>

======== basicfuse.py output =========
```
# tree /mnt
/mnt
├── customchmodfile
├── demotreeclass
│   ├── help
│   └── info
├── helpfilefunc
├── link_to_tmp -> /tmp
├── nulldir
├── nullfile
├── staticfile
└── tree
    ├── friend
    ├── peer
    └── user
```
======== basicfuse.py output =========

======== mpfuse.py output =========
```
# tree  /mnt/
/mnt/
├── config -> /usr/local/etc/asterisk
├── peers
│   ├── iax2
│   │   ├── iaxpeer1
│   │   │   └── full
│   │   └── iaxpeer2
│   │       └── full
│   └── sip
│       ├── _offline
│       │   └── sippeer1 -> ../sippeer1
│       ├── _online
│       └── sippeer1
│           ├── codecs
│           ├── contexts
│           ├── credentials
│           ├── full
│           └── huntgroups
└── users
    ├── iax2
    │   └── iaxuser1
    │       └── full
    ├── sipfriends
    │   ├── sipfriend1
    │   │   ├── codecs
    │   │   ├── contexts
    │   │   ├── credentials
    │   │   ├── full
    │   │   └── huntgroups
    │   ├── _offline
    │   │   ├── sipfriend1 -> ../sipfriend1
    │   │   ├── sipfriend2 -> ../sipfriend2
    │   │   └── sipfriend3 -> ../sipfriend3
    │   ├── _online
    │   │   └── realtimeuser1 -> ../realtimeuser1
    │   ├── sipfriend2
    │   │   ├── codecs
    │   │   ├── contexts
    │   │   ├── credentials
    │   │   ├── full
    │   │   └── huntgroups
    │   ├── sipfriend3
    │   │   ├── codecs
    │   │   ├── contexts
    │   │   ├── credentials
    │   │   ├── full
    │   │   └── huntgroups
    │   └── realtimeuser1
    │       ├── codecs
    │       ├── contexts
    │       ├── credentials
    │       ├── full
    │       └── huntgroups
    └── sipusers
        ├── _offline
        │   └── realtimeuser2 -> ../realtimeuser2
        ├── _online
        └── realtimeuser2
            ├── codecs
            ├── contexts
            ├── credentials
            ├── full
            └── huntgroups
```
======== mpfuse.py output =========


