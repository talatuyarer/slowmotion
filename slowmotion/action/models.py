# -*- coding: utf-8 -*-
from django.db import models

class Users(models.Model):
    name = models.CharField(verbose_name=u"İsim",max_length=50)
    surname = models.CharField(verbose_name=u"Soyisim",max_length=50)
    email = models.EmailField(verbose_name=u"Email",unique=True)
    token = models.CharField(verbose_name=u"Facebook Token",max_length=300, null=True, blank=True)
    expired = models.CharField(verbose_name=u"Facebook Expired",max_length=10, null=True, blank=True)
    
    def __unicode__(self):
        return self.name + u" " + self.surname
    
    class Meta:
        verbose_name=u"Kullanıcı"
        verbose_name_plural = u"Kullanıcılar"

class Video(models.Model):
    user = models.ForeignKey(Users)
    video = models.FileField(upload_to="videos/")
    uploaded = models.BooleanField(verbose_name=u"Upload Edildi mi", default=False)
    md5sum = models.CharField(verbose_name=u"Video MD5 Sum",max_length=100, null=True, blank=True)
          
    class Meta:
        verbose_name=u"Vidyo"
        verbose_name_plural = u"Vidyolar"    
