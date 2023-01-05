from ninja import Router, Schema, ModelSchema
from ninja.security import django_auth, APIKeyHeader
from django.http import Http404
from django.contrib.auth.models import User, Group
from LexneticSchool.settings import DEFAULT_PASSWORD

from lexnetic_school.models import Class, Student, Teacher, School, HeadMaster, PersonalInfo, Member
from lexnetic_school.schemas import \
	OkOut, ErrorOut,\
	SchoolIn, SchoolOut,\
	HeadMasterIn, HeadMasterOut, HeadMasterPut,\
	MemberIn, MemberOut,\
	StudentIn, StudentOut, StudentPut,\
	TeacherIn, TeacherOut, TeacherPut,\
	ClassIn, ClassOut

router = Router()

######################
#  Helper Functions  #
######################

# Custom 404
def my_get_object_or_404(model: ModelSchema, **kwargs) -> ModelSchema or dict:
	try:
		return model.objects.get(**kwargs)
	except:
		raise Http404(str(model.__name__) + " with id "+ str(kwargs.get('id', kwargs.get('pk'))))

# Custom dict without keys
def my_without_keys(d: dict, keys: list or dict or tuple) -> dict:
	return {x: d[x] for x in d if x not in keys}

# Generate username and password
def generate_username_password(member: Member) -> tuple:
	def generate_username(first_name: str, last_name: str, n: int) -> str:
		return (first_name.lower()[:n] + last_name.lower())[:8]
	for i in range(1, len(member.personal_info.first_name)):
		username = generate_username(member.personal_info.first_name, member.personal_info.last_name, i)
		if not User.objects.filter(username=username).exists():
			break
	password = DEFAULT_PASSWORD
	return (username, password)

# create Django User
def create_django_user(member: Member, is_staff: bool = False) -> User:
	username, password = generate_username_password(member)
	if member.username:
		username = member.username
	try:
		user = User.objects.create_user(
				username=username,
				password=password,
				is_staff=is_staff,
				first_name=member.personal_info.first_name,
				last_name=member.personal_info.last_name,
				email=member.personal_info.email,
		)
	except:
		raise Exception()
	return user

######################
#     AuthBearer     #
######################

class AuthHeader(APIKeyHeader):
	param_name = 'username_password'
	def authenticate(self, request, key):
		username, password = key.split(':')
		user = User.objects.get(username=username)
		return user

######################
#   API for Schools  #
######################

# GET alls Schools
@router.get('schools', response=list[SchoolOut])
def list_schools(request):
	return [SchoolOut.from_orm(school) for school in School.objects.all()]

# GET School by id
@router.get('school/{int:school_id}', response={200: SchoolOut, 404: ErrorOut})
def get_school(request, school_id: int):
	school = my_get_object_or_404(School, id=school_id)
	school_out = SchoolOut.from_orm(school)
	return school_out

# POST School
@router.post('schools', response={200: OkOut, 404: ErrorOut})
def create_school(request, payload: SchoolIn):
	school = School.objects.create(**payload.dict())
	Group.objects.create(name=school.name)
	return {"detail":"School sucessfully created.", "model": SchoolOut.from_orm(school)}

# PUT School by id
@router.put('school/{int:school_id}', response={200: OkOut, 404: ErrorOut})
def update_school(request, school_id: int, payload: SchoolIn):
	school = my_get_object_or_404(School, id=school_id)
	for attr, value in payload.dict().items():
		setattr(school, attr, value)
	school.save()
	return {"detail":"School sucessfully updated.", "model": SchoolOut.from_orm(school)}

# DELETE School by id
@router.delete('school/{int:school_id}', response=dict)
def delete_school(request, school_id: int):
	school = my_get_object_or_404(School, id=school_id)
	school.delete()
	return {"detail":f"School with id {school_id} sucessfully deleted."}

######################
#   API for Members  #
######################

# GET alls Members
@router.get('members', response=list[MemberOut])
def list_members(request):
	return [MemberOut.from_orm(member) for member in Member.objects.all()]

