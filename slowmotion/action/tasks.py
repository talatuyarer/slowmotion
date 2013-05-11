# File upload files over the ssh with celery
from celery import task
from django.conf import settings

import paramiko
import os, commands

import urllib2

def check_connection():
    try:
        response=urllib2.urlopen(u"http://"+settings.SSH_HOST,timeout=1)
        return True
    except: pass
    return False
    
def get_remote_md5(file, ssh):
  # md5sum was not being found via SSH, so had to add full path
  (ssh_in, ssh_out, ssh_err) = ssh.exec_command("/usr/bin/md5sum %s" % file)
  for line in ssh_out.readlines():
    md5sum = line.split(" ")[0]
    return md5sum

def get_local_md5(file):
    #Get Local Video MD5SUM
    local_out = commands.getoutput("md5sum %s" % file)
    return local_out.split(" ")[0]

def open_sshclient(host,user,password):
    #Create SSH Connection
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.load_system_host_keys()
    ssh_client.connect(host, username=user, password=password)
    return ssh_client

@task
def add_queue(instance):
    if instance.uploaded == 0 and check_connection():
        #Connect SSH
        ssh = open_sshclient(settings.SSH_HOST,settings.SSH_USER,settings.SSH_PASSWORD)
        ftp = ssh.open_sftp()
        remote_file = settings.SSH_PATH+instance.video.name
        
        #Send Local to Remote Video
        ftp.put(instance.video.path, remote_file)
        
        #Get MD5SUMs
        local_md5 = get_local_md5(instance.video.path)
        remote_md5 = get_remote_md5(remote_file, ssh)

        #Control MD5Sums
        while local_md5 != remote_md5:
            ftp.put(instance.video.path, remote_file)
            local_md5 = get_local_md5(instance.video.path)
            remote_md5 = get_remote_md5(remote_file, ssh)
        
        #If SUMs OK. Update Sender
        instance.md5sum = local_md5
        instance.uploaded = 1
        instance.save()
        return instance
