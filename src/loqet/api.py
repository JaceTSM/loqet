###########
# loq api #
###########
"""
loq api: for interacting with loq files not associated with a context

API:
read_loq_file   get unencrypted contents of loq file
write_loq_file  encrypt contents and write them to a loq file

API + CLI:
loq         encrypt a file
unloq       unencrypt a file

CLI only:
loq print    print encrypted file contents
loq edit     edit encrypted file in place
loq view     view encrypted file contents in viewer
"""




#############
# loqet api #
#############
"""
loqet api: for interacting with a loqet secret store

API:
loqet_load      load a single loqet namespace (one file from the loqet dir)

CLI only:
loqet get       retrieve value from a loqet namespace
loqet read      read contents of target loquet namespace
loqet open      unloq all loq files in loqet dir
loqet close     loq all open configs in loqet dir


Notes:
* When a .loq and .open file exist for a given config, 
    the .open file contents take precedence. This way you
    can unloq a file, change it, test your change, and then 
    loq it when you are done
* This isn't initially intended for dynamic secret setting
    within python. For now the api will be read-only so people
    don't accidentally overwrite their local secret stores without
    putting some effort in. :)
"""