# GET Member by id
@router.get('member/{int:member_id}', response={200: MemberOut, 404: ErrorOut})
def get_member(request, member_id: int):
	member = my_get_object_or_404(Member, id=member_id)
	return MemberOut.from_orm(member)

# GET Members by school id
@router.get('members/{int:school_id}', response=list[MemberOut])
def get_members_by_school(request, school_id: int):
	school = my_get_object_or_404(School, id=school_id)
	return [MemberOut.from_orm(member) for member in Member.objects.filter(school=school)]

# GET Member by username
@router.get('member/{str:username}', response={200: MemberOut, 404: ErrorOut})
def get_member_by_username(request, username: str):
	member = my_get_object_or_404(Member, username=username)
	return MemberOut.from_orm(member)

# # PUT username and password
# @router.put('member/{int:member_id}/password', auth=AuthHeader ,response={200: OkOut, 403: ErrorOut, 404: ErrorOut})
# def update_member_username_password(request, member_id: int, payload: MemberIn):
# 	if request.auth.get_role() != 'headmaster':
# 		return 403, {"You are not allowed to do this action."}
# 	member = my_get_object_or_404(Member, id=member_id)
# 	username, password = generate_username_password(payload)
# 	return {"detail":"Username and password sucessfully updated.", "model": MemberOut.from_orm(member)}

######################
# API for HeadMaster #
######################

# GET alls HeadsMasters
@router.get('heads_masters', response=list[HeadMasterOut])
def list_heads_masters(request):
	return [HeadMasterOut.from_orm(head_master) for head_master in HeadMaster.objects.all()]

# GET HeadMaster by id
@router.get('heads_master/{int:head_master_id}', response={200: HeadMasterOut, 404: ErrorOut})
def get_head_master(request, head_master_id: int):
	head_master = my_get_object_or_404(HeadMaster, id=head_master_id)
	return HeadMasterOut.from_orm(head_master)

# POST HeadMaster
@router.post('heads_masters', response={200: OkOut, 409: ErrorOut, 404: ErrorOut})
def create_head_master(request, payload: HeadMasterIn):
	school = my_get_object_or_404(School, id=payload.school_id)
	for head_master in HeadMaster.objects.all():
		if head_master.school == school:
			return 404, {"detail": "There is already a HeadMaster for this school."}
	new_personal_info = PersonalInfo.objects.create(**payload.personal_info.dict())
	new_member = Member.objects.create(personal_info=new_personal_info, school=school, role="HM")
	new_head_master = HeadMaster.objects.create(member=new_member, school=school)
	try:
		new_user = create_django_user(new_member, is_staff=True, username=payload.username)
		new_member.username = new_user.username
		new_member.save()
	except:
		new_head_master.delete()
		new_member.delete()
		new_personal_info.delete()
		return 409, {"detail":"Username already exists."}
	return {
			"detail":"HeadMaster sucessfully created.",
			"model": HeadMasterOut.from_orm(new_head_master),
			"username": new_user.username,
		}

# PUT HeadMaster by id
@router.put('heads_master/{int:head_master_id}', response={200: OkOut, 404: ErrorOut})
def update_head_master(request, head_master_id: int, payload: HeadMasterPut):
	head_master = my_get_object_or_404(HeadMaster, id=head_master_id)
	for attr, value in payload.dict().items():
		if attr == 'personal_info':
			if value:
				for attr, value in payload.personal_info.dict().items():
					setattr(head_master.personal_info, attr, value)
		else:
			setattr(head_master, attr, value)
	head_master.personal_info.save()
	head_master.save()
	return {"detail":"HeadMaster sucessfully updated.", "model": HeadMasterOut.from_orm(head_master)}

