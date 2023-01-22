from ninja import Router, ModelSchema, Form
from ninja.pagination import paginate
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.contrib.auth.models import User
from LexneticSchool.settings import DEFAULT_PASSWORD, SECRET_KEY, CREATE_USER_ON_POST

from lexnetic_school.models.models import (
	Class,
	Student,
	Teacher,
	School,
	HeadMaster,
	PersonalInfo,
	Member,
)
from lexnetic_school.models.schemas import (
	OkOut,
	DetailOut,
	ClassIn,
	ClassOut,
	ClassPut,
	ClassPatch,
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
#   API for Classes  #
######################


# GET alls Classes
@router.get(
	path="classes",
	response=list[ClassOut],
	tags=["Class"],
	summary="List all Classes",
	description="Return List all Classes with pagination",
)
@paginate
def list_classes(request):
	return [ClassOut.from_orm(class_) for class_ in Class.objects.all()]


# GET Class by id
@router.get(
	path="class/{int:class_id}",
	response={200: ClassOut, 404: DetailOut},
	tags=["Class"],
	summary="Get a Class",
	description="Get a Class by id",
)
def get_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	return 200, ClassOut.from_orm(class_)


# POST Class
@router.post(
	path="classes",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Class"],
	summary="Create a Class",
	description="Create a Class",
)
def create_class(request, payload: ClassIn = Form(...)):
	try:
		teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
	except:
		return 404, {"detail": "Teacher does not exist."}
	try:
		school = my_get_object_or_404(School, id=payload.school_id)
	except:
		return 404, {"detail": "School does not exist."}
	new_class_info = my_without_keys(payload.dict(), ["teacher_id", "school_id"])
	new_class = Class.objects.create(teacher=teacher, school=school, **new_class_info)
	return 200, {
		"detail": "Class sucessfully created.",
		"model": ClassOut.from_orm(new_class),
	}


# PUT Class by id
@router.put(
	path="class/{int:class_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Class"],
	summary="Update a Class",
	description="Update a Class by id",
)
def update_class(request, class_id: int, payload: ClassPut = Form(...)):
	try:
		class_ = my_get_object_for_update_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	for attr, value in payload.dict().items():
		if attr == "teacher_id":
			try:
				teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
			except:
				return 404, {"detail": "Teacher does not exist."}
			setattr(class_, "teacher", teacher)
		elif attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {"detail": "School does not exist."}
			setattr(class_, "school", school)
		else:
			setattr(class_, attr, value)
	class_.save()
	return 200, {
		"detail": "Class sucessfully updated.",
		"model": ClassOut.from_orm(class_),
	}


# PATCH Class by id
@router.patch(
	path="class/{int:class_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Class"],
	summary="Update a Class",
	description="Update a Class by id",
)
def patch_class(request, class_id: int, payload: ClassPatch = Form(...)):
	try:
		class_ = my_get_object_for_update_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == "teacher_id":
			try:
				teacher = my_get_object_or_404(Teacher, id=payload.teacher_id)
			except:
				return 404, {"detail": "Teacher does not exist."}
			setattr(class_, attr, teacher)
		elif attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {"detail": "School does not exist."}
			setattr(class_, attr, school)
		else:
			setattr(class_, attr, value)
	class_.save()
	return 200, {"detail": "Class sucessfully patched.", "model": ClassOut.from_orm(class_)}


# DELETE Class by id
@router.delete(
	path="class/{int:class_id}",
	response={200: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Class"],
	summary="Delete a Class",
	description="Delete a Class by id",
)
def delete_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	for student in Student.objects.filter(f_class=class_):
		delete_memberSubType(student)
	class_.delete()
	return 200, {"detail": f"Class with id {class_id} sucessfully deleted."}


# GET alls Classes by School id
@router.get(
	path="school/{int:school_id}/classes",
	response={200: list[ClassOut], 404: DetailOut},
	tags=["Class"],
	summary="List all Classes by School id",
	description="Return List all Classes by School id with pagination",
)
def list_classes_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	if not Class.objects.filter(school=school).exists():
		return 404, {"detail": "No Classes found."}
	return 200, [
		ClassOut.from_orm(class_) for class_ in Class.objects.filter(school=school)
	]
