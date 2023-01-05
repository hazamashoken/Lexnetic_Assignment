from django.contrib import admin

from lexnetic_school.models import HeadMaster, School, Class, Student, Teacher, Member, PersonalInfo
# Register your models here.

admin.site.register(HeadMaster)
admin.site.register(School)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Member)
admin.site.register(PersonalInfo)
