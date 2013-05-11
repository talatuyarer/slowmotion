from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse
from django.core.files import File

from django.db.models.signals import post_save
from django.dispatch import receiver

from action.models import Users,Video
from action.tasks import add_queue

import os
import json

from time import sleep

import ptp

import urllib2


firsttime = True

lastmovie = """\
        function dircomp(d1, d2)
            -- compare the digits of a DCIM subdirectory.
            return string.sub(d1, 1, 3) < string.sub(d2, 1, 3)
        end

        function file_comp(f1, f2)
            -- compare the digits of an image/video file in a DCIM subdirectory.
            return string.sub(f1, 5, 8) < string.sub(f2, 5, 9)
        end

        local entries = os.listdir("A/DCIM")
        local max_dir = nil
        local max_file = nil
        local i
        if #entries == 0 then
            write_usb_msg(nil)
            return
        end
        table.sort(entries, dircomp)
        for i = table.getn(entries), 1, -1 do
            local dir_name = entries[i]
            if string.find(dir_name, '^%d%d%d') then
                dir_name = "A/DCIM/" .. dir_name
                if os.stat(dir_name)['is_dir'] then
                    max_dir = dir_name
                    break
                end
            end
        end
        if max_dir == nil then
            write_usb_msg(nil)
            return
        end
        -- Without the sleep(1)
        sleep(1)
        entries = os.listdir(max_dir)
        table.sort(entries, file_comp)
        for i = table.getn(entries), 1, -1 do
            local filename = entries[i]
            if string.find(filename, '^....%d%d%d%d') then
                -- XXX would it make sense to also check if we have a
                -- real file, not a directory? Or the name's suffix?
                write_usb_msg(max_dir .. '/' .. filename)
                return
            end
        end
        -- this happens if we have an empty directory.
        write_usb_msg(max_dir)
        """

def run_script(device,lua):
    script_id = device.chdkExecLua(lua)
    while (device.chdkScriptStatus(script_id) & ptp.CHDKScriptStatus.MSG == 0):
        sleep(0.5)
        #print "waiting for script to finish"
    msg_id = None
    while msg_id != script_id:
        msg, msg_type, msg_id = device.chdkReadScriptMessage()
    return msg

def click_video(device, lua):
    script_id = device.chdkExecLua(lua)
    sleep(0.5)
    return script_id 

@login_required(login_url='/admin/')
def index(request):
    index = "Ana Sayfa"
    context = {'index': index}
    return render(request, 'index.html', context)

@csrf_exempt
def register(request):
    if request.POST:
        data = json.loads(request.raw_post_data)
        kullanici, created = Users.objects.get_or_create(name=data["name"], surname=data["surname"],email = data["email"])
        if data.has_key('token'):
            kullanici.token = data["token"]

        if data.has_key('expired'):
            kullanici.token = data["expired"]

        kullanici.save()
        user_json = {}
        user_json['id'] = kullanici.id
        data = json.dumps(user_json)
    else:
        data = 'fail'        
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
                    
            


def get_users(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        users = Users.objects.filter(name__icontains = q ).order_by("id")[:20]
        results = []
        for user in users:
            user_json = {}
            user_json['id'] = user.id
            user_json['label'] = user.name +" " + user.surname
            user_json['value'] = user.name +" " + user.surname
            results.append(user_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

@login_required(login_url='/admin/')   
def recording(request):
    global firsttime
    if request.POST:
        user_id = request.POST.get('user_id')
        user_name = request.POST.get('users')       
        if firsttime:
            os.system("killall gvfsd-gphoto2")
            sleep(0.2)    
        # For Connection 2 cam 
        cam0 = ptp.list_devices()[0]
        #cam1 = ptp.list_devices()[1]
        device0 = ptp.PTPDevice(cam0[0], cam0[1])
        #device1 = ptp.PTPDevice(cam1[0], cam1[1])
        if firsttime:
            msg = run_script(device0,'return switch_mode_usb(1)')
            #run_script(device1,'return switch_mode_usb(1)')
            firsttime = False
            
        device0_script = click_video(device0,"click('video')")
        #device1_script = click_video(device1,"click('video')")
        
        context = {
            'user_id': user_id,
            'user_name':user_name,
        }
        return render(request, 'recording.html', context)
    else:
        return redirect('/')        

@login_required(login_url='/admin/')   
def save(request):
    global lastmovie
    if request.POST:
        device0_script = None
        device1_script = None
        user_id = request.POST.get('user_id')
        # For Connection 2 cam 
        cam0 = ptp.list_devices()[0]
        #cam1 = ptp.list_devices()[1]
        
        device0 = ptp.PTPDevice(cam0[0], cam0[1])
        #device1 = ptp.PTPDevice(cam1[0], cam1[1])
        
        #stop recording
        device0_script = click_video(device0,"click('video')")
        #device1_script = click_video(device1,"click('video')")    
        
        while (device0_script == None and device1_script == None):
            sleep(0.2)
        
        #get last file
        path0 = run_script(device0,lastmovie)
        #path1 = run_script(device1,lastmovie)
        
        device0.chdkDownload(path0,settings.MEDIA_ROOT+u"tmp/"+user_id+u"_video0.mov")
        #device1.chdkDownload(path0,settings.MEDIA_ROOT+"tmp/"+user_id+"_video1.mov")
        
        #ffmpeg process
        slowmotion_path = settings.MEDIA_ROOT+"tmp/"+user_id+"_video0.mov"
        
        slowmotion_file = open(slowmotion_path)
        #Create Video Record
        video = Video()
        video.user_id= user_id
        video.video.save(user_id+"_video0.mov", File(slowmotion_file))
        video.save()
    return redirect('/')

@receiver(post_save, sender=Video)
def upload(sender,instance, **kwargs):
    add_queue.delay(instance)
    