# DELETE HeadMaster by id
@router.delete('heads_master/{int:head_master_id}', response=dict)
def delete_head_master(request, head_master_id: int):
	head_master = my_get_object_or_404(HeadMaster, id=head_master_id)
	member = my_get_object_or_404(Member, id=head_master.member.id)
	personal_info = my_get_object_or_404(PersonalInfo, id=member.personal_info.id)
	head_master.delete()
	member.delete()
	personal_info.delete()
	return {"detail":f"HeadMaster with id {head_master_id} sucessfully deleted."}

######################
#  API for Teachers  #
######################

# GET alls Teachers
@router.get('teachers', response=list[TeacherOut])
def list_teachers(request):
	return [TeacherOut.from_orm(teacher) for teacher in Teacher.objects.all()]

# GET Teacher by id
@router.get('teacher/{int:teacher_id}', response={200: TeacherOut, 404: ErrorOut})
def get_teacher(request, teacher_id: int):
	teacher = my_get_object_or_404(Teacher, id=teacher_id)
	return TeacherOut.from_orm(teacher)

# POST Teacher
@router.post('teachers', response={200: OkOut, 409: ErrorOut, 404: ErrorOut})
def create_teacher(request, payload: TeacherIn):
	school = my_get_object_or_404(School, id=payload.school_id)
	new_personal_info = PersonalInfo.objects.create(**payload.personal_info.dict())
	new_member = Member.objects.create(personal_info=new_personal_info, school=school, role="TE", username=payload.username)
	new_teacher = Teacher.objects.create(member=new_member)
	try:
		new_user = create_django_user(new_member, is_staff=True)
		new_member.username = new_user.username
		new_member.save()
	except:
		new_teacher.delete()
		new_member.delete()
		new_personal_info.delete()
		return 409, {"detail":"Username already exists."}
	return {
			"detail":"Teacher sucessfully created.",
			"model": TeacherOut.from_orm(new_teacher),
			"username": new_user.username,
		}

# PUT Teacher by id
@router.put('teacher/{int:teacher_id}', response={200: OkOut, 404: ErrorOut})
def update_teacher(request, teacher_id: int, payload: TeacherPut):
	teacher = my_get_object_or_404(Teacher, id=teacher_id)
	for attr, value in payload.dict().items():
		if attr == 'personal_info':
			if value:
				for attr, value in payload.personal_info.dict().items():
					setattr(teacher.personal_info, attr, value)
		else:
			setattr(teacher, attr, value)
	teacher.personal_info.save()
	teacher.save()
	return {"detail":"Teacher sucessfully updated.", "model": TeacherOut.from_orm(teacher)}

# DELETE Teacher by id
@router.delete('teacher/{int:teacher_id}', response=dict)
def delete_teacher(request, teacher_id: int):
	teacher = my_get_object_or_404(Teacher, id=teacher_id)
	member = my_get_object_or_404(Member, id=teacher.member.id)
	personal_info = my_get_object_or_404(PersonalInfo, id=member.personal_info.id)
	teacher.delete()
	member.delete()
	personal_info.delete()
	return {"detail":f"Teacher with id {teacher_id} sucessfully deleted."}

######################
#   API for Classes  #
######################

# GET alls Classes
@router.get('classes', response=list[ClassOut])
def list_classes(request):
	return [ClassOut.from_orm(class_) for class_ in Class.objects.all()]

# GET Class by id
@router.get('class/{int:class_id}', response={200: ClassOut, 404: ErrorOut})
def get_class(request, class_id: int):
	class_ = my_get_object_or_404(Class, id=class_id)
	return ClassOut.from_orm(class_)

# POST Class
@router.post('classes', response={200: OkOut, 404: ErrorOut})
def create_class(request, payload: ClassIn):
	teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
	school = my_get_object_or_404(School, id=payload.school_id)
	new_class_info = my_without_keys(payload.dict(), ['teacher_id', 'school_id'])
	new_class = Class.objects.create(teacher=teacher, school=school, **new_class_info)
	return {
			"detail":"Class sucessfully created.",
			"model": ClassOut.from_orm(new_class)
		}

