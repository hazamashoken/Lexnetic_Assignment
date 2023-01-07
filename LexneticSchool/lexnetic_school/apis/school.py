from ninja import Router, ModelSchema, Form
from ninja.pagination import paginate
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.contrib.auth.models import User
from LexneticSchool.settings import DEFAULT_PASSWORD, SECRET_KEY, CREATE_USER_ON_POST

from lexnetic_school.models import Class, Student, Teacher, School, HeadMaster, PersonalInfo, Member
from lexnetic_school.schemas import \
	OkOut, DetailOut,\
	SchoolIn, SchoolOut, SchoolPatch

from lexnetic_school.api import \
	my_get_object_for_update_or_404,\
	my_get_object_or_404,\
	AuthBearer,\
	delete_memberSubType,\
	create_memberSubType,\
	my_without_keys

router = Router()

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
