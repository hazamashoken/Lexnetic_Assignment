from django.db import models

# Create your models here.
class HeadMaster(models.Model):
	member = models.ForeignKey('Member', on_delete=models.CASCADE)
	school = models.OneToOneField('School', on_delete=models.CASCADE)

class School(models.Model):
	name = models.CharField(max_length=100)
	address = models.CharField(max_length=100)
	phone = models.CharField(max_length=100, blank=True, null=True)
	email = models.CharField(max_length=100, blank=True, null=True)
	website = models.CharField(max_length=100, blank=True, null=True)

class Class(models.Model):
	year = models.IntegerField(default=0)
	teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
	school = models.ForeignKey('School', on_delete=models.CASCADE)

class Teacher(models.Model):
	member = models.ForeignKey('Member', on_delete=models.CASCADE)

class Student(models.Model):
	member = models.ForeignKey('Member', on_delete=models.CASCADE)
	intake_year = models.IntegerField(default=0)
	f_class = models.ForeignKey('Class', on_delete=models.CASCADE)

class Member(models.Model):
	school = models.ForeignKey('School', on_delete=models.CASCADE)
	username = models.CharField(max_length=100, unique=True, default=None, blank=True, null=True)
	TEACHER = "TE"
	HEAD_MASTER = "HM"
	STUDENT = "ST"
	ROLE_CHOICES = [
		(TEACHER, "Teacher"),
		(HEAD_MASTER, "Head Master"),
		(STUDENT, "Student"),
	]
	role = models.CharField(max_length=2, choices=ROLE_CHOICES, default=STUDENT)
	personal_info = models.OneToOneField('PersonalInfo', on_delete=models.CASCADE)

class PersonalInfo(models.Model):
	first_name = models.CharField(max_length=100)
	middle_name = models.CharField(max_length=100, default=None, blank=True, null=True)
	last_name = models.CharField(max_length=100)
	email = models.EmailField(max_length=100, default=None, blank=True, null=True)
	phone = models.CharField(max_length=100, default=None, blank=True, null=True)
	address = models.CharField(max_length=100, default=None, blank=True, null=True)
