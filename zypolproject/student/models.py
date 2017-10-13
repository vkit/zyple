from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Userprofile(models.Model):
    user=models.OneToOneField(User, blank=True, null=True)
    name=models.CharField(max_length=150,blank=True)
    role=models.IntegerField(default=1, help_text="1-Student, 2-Teacher,3-Admin")
    email=models.EmailField(blank=True)
    # is_admin=models.BooleanField()
    is_admin = models.NullBooleanField()
    is_teacher = models.NullBooleanField()
    is_student = models.NullBooleanField()

    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(default=timezone.now)
    modified_at=models.DateTimeField(default=timezone.now)
    profile_image=models.ImageField(upload_to='userprofilepics', blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return '%s - %s'%(self.user.username, self.name)

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        return super(Userprofile, self).save(*args, **kwargs)


class Task(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    task_headline = models.CharField(max_length=10)
    task_body = models.TextField()
    created_at=models.DateTimeField(default=timezone.now)
    modified_at=models.DateTimeField(default=timezone.now)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.task_headline

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        return super(Task, self).save(*args, **kwargs)

class AssignTask(models.Model):
    student_to = models.ForeignKey(User, blank=True, null=True)
    task = models.ForeignKey(Task, blank=True, null=True)
    task_status = models.IntegerField(default=0, help_text="1-todo,2-progress,3-approved,4-disapproved,5-doing,6-done")
    created_at=models.DateTimeField(default=timezone.now)
    modified_at=models.DateTimeField(default=timezone.now)
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return unicode(self.task)

    def save(self, *args, **kwargs):
        self.modified_at = timezone.now()
        return super(Assign, self).save(*args, **kwargs)


