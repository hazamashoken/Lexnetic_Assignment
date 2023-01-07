from ninja import Router, ModelSchema, Form
from ninja.pagination import paginate
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.contrib.auth.models import User
from LexneticSchool.settings import DEFAULT_PASSWORD, SECRET_KEY, CREATE_USER_ON_POST

from lexnetic_school.models import Class, Student, Teacher, School, HeadMaster, PersonalInfo, Member
from lexnetic_school.schemas import \
	OkOut, DetailOut,\
	SchoolIn, SchoolOut, SchoolPatch,\
	HeadMasterIn, HeadMasterOut, HeadMasterPut, HeadMasterPatch,\
	MemberOut,\
	StudentIn, StudentOut, StudentPut, StudentPatch,\
	TeacherIn, TeacherOut, TeacherPut, TeacherPatch,\
	ClassIn, ClassOut, ClassPut, ClassPatch

router = Router()

######################
#  Helper Functions  #
######################

# Custom 404
def my_get_object_or_404(model: ModelSchema, **kwargs) -> ModelSchema or dict:
	try:
		return model.objects.get(**kwargs)
	except:
		raise HttpError(404, str(model.__name__) + " with " + str(kwargs.keys()) + ' ' + str(kwargs.values()) + ' does not exist')

def my_get_object_for_update_or_404(model: ModelSchema, **kwargs) -> ModelSchema or dict:
	try:
		return model.objects.select_for_update().get(**kwargs)
	except:
		raise HttpError(404, str(model.__name__) + " with " + str(kwargs.keys()) + ' ' + str(kwargs.values()) + ' does not exist')

# Custom dict without keys
def my_without_keys(d: dict, keys: list or dict or tuple) -> dict:
	return {x: d[x] for x in d if x not in keys}

# Generate username and password
def generate_username_password(member: Member) -> tuple:
	def generate_username(first_name: str, last_name: str, n: int) -> str:
		return (first_name.lower()[:n] + last_name.lower())[:8]
	for i in range(1, len(member.personal_info.first_name)):
		username = generate_username(member.personal_info.first_name, member.personal_info.last_name, i)
		if not Member.objects.filter(username=username).exists():
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

# delete Member subtypes
def delete_memberSubType(memberSubType: Teacher or Student or HeadMaster) -> None:
	member = memberSubType.member
	user = User.objects.get(username=member.username)
	personal_info = member.personal_info
	memberSubType.delete()
	member.delete()
	personal_info.delete()
	user.delete()

def get_subtype(role: str) -> Teacher or Student or HeadMaster:
	if role == "HM":
		return HeadMaster
	elif role == "TE":
		return Teacher
	elif role == "ST":
		return Student
	else:
		return 404

# create Member subtypes
def create_memberSubType(role: str, payload: TeacherIn or StudentIn or HeadMasterIn) -> Teacher or Student or HeadMaster or int:
	# get MemberSubType from role
	MemberSubType = get_subtype(role)
	# check if school exists then set school
	try:
		school = my_get_object_or_404(School, id=payload.school_id)
	except:
		return 4041

	# check if school has a headmaster
	if MemberSubType == HeadMaster:
		for headmaster in MemberSubType.objects.all():
			if headmaster.school == school:
				return 4042

	# check if username exists then create new Member
	if Member.objects.filter(username=payload.username).exists():
		return 409
	if MemberSubType == Student:
		if not Class.objects.filter(id=payload.class_id).exists():
			return 4043
	# create new PersonalInfo
	new_personal_info = PersonalInfo.objects.create(**payload.personal_info.dict())
	new_member = Member.objects.create(personal_info=new_personal_info, school=school, role=role, username=payload.username)

	# check if class exists then create new MemberSubType
	if MemberSubType == HeadMaster:
		new_member_subtype = MemberSubType.objects.create(member=new_member, school=school)
	elif MemberSubType == Teacher:
		new_member_subtype = MemberSubType.objects.create(member=new_member)
	elif MemberSubType == Student:
		class_ = my_get_object_or_404(Class, id=payload.class_id)
		new_member_subtype = MemberSubType.objects.create(member=new_member, f_class=class_ ,intake_year=payload.intake_year)

	# create new Django User, change in settings.py
	if CREATE_USER_ON_POST:
		new_user = create_django_user(new_member, is_staff=(MemberSubType == HeadMaster or MemberSubType == Teacher))
		new_member.username = new_user.username
		new_member.save()
	return new_member_subtype

