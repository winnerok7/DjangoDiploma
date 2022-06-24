from django.db import models
from django.contrib.auth.models import AbstractUser
from .utilities import get_time_marker
# Create your models here.

class CmnUser(AbstractUser):
    is_activated = models.BooleanField(default=True,db_index=True,verbose_name='Is you activated?')
    alert_message = models.BooleanField(default=True, verbose_name='Send messages about new comments?')

    def delete(self, *args, **kwargs):
        for ad in self.ad_set.all():
            ad.delete()
        super().delete(*args,**kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Heading(models.Model):
    name = models.CharField(max_length=30,db_index=True,unique=True,verbose_name='Name')
    order = models.SmallIntegerField(default=0,db_index=True,verbose_name='Order')
    super_heading = models.ForeignKey('SuperHeading',on_delete=models.PROTECT,null=True,blank=True,verbose_name='Main Heading')

class SuperHeadingManage(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_heading__isnull=True)

class SuperHeading(Heading):
    objects= SuperHeadingManage()

    def __str__(self):
        return self.name

    class Meta:
        proxy= True
        ordering=('order','name')
        verbose_name='Main Heading'
        verbose_name_plural='Main Headings'

class SubHeadingManage(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_heading__isnull=False)

class SubHeading(Heading):
    objects = SubHeadingManage()

    def __str__(self):
        return '%s - %s' % (self.super_heading.name,self.name)

    class Meta:
        proxy=True
        ordering = ('super_heading__order','super_heading__name','order','name')
        verbose_name = 'Subheading'
        verbose_name_plural= 'Subheadings'


class Ad(models.Model):
    heading = models.ForeignKey(SubHeading, on_delete=models.PROTECT,
                               verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name='Товар')
    content = models.TextField(verbose_name='Опис')
    price = models.FloatField(default=0, verbose_name='Ціна')
    contacts = models.TextField(verbose_name='Контакти')
    image = models.ImageField(blank=True, upload_to=get_time_marker,
                              verbose_name='Зображення')
    author = models.ForeignKey(CmnUser, on_delete=models.CASCADE,
                               verbose_name='Автор об`яви')
    is_active = models.BooleanField(default=True, db_index=True,
                                    verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True,
                                      verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        for ai in self.addimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Advertisments'
        verbose_name = 'Advertisment'
        ordering = ['-created_at']


class AddImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE,
                           verbose_name='Advertisment')
    image = models.ImageField(upload_to=get_time_marker,
                              verbose_name='Image')

    class Meta:
        verbose_name_plural = 'Additional images'
        verbose_name = 'Additional image'

class Comment(models.Model):
    ad = models.ForeignKey(Ad,on_delete=models.CASCADE,verbose_name='Ad')
    author = models.CharField(max_length=30,verbose_name='Author')
    content = models.TextField(verbose_name='Content')
    is_active = models.BooleanField(default=True,db_index=True,verbose_name='Showed in ad?')
    created_at = models.DateTimeField(auto_now_add=True,db_index=True,verbose_name='Created at')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural='Comments'
        ordering = ['created_at']

