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
	StudentIn,
	StudentOut,
	StudentPut,
	StudentPatch,
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
#  API for Students  #
######################


# GET alls Students
@router.get(
	"students",
	response=list[StudentOut],
	tags=["Student"],
	summary="List all Students",
	description="Return List all Students with pagination",
)
@paginate
def list_students(request):
	return [StudentOut.from_orm(student) for student in Student.objects.all()]


# GET Student by id
@router.get(
	"student/{int:student_id}",
	response={200: StudentOut, 404: DetailOut},
	tags=["Student"],
	summary="Get a Student",
	description="Get a Student by id",
)
def get_student(request, student_id: int):
	try:
		student = my_get_object_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	return 200, StudentOut.from_orm(student)


# POST Student
@router.post(
	"students",
	response={200: OkOut, 409: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Student"],
	summary="Create a Student",
	description="Create a Student",
)
def create_student(request, payload: StudentIn = Form(...)):
	new_student = create_memberSubType("ST", payload)
	if new_student == 409:
		return 409, {"detail": "Username already exists."}
	if new_student == 4041:
		return 404, {"detail": "School does not exist."}
	if new_student == 4043:
		return 404, {"detail": "Class does not exist."}
	return 200, {
		"detail": "Student sucessfully created.",
		"model": StudentOut.from_orm(new_student),
	}


# PUT Student by id
@router.put(
	"student/{int:student_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Student"],
	summary="Update a Student",
	description="Update a Student by id",
)
def update_student(request, student_id: int, payload: StudentPut = Form(...)):
	try:
		student = my_get_object_for_update_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	for attr, value in payload.dict().items():
		if attr == "personal_info":
			for attr, value in payload.personal_info.dict().items():
				setattr(student.member.personal_info, attr, value)
		elif attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {"detail": "School does not exist."}
			setattr(student.member, attr, school)
		elif attr == "class_id":
			try:
				class_ = my_get_object_or_404(Class, id=payload.class_id)
			except:
				return 404, {"detail": "Class does not exist."}
			setattr(student, attr, class_)
		else:
			setattr(student, attr, value)
	student.member.personal_info.save()
	student.member.save()
	student.save()
	return 200, {
		"detail": "Student sucessfully updated.",
		"model": StudentOut.from_orm(student),
	}


# PATCH Student by id
@router.patch(
	"student/{int:student_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Student"],
	summary="Update a Student",
	description="Update a Student by id",
)
def patch_student(request, student_id: int, payload: StudentPatch = Form(...)):
	try:
		student = my_get_object_for_update_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	for attr, value in payload.dict(exclude_unset=True).items():
		if attr == "personal_info":
			for attr, value in payload.personal_info.dict(exclude_unset=True).items():
				setattr(student.member.personal_info, attr, value)
		elif attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=payload.school_id)
			except:
				return 404, {"detail": "School does not exist."}
			setattr(student.member, attr, school)
		elif attr == "class_id":
			try:
				class_ = my_get_object_or_404(Class, id=payload.class_id)
			except:
				return 404, {"detail": "Class does not exist."}
			setattr(student, attr, class_)
		else:
			setattr(student, attr, value)
	student.member.personal_info.save()
	student.member.save()
	student.save()
	return 200, {
		"detail": "Student sucessfully patched.",
		"model": StudentOut.from_orm(student),
	}


# DELETE Student by id
@router.delete(
	"student/{int:student_id}",
	response={200: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["Student"],
	summary="Delete a Student",
	description="Delete a Student by id",
)
def delete_student(request, student_id: int):
	try:
		student = my_get_object_or_404(Student, id=student_id)
	except:
		return 404, {"detail": "Student does not exist."}
	delete_memberSubType(student)
	return 200, {"detail": f"Student with id {student_id} sucessfully deleted."}


# GET alls Students by School id
@router.get(
	"school/{int:school_id}/students",
	response={200: list[StudentOut], 404: DetailOut},
	tags=["Student"],
	summary="List all Students by School id",
	description="Return List all Students by School id with pagination",
)
def list_students_by_school(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	return 200, [
		StudentOut.from_orm(student)
		for student in Student.objects.filter(member__school=school)
	]


# GET alls Students by Class id
@router.get(
	"class/{int:class_id}/students",
	response={200: list[StudentOut], 404: DetailOut},
	tags=["Student"],
	summary="List all Students by Class id",
	description="Return List all Students by Class id with pagination",
)
def list_students_by_class(request, class_id: int):
	try:
		class_ = my_get_object_or_404(Class, id=class_id)
	except:
		return 404, {"detail": "Class does not exist."}
	return 200, [
		StudentOut.from_orm(student)
		for student in Student.objects.filter(f_class=class_)
	]