######################
#     AuthBearer     #
######################

class AuthBearer(HttpBearer):
	def authenticate(self, request, token: str) :
		if token == SECRET_KEY:
			return SECRET_KEY

######################
#   API for Schools  #
######################

# GET alls Schools
@router.get('schools', response=list[SchoolOut], tags=['School'], summary="List all schools", description="Return List all schools with pagination")
@paginate
def list_schools(request):
	return [SchoolOut.from_orm(school) for school in School.objects.all()]

# GET School by id
@router.get('school/{int:school_id}', response={200: SchoolOut, 404: DetailOut}, tags=['School'], summary="Get a school", description="Get a school by id")
def get_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	return 200, SchoolOut.from_orm(school)

# POST School
@router.post('schools', response={200: OkOut, 404: DetailOut}, auth=AuthBearer() ,tags=['School'], summary="Create a school", description="Create a school")
def create_school(request, payload: SchoolIn = Form(...)):
	school = School.objects.create(**payload.dict())
	return {"detail":"School sucessfully created.", "model": SchoolOut.from_orm(school)}

# PUT School by id
@router.put('school/{int:school_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['School'], summary="Update a school", description="Update a school")
def update_school(request, school_id: int, payload: SchoolIn = Form(...)):
	try:
		school = my_get_object_for_update_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	for attr, value in payload.dict().items():
		setattr(school, attr, value)
	school.save()
	return 200, {"detail":"School sucessfully updated.", "model": SchoolOut.from_orm(school)}

# PATCH School by id
@router.patch('school/{int:school_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['School'], summary="Update a school", description="Update a school")
def patch_school(request, school_id: int, payload: SchoolPatch = Form(...)):
	try:
		school = my_get_object_for_update_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	for attr, value in payload.dict(exclude_unset=True).items():
		setattr(school, attr, value)
	school.save()
	return {"detail":"School sucessfully patched.", "model": SchoolOut.from_orm(school)}

# DELETE School by id
@router.delete('school/{int:school_id}', response={200: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['School'], summary="Delete a school", description="Delete a school")
def delete_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	if Class.objects.filter(school=school).exists():
		for class_ in Class.objects.filter(school=school):
			class_.delete()
	if Teacher.objects.filter(member__school=school).exists():
		for teacher in Teacher.objects.filter(school=school):
			delete_memberSubType(teacher)
	if Student.objects.filter(member__school=school).exists():
		for student in Student.objects.filter(school=school):
			delete_memberSubType(student)
	if HeadMaster.objects.filter(school=school).exists():
		headmaster =  my_get_object_or_404(HeadMaster, school=school)
		delete_memberSubType(headmaster)
	school.delete()
	return 200, {"detail":f"School with id {school_id} sucessfully deleted."}

# GET School by HeadMaster id
@router.get('headmaster/{int:headmaster_id}/school', response={200: SchoolOut, 404: DetailOut}, tags=['School'], summary="Get a school by HeadMaster id", description="Get a school by HeadMaster id")
def get_school_by_headmaster(request, headmaster_id: int):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	school = my_get_object_or_404(School, id=headmaster.school.id)
	return SchoolOut.from_orm(school)

######################
#   API for Members  #
######################

# GET alls Members
@router.get('members', response=list[MemberOut], tags=['Member'], summary="List all members", description="Return List all members with pagination")
@paginate
def list_members(request):
	return [MemberOut.from_orm(member) for member in Member.objects.all()]

# GET Member by id
@router.get('member/{int:member_id}', response={200: MemberOut, 404: DetailOut}, tags=['Member'], summary="Get a member", description="Get a member by id")
def get_member(request, member_id: int):
	try:
		member = my_get_object_or_404(Member, id=member_id)
	except:
		return 404, {"detail":"Member does not exist."}
	return 200, MemberOut.from_orm(member)

# GET Members by school id
@router.get('members/{int:school_id}', response={200: list[MemberOut], 404: DetailOut}, tags=['Member'], summary="Get members by school", description="Get members by school id")
def get_members_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	return 200, [MemberOut.from_orm(member) for member in Member.objects.filter(school=school)]

# GET Member by username
@router.get('member/{str:username}', response={200: MemberOut, 404: DetailOut}, tags=['Member'], summary="Get a member", description="Get a member by username")
def get_member_by_username(request, username: str):
	try:
		member = my_get_object_or_404(Member, username=username)
	except:
		return 404, {"detail":"Member does not exist."}
	return 200, MemberOut.from_orm(member)

# GET alls Members of a school
@router.get('school/{int:school_id}/members', response={200: list[MemberOut], 404: DetailOut}, tags=['Member'], summary="List all members of a school", description="Return List all members of a school with pagination")
def list_members_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	return [MemberOut.from_orm(member) for member in Member.objects.filter(school=school)]

# DELETE Member by id
# @router.delete('member/{int:member_id}', response=dict, auth=AuthBearer(), tags=['Member'], summary="Delete a member", description="Delete a member")
# def delete_member(request, member_id: int):
# 	try:
# 		member = my_get_object_or_404(Member, id=member_id)
# 	except:
# 		return 404, {"detail":"Member does not exist."}
# 	personal_info = member.personal_info
# 	member.delete()
# 	personal_info.delete()
# 	return 200, {"detail":f"Member with id {member_id} sucessfully deleted."}

# # PUT username and password
# @router.put('member/{int:member_id}/password', auth=AuthHeader ,response={200: OkOut, 403: DetailOut, 404: DetailOut})
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
@router.get('headmasters', response=list[HeadMasterOut], tags=['HeadMaster'], summary="List all HeadMaster", description="Return List all HeadMaster with pagination")
@paginate
def list_headmasters(request):
	return [HeadMasterOut.from_orm(headmaster) for headmaster in HeadMaster.objects.all()]

# GET HeadMaster by id
@router.get('headmaster/{int:headmaster_id}', response={200: HeadMasterOut, 404: DetailOut}, tags=['HeadMaster'], summary="Get a HeadMaster", description="Get a HeadMaster by id")
def get_headmaster(request, headmaster_id: int):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	return 200, HeadMasterOut.from_orm(headmaster)

# POST HeadMaster
@router.post('headmasters', response={200: OkOut, 409: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['HeadMaster'], summary="Create a HeadMaster", description="Create a HeadMaster")
def create_headmaster(request, payload: HeadMasterIn = Form(...)):
	new_headmaster = create_memberSubType("HM", payload)
	if new_headmaster == 4041:
		return 404, {"detail":"School does not exist."}
	if new_headmaster == 4042:
		return 409, {"detail": "School already has a HeadMaster."}
	if new_headmaster == 404:
		return 404, {"detail": "Role Error."}
	if new_headmaster == 409:
		return 409, {"detail": "This username already exist."}
	return 200, {
			"detail":"HeadMaster sucessfully created.",
			"model": HeadMasterOut.from_orm(new_headmaster),
		}

# PUT HeadMaster by id
@router.put('headmaster/{int:headmaster_id}', response={200: OkOut, 409: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['HeadMaster'], summary="Update a HeadMaster", description="Update a HeadMaster by id")
def update_headmaster(request, headmaster_id: int, payload: HeadMasterPut = Form(...)):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	for attr, value in payload.dict().items():
		if attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=value)
			except:
				return 404, {"detail":"School does not exist."}
			if HeadMaster.objects.filter(school=school).exists():
				if HeadMaster.objects.get(school=school).id != headmaster.id:
					return 409, {"detail": "School already has a HeadMaster."}
			headmaster.school = school
		elif attr == 'personal_info':
			for attr2, value2 in value.items():
				setattr(headmaster.member.personal_info, attr2, value2)
	headmaster.member.personal_info.save()
	headmaster.member.save()
	headmaster.save()
	return 200, {"detail":"HeadMaster sucessfully updated.", "model": HeadMasterOut.from_orm(headmaster)}

# PATCH HeadMaster by id
@router.patch('headmaster/{int:headmaster_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['HeadMaster'], summary="Update a HeadMaster", description="Update a HeadMaster by id")
def patch_headmaster(request, headmaster_id: int, payload: HeadMasterPatch = Form(...)):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	for attr, value in payload.dict(exclude_unset=True, exclude_none=True).items():
		if attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=value)
			except:
				return 404, {"detail":"School does not exist."}
			if HeadMaster.objects.filter(school=school).exists():
				if HeadMaster.objects.get(school=school).id != headmaster.id:
					return 409, {"detail": "School already has a HeadMaster."}
			headmaster.school = school
		elif attr == 'personal_info':
			for attr2, value2 in value.items():
				if value2:
					setattr(headmaster.member.personal_info, attr2, value2)
	headmaster.member.personal_info.save()
	headmaster.member.save()
	headmaster.save()
	return 200, {"detail":"HeadMaster sucessfully patched.", "model": HeadMasterOut.from_orm(headmaster)}

# DELETE HeadMaster by id
@router.delete('headmaster/{int:headmaster_id}', response={200: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['HeadMaster'], summary="Delete a HeadMaster", description="Delete a HeadMaster by id")
def delete_headmaster(request, headmaster_id: int):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	delete_memberSubType(headmaster)
	return 200, {"detail":f"HeadMaster with id {headmaster_id} sucessfully deleted."}

# GET HeadMaster by school id
@router.get('school/{int:school_id}/headmaster', response={200: HeadMasterOut, 404: DetailOut}, tags=['HeadMaster'], summary="Get a HeadMaster by school id", description="Get a HeadMaster by school id")
def get_headmaster_by_school_id(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail":"School does not exist."}
	try:
		headmaster = my_get_object_or_404(HeadMaster, school=school)
	except:
		return 404, {"detail":"HeadMaster does not exist."}
	return 200, HeadMasterOut.from_orm(headmaster)

######################
#  API for Teachers  #
######################

# GET alls Teachers
@router.get('teachers', response=list[TeacherOut], tags=['Teacher'], summary="List all Teachers", description="Return List all Teachers with pagination")
@paginate
def list_teachers(request):
	return [TeacherOut.from_orm(teacher) for teacher in Teacher.objects.all()]

# GET Teacher by id
@router.get('teacher/{int:teacher_id}', response={200: TeacherOut, 404: DetailOut}, tags=['Teacher'], summary="Get a Teacher", description="Get a Teacher by id")
def get_teacher(request, teacher_id: int):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {"detail":"Teacher does not exist."}
	return 200, TeacherOut.from_orm(teacher)

# POST Teacher
@router.post('teachers', response={200: OkOut, 409: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['Teacher'], summary="Create a Teacher", description="Create a Teacher")
def create_teacher(request, payload: TeacherIn = Form(...)):
	new_teacher = create_memberSubType("TE", payload)
	if new_teacher == 4041:
		return 404, {'detail': 'School does not exist.'}
	if new_teacher == 404:
		return 404, {"detail": "There is already a Teacher for this school."}
	if new_teacher == 409:
		return 409, {"detail": "This username already exist."}
	return 200, {
			"detail":"Teacher sucessfully created.",
			"model": TeacherOut.from_orm(new_teacher)
		}

# PUT Teacher by id
@router.put('teacher/{int:teacher_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Teacher'], summary="Update a Teacher", description="Update a Teacher by id")
def update_teacher(request, teacher_id: int, payload: TeacherPut = Form(...)):
	try:
		teacher = my_get_object_for_update_or_404(Teacher, id=teacher_id)
	except:
		return 404, {'detail': 'Teacher does not exist.'}
	for attr, value in payload.dict().items():
		if attr == 'personal_info':
			for attr2, value2 in payload.personal_info.dict().items():
				setattr(teacher.member.personal_info, attr2, value2)
		else:
			setattr(teacher, attr, value)
	teacher.member.personal_info.save()
	teacher.member.save()
	teacher.save()
	return 200, {
			"detail":"Teacher sucessfully updated.",
			"model": TeacherOut.from_orm(teacher)
		}

# PATCH Teacher by id
@router.patch('teacher/{int:teacher_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Teacher'], summary="Update a Teacher", description="Update a Teacher by id")
def patch_teacher(request, teacher_id: int, payload: TeacherPatch = Form(...)):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {'detail': 'Teacher does not exist.'}
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == 'personal_info':
			for attr, value in payload.personal_info.dict(exclude_unset=True).items():
				setattr(teacher.member.personal_info, attr, value)
		else:
			setattr(teacher, attr, value)
	teacher.member.personal_info.save()
	teacher.member.save()
	teacher.save()
	return 200, {
			"detail":"Teacher sucessfully patched.",
			"model": TeacherOut.from_orm(teacher)
		}

# DELETE Teacher by id
@router.delete('teacher/{int:teacher_id}', response={200: dict, 404: DetailOut}, auth=AuthBearer(), tags=['Teacher'], summary="Delete a Teacher", description="Delete a Teacher by id")
def delete_teacher(request, teacher_id: int):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {'detail': 'Teacher does not exist.'}
	delete_memberSubType(teacher)
	return 200, {
		"detail":f"Teacher with id {teacher_id} sucessfully deleted."
	}

# GET alls Teachers by school id
@router.get('school/{int:school_id}/teachers', response={200: list[TeacherOut], 404: DetailOut}, tags=['Teacher'], summary="List all Teachers by school id", description="Return List all Teachers by school id with pagination")
def list_teachers_by_school_id(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	return 200, [TeacherOut.from_orm(teacher) for teacher in Teacher.objects.filter(member__school=school)]


######################
#   API for Classes  #
######################

# GET alls Classes
@router.get('classes', response=list[ClassOut], tags=['Class'], summary="List all Classes", description="Return List all Classes with pagination")
@paginate
def list_classes(request):
	return [ClassOut.from_orm(class_) for class_ in Class.objects.all()]

# GET Class by id
@router.get('class/{int:class_id}', response={200: ClassOut, 404: DetailOut}, tags=['Class'], summary="Get a Class", description="Get a Class by id")
def get_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {"detail":"Class does not exist."}
	return 200, ClassOut.from_orm(class_)

# POST Class
@router.post('classes', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Class'], summary="Create a Class", description="Create a Class")
def create_class(request, payload: ClassIn = Form(...)):
	try:
		teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
	except:
		return 404, {'detail': 'Teacher does not exist.'}
	try:
		school = my_get_object_or_404(School, id=payload.school_id)
	except:
		return 404, {'detail': 'School does not exist.'}
	new_class_info = my_without_keys(payload.dict(), ['teacher_id', 'school_id'])
	new_class = Class.objects.create(teacher=teacher, school=school, **new_class_info)
	return 200, {
			"detail":"Class sucessfully created.",
			"model": ClassOut.from_orm(new_class)
		}

# PUT Class by id
@router.put('class/{int:class_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Class'], summary="Update a Class", description="Update a Class by id")
def update_class(request, class_id: int, payload: ClassPut = Form(...)):
	try:
		class_ = my_get_object_for_update_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	for attr, value in payload.dict().items():
		if attr == 'teacher_id':
			try:
				teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
			except:
				return 404, {'detail': 'Teacher does not exist.'}
			setattr(class_, 'teacher', teacher)
		elif attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {'detail': 'School does not exist.'}
			setattr(class_, 'school', school)
		else:
			setattr(class_, attr, value)
	class_.save()
	return 200, {
			"detail":"Class sucessfully updated.",
			"model": ClassOut.from_orm(class_)
			}

# PATCH Class by id
@router.patch('class/{int:class_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Class'], summary="Update a Class", description="Update a Class by id")
def patch_class(request, class_id: int, payload: ClassPatch = Form(...)):
	class_ = my_get_object_for_update_or_404(Class, id=class_id)
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == 'teacher_id':
			try:
				teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
			except:
				return 404, {'detail': 'Teacher does not exist.'}
			setattr(class_, attr, teacher)
		elif attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {'detail': 'School does not exist.'}
			setattr(class_, attr, school)
		else:
			setattr(class_, attr, value)
	class_.save()
	return {
			"detail":"Class sucessfully patched.",
			"model": ClassOut.from_orm(class_)
			}

# DELETE Class by id
@router.delete('class/{int:class_id}', response={200: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['Class'], summary="Delete a Class", description="Delete a Class by id")
def delete_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	for student in Student.objects.filter(f_class=class_):
		delete_memberSubType(student)
	class_.delete()
	return 200, {"detail":f"Class with id {class_id} sucessfully deleted."}

# GET alls Classes by School id
@router.get('school/{int:school_id}/classes', response={200: list[ClassOut], 404: DetailOut}, tags=['Class'], summary="List all Classes by School id", description="Return List all Classes by School id with pagination")
def list_classes_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	if not Class.objects.filter(school=school).exists():
		return 404, {"detail": "No Classes found."}
	return 200, [ClassOut.from_orm(class_) for class_ in Class.objects.filter(school=school)]

######################
#  API for Students  #
######################

# GET alls Students
@router.get('students', response=list[StudentOut], tags=['Student'], summary="List all Students", description="Return List all Students with pagination")
@paginate
def list_students(request):
	return [StudentOut.from_orm(student) for student in Student.objects.all()]

# GET Student by id
@router.get('student/{int:student_id}', response={200: StudentOut, 404: DetailOut}, tags=['Student'], summary="Get a Student", description="Get a Student by id")
def get_student(request, student_id: int):
	try:
		student = my_get_object_or_404(Student, id=student_id)
	except:
		return 404, {"detail":"Student does not exist."}
	return 200, StudentOut.from_orm(student)

# POST Student
@router.post('students', response={200: OkOut, 409: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['Student'], summary="Create a Student", description="Create a Student")
def create_student(request, payload: StudentIn = Form(...)):
	new_student = create_memberSubType("ST", payload)
	if new_student == 409:
		return 409, {"detail":"Username already exists."}
	if new_student == 4041:
		return 404, {"detail":"School does not exist."}
	if new_student == 4043:
		return 404, {"detail":"Class does not exist."}
	return 200, {
			"detail":"Student sucessfully created.",
			"model": StudentOut.from_orm(new_student)
			}

# PUT Student by id
@router.put('student/{int:student_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Student'], summary="Update a Student", description="Update a Student by id")
def update_student(request, student_id: int, payload: StudentPut = Form(...)):
	try:
		student = my_get_object_for_update_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	for attr, value in payload.dict().items():
		if attr == 'personal_info':
			for attr, value in payload.personal_info.dict().items():
				setattr(student.member.personal_info, attr, value)
		elif attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {'detail': 'School does not exist.'}
			setattr(student.member, attr, school)
		elif attr == 'class_id':
			try:
				class_ = my_get_object_or_404(Class, id=payload.class_id)
			except:
				return 404, {'detail': 'Class does not exist.'}
			setattr(student, attr, class_)
		else:
			setattr(student, attr, value)
	student.member.personal_info.save()
	student.member.save()
	student.save()
	return 200, {
			"detail":"Student sucessfully updated.",
			"model": StudentOut.from_orm(student)
			}

# PATCH Student by id
@router.patch('student/{int:student_id}', response={200: OkOut, 404: DetailOut}, auth=AuthBearer(), tags=['Student'], summary="Update a Student", description="Update a Student by id")
def patch_student(request, student_id: int, payload: StudentPatch = Form(...)):
	try:
		student = my_get_object_for_update_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == 'personal_info':
			for attr, value in payload.personal_info.dict().items():
				setattr(student.member.personal_info, attr, value)
		elif attr == 'school_id':
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {'detail': 'School does not exist.'}
			setattr(student.member, attr, school)
		elif attr == 'class_id':
			try:
				class_ = my_get_object_or_404(Class, id=payload.class_id)
			except:
				return 404, {'detail': 'Class does not exist.'}
			setattr(student, attr, class_)
		else:
			setattr(student, attr, value)
	student.member.personal_info.save()
	student.member.save()
	student.save()
	return 200, {
			"detail":"Student sucessfully patched.",
			"model": StudentOut.from_orm(student)
			}

# DELETE Student by id
@router.delete('student/{int:student_id}', response={200: DetailOut, 404: DetailOut}, auth=AuthBearer(), tags=['Student'], summary="Delete a Student", description="Delete a Student by id")
def delete_student(request, student_id: int):
	try:
		student = my_get_object_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	delete_memberSubType(student)
	return 200, {"detail":f"Student with id {student_id} sucessfully deleted."}

# GET alls Students by School id
@router.get('school/{int:school_id}/students', response={200: list[StudentOut], 404: DetailOut}, tags=['Student'], summary="List all Students by School id", description="Return List all Students by School id with pagination")
def list_students_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {'detail': 'School does not exist.'}
	return 200, [StudentOut.from_orm(student) for student in Student.objects.filter(member__school=school)]

# GET alls Students by Class id
@router.get('class/{int:class_id}/students', response={200: list[StudentOut], 404: DetailOut}, tags=['Student'], summary="List all Students by Class id", description="Return List all Students by Class id with pagination")
def list_students_by_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {'detail': 'Class does not exist.'}
	return 200, [StudentOut.from_orm(student) for student in Student.objects.filter(f_class=class_)]

######################
#   API for utils	 #
######################

