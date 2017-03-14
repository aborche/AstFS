# AstFS
Asterisk Virtual FileSystem

Asterisk configuration wrapper to virtual file system

basicfuse.py - basic demo class for making simple vfs

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
Then run 
```
# python mpfuse.py
```

For stop process just run 
```
# umount <mountpoint>
```

======== basicfuse.py output =========
```
# tree -ghpu /mnt/
/mnt/
├── [-rw------- root     wheel      27]  customchmodfile
├── [drwxr-xr-x asterisk asterisk  512]  demotreeclass
│   ├── [-rw-r--r-- asterisk asterisk   12]  help
│   └── [-rw-r--r-- asterisk asterisk   12]  info
├── [-rw-r--r-- asterisk asterisk   33]  helpfilefunc
├── [lrwxr-xr-x asterisk asterisk    4]  link_to_tmp -> /tmp
├── [drwxr-xr-x asterisk asterisk  512]  nulldir
├── [-rw-r--r-- asterisk asterisk    0]  nullfile
├── [-rw-r--r-- asterisk asterisk   22]  staticfile
└── [drwxr-xr-x asterisk asterisk  512]  tree
    ├── [drwxr-xr-x asterisk asterisk  512]  friend
    ├── [-rw-r--r-- asterisk asterisk   16]  peer
    └── [drwxr-xr-x asterisk asterisk  512]  user

6 directories, 7 files
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


