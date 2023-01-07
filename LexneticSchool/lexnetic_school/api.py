from ninja import Router, ModelSchema, Form
from ninja.pagination import paginate
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.contrib.auth.models import User
from LexneticSchool.settings import DEFAULT_PASSWORD, SECRET_KEY, CREATE_USER_ON_POST

from lexnetic_school.models import (
	Class,
	Student,
	Teacher,
	School,
	HeadMaster,
	PersonalInfo,
	Member,
)
from lexnetic_school.schemas import (
	OkOut,
	DetailOut,
	HeadMasterIn,
	MemberOut,
	StudentIn,
	TeacherIn,
)

router = Router()

######################
#  Helper Functions  #
######################


# Custom 404
def my_get_object_or_404(model: ModelSchema, **kwargs) -> ModelSchema or dict:
	try:
		return model.objects.get(**kwargs)
	except:
		raise HttpError(
			404,
			str(model.__name__)
			+ " with "
			+ str(kwargs.keys())
			+ " "
			+ str(kwargs.values())
			+ " does not exist",
		)


def my_get_object_for_update_or_404(
	model: ModelSchema, **kwargs
) -> ModelSchema or dict:
	try:
		return model.objects.select_for_update().get(**kwargs)
	except:
		raise HttpError(
			404,
			str(model.__name__)
			+ " with "
			+ str(kwargs.keys())
			+ " "
			+ str(kwargs.values())
			+ " does not exist",
		)


# Custom dict without keys
def my_without_keys(d: dict, keys: list or dict or tuple) -> dict:
	return {x: d[x] for x in d if x not in keys}


# Generate username and password
def generate_username_password(member: Member) -> tuple:
	def generate_username(first_name: str, last_name: str, n: int) -> str:
		return (first_name.lower()[:n] + last_name.lower())[:8]

	for i in range(1, len(member.personal_info.first_name)):
		username = generate_username(
			member.personal_info.first_name, member.personal_info.last_name, i
		)
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
	user = None
	if User.objects.filter(username=member.username).exists():
		user = User.objects.get(username=member.username)
	personal_info = member.personal_info
	memberSubType.delete()
	member.delete()
	personal_info.delete()
	if user:
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
def create_memberSubType(
	role: str, payload: TeacherIn or StudentIn or HeadMasterIn
) -> Teacher or Student or HeadMaster or int:
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
	new_member = Member.objects.create(
		personal_info=new_personal_info,
		school=school,
		role=role,
		username=payload.username,
	)

	# check if class exists then create new MemberSubType
	if MemberSubType == HeadMaster:
		new_member_subtype = MemberSubType.objects.create(
			member=new_member, school=school
		)
	elif MemberSubType == Teacher:
		new_member_subtype = MemberSubType.objects.create(member=new_member)
	elif MemberSubType == Student:
		class_ = my_get_object_or_404(Class, id=payload.class_id)
		new_member_subtype = MemberSubType.objects.create(
			member=new_member, f_class=class_, intake_year=payload.intake_year
		)

	if not payload.username:
		new_member.username = generate_username_password(new_member)[0]

	# create new Django User, change in settings.py
	if CREATE_USER_ON_POST:
		new_user = create_django_user(
			new_member,
			is_staff=(MemberSubType == HeadMaster or MemberSubType == Teacher),
		)
		new_member.username = new_user.username
	new_member.save()
	return new_member_subtype


######################
#     AuthBearer     #
######################


class AuthBearer(HttpBearer):
	def authenticate(self, request, token: str):
		if token == SECRET_KEY:
			return SECRET_KEY


######################
#   API for Members  #
######################


# GET alls Members
@router.get(
	"members",
	response=list[MemberOut],
	tags=["Member"],
	summary="List all members",
	description="Return List all members with pagination",
)
@paginate
def list_members(request):
	return [MemberOut.from_orm(member) for member in Member.objects.all()]


# GET Member by id
@router.get(
	"member/{int:member_id}",
	response={200: MemberOut, 404: DetailOut},
	tags=["Member"],
	summary="Get a member",
	description="Get a member by id",
)
def get_member(request, member_id: int):
	try:
		member = my_get_object_or_404(Member, id=member_id)
	except:
		return 404, {"detail": "Member does not exist."}
	return 200, MemberOut.from_orm(member)


# GET Members by school id
@router.get(
	"members/{int:school_id}",
	response={200: list[MemberOut], 404: DetailOut},
	tags=["Member"],
	summary="Get members by school",
	description="Get members by school id",
)
def get_members_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	return 200, [
		MemberOut.from_orm(member) for member in Member.objects.filter(school=school)
	]


# GET Member by username
@router.get(
	"member/{str:username}",
	response={200: MemberOut, 404: DetailOut},
	tags=["Member"],
	summary="Get a member",
	description="Get a member by username",
)
def get_member_by_username(request, username: str):
	try:
		member = my_get_object_or_404(Member, username=username)
	except:
		return 404, {"detail": "Member does not exist."}
	return 200, MemberOut.from_orm(member)


# GET alls Members of a school
@router.get(
	"school/{int:school_id}/members",
	response={200: list[MemberOut], 404: DetailOut},
	tags=["Member"],
	summary="List all members of a school",
	description="Return List all members of a school with pagination",
)
def list_members_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	return [
		MemberOut.from_orm(member) for member in Member.objects.filter(school=school)
	]


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
#   API for utils	 #
######################