# PUT Class by id
@router.put('class/{int:class_id}', response={200: OkOut, 404: ErrorOut})
def update_class(request, class_id: int, payload: ClassIn):
	class_ = my_get_object_or_404(Class, id=class_id)
	teacher = None
	school = None
	for attr, value in payload.dict().items():
		if attr == 'teacher_id':
			teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
			setattr(class_, attr, teacher)
		elif attr == 'school_id':
			school = my_get_object_or_404(School, id=payload.school_id)
			setattr(class_, attr, school)
		else:
			setattr(class_, attr, value)
	if teacher:
		teacher.save()
	if school:
		school.save()
	class_.save()
	return {
			"detail":"Class sucessfully updated.",
			"model": ClassOut.from_orm(class_)
			}

# DELETE Class by id
@router.delete('class/{int:class_id}', response=dict)
def delete_class(request, class_id: int):
	class_ = my_get_object_or_404(Class, id=class_id)
	for student in class_.students.all():
		member = my_get_object_or_404(Member, id=student.member.id)
		personal_info = my_get_object_or_404(PersonalInfo, id=member.personal_info.id)
		student.delete()
		member.delete()
		personal_info.delete()
	class_.delete()
	return {"detail":f"Class with id {class_id} sucessfully deleted."}

######################
#  API for Students  #
######################

# GET alls Students
@router.get('students', response=list[StudentOut])
def list_students(request):
	return [StudentOut.from_orm(student) for student in Student.objects.all()]

# GET Student by id
@router.get('student/{int:student_id}', response={200: StudentOut, 404: ErrorOut})
def get_student(request, student_id: int):
	student = my_get_object_or_404(Student, id=student_id)
	return StudentOut.from_orm(student)

# POST Student
@router.post('students', response={200: OkOut, 409: ErrorOut, 404: ErrorOut})
def create_student(request, payload: StudentIn):
	school = my_get_object_or_404(School, id=payload.school_id)
	class_ = my_get_object_or_404(Class, id=payload.class_id)
	new_personal_info = PersonalInfo.objects.create(**payload.personal_info.dict())
	new_member = Member.objects.create(personal_info=new_personal_info, school=school, role="ST", username=payload.username)
	new_student = Student.objects.create(member=new_member, f_class=class_)
	try:
		new_user = create_django_user(new_member)
		new_member.username = new_user.username
		new_member.save()
	except:
		new_member.delete()
		new_personal_info.delete()
		new_student.delete()
		return 409, {"detail":"Username already exists."}
	return {
			"detail":"Student sucessfully created.",
			"model": StudentOut.from_orm(new_student),
			"username": new_user.username,
			}


# PUT Student by id
@router.put('student/{int:student_id}', response={200: OkOut, 404: ErrorOut})
def update_student(request, student_id: int, payload: StudentPut):
	student = my_get_object_or_404(Student, id=student_id)
	school = None
	class_ = None
	for attr, value in payload.dict().items():
		if attr == 'personal_info':
			if value:
				for attr, value in payload.personal_info.dict().items():
					setattr(student.member.personal_info, attr, value)
				student.member.personal_info.save()
		elif attr == 'school_id':
			school = my_get_object_or_404(School, id=payload.school_id)
			setattr(student.member, attr, school)
		elif attr == 'class_id':
			class_ = my_get_object_or_404(Class, id=payload.class_id)
			setattr(student, attr, class_)
		else:
			setattr(student, attr, value)
	if school:
		school.save()
	if class_:
		class_.save()
	student.save()
	return {
			"detail":"Student sucessfully updated.",
			"model": StudentOut.from_orm(student)
			}

# DELETE Student by id
@router.delete('student/{int:student_id}', response=dict)
def delete_student(request, student_id: int):
	student = my_get_object_or_404(Student, id=student_id)
	member = my_get_object_or_404(Member, id=student.member.id)
	personal_info = my_get_object_or_404(PersonalInfo, id=member.personal_info.id)
	student.delete()
	member.delete()
	personal_info.delete()
	return {"detail":f"Student with id {student_id} sucessfully deleted."}

######################
#   API for utils	 #
######################


