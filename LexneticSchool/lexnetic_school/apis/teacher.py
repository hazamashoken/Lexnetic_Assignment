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
	TeacherIn,
	TeacherOut,
	TeacherPut,
	TeacherPatch,
)

from lexnetic_school.api import (
	my_get_object_for_update_or_404,
	my_get_object_or_404,
	AuthBearer,
	delete_memberSubType,
	create_memberSubType,
	my_without_keys,
)

router = Router()

######################
#  API for Teachers  #
######################


# GET alls Teachers
@router.get(
	"teachers",
	response=list[TeacherOut],
	tags=["Teacher"],
	summary="List all Teachers",
	description="Return List all Teachers with pagination",
)
@paginate
def list_teachers(request):
	return [TeacherOut.from_orm(teacher) for teacher in Teacher.objects.all()]


# GET Teacher by id
@router.get(
	"teacher/{int:teacher_id}",
	response={200: TeacherOut, 404: DetailOut},
	tags=["Teacher"],
	summary="Get a Teacher",
	description="Get a Teacher by id",
)
def get_teacher(request, teacher_id: int):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {"detail": "Teacher does not exist."}
	return 200, TeacherOut.from_orm(teacher)


# POST Teacher
@router.post(
	"teachers",
	response={200: OkOut, 409: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Teacher"],
	summary="Create a Teacher",
	description="Create a Teacher",
)
def create_teacher(request, payload: TeacherIn = Form(...)):
	new_teacher = create_memberSubType("TE", payload)
	if new_teacher == 4041:
		return 404, {"detail": "School does not exist."}
	if new_teacher == 404:
		return 404, {"detail": "There is already a Teacher for this school."}
	if new_teacher == 409:
		return 409, {"detail": "This username already exist."}
	return 200, {
		"detail": "Teacher sucessfully created.",
		"model": TeacherOut.from_orm(new_teacher),
	}


# PUT Teacher by id
@router.put(
	"teacher/{int:teacher_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Teacher"],
	summary="Update a Teacher",
	description="Update a Teacher by id",
)
def update_teacher(request, teacher_id: int, payload: TeacherPut = Form(...)):
	try:
		teacher = my_get_object_for_update_or_404(Teacher, id=teacher_id)
	except:
		return 404, {"detail": "Teacher does not exist."}
	for attr, value in payload.dict().items():
		if attr == "personal_info":
			for attr2, value2 in payload.personal_info.dict().items():
				setattr(teacher.member.personal_info, attr2, value2)
		else:
			setattr(teacher, attr, value)
	teacher.member.personal_info.save()
	teacher.member.save()
	teacher.save()
	return 200, {
		"detail": "Teacher sucessfully updated.",
		"model": TeacherOut.from_orm(teacher),
	}


# PATCH Teacher by id
@router.patch(
	"teacher/{int:teacher_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Teacher"],
	summary="Update a Teacher",
	description="Update a Teacher by id",
)
def patch_teacher(request, teacher_id: int, payload: TeacherPatch = Form(...)):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {"detail": "Teacher does not exist."}
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == "personal_info":
			for attr2, value2 in value.items():
				if value2:
					setattr(teacher.member.personal_info, attr2, value2)
		else:
			setattr(teacher, attr, value)
	teacher.member.personal_info.save()
	teacher.member.save()
	teacher.save()
	return 200, {
		"detail": "Teacher sucessfully patched.",
		"model": TeacherOut.from_orm(teacher),
	}


# DELETE Teacher by id
@router.delete(
	"teacher/{int:teacher_id}",
	response={200: dict, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Teacher"],
	summary="Delete a Teacher",
	description="Delete a Teacher by id",
)
def delete_teacher(request, teacher_id: int):
	try:
		teacher = my_get_object_or_404(Teacher, id=teacher_id)
	except:
		return 404, {"detail": "Teacher does not exist."}
	delete_memberSubType(teacher)
	return 200, {"detail": f"Teacher with id {teacher_id} sucessfully deleted."}


# GET alls Teachers by school id
@router.get(
	"school/{int:school_id}/teachers",
	response={200: list[TeacherOut], 404: DetailOut},
	tags=["Teacher"],
	summary="List all Teachers by school id",
	description="Return List all Teachers by school id with pagination",
)
def list_teachers_by_school_id(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	return 200, [
		TeacherOut.from_orm(teacher)
		for teacher in Teacher.objects.filter(member__school=school)
	]
