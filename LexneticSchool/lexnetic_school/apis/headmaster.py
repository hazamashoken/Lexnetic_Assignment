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
	HeadMasterOut,
	HeadMasterPut,
	HeadMasterPatch,
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
# API for HeadMaster #
######################


# GET alls HeadsMasters
@router.get(
	path="headmasters",
	response=list[HeadMasterOut],
	tags=["HeadMaster"],
	summary="List all HeadMaster",
	description="Return List all HeadMaster with pagination",
)
@paginate
def list_headmasters(request):
	return [
		HeadMasterOut.from_orm(headmaster) for headmaster in HeadMaster.objects.all()
	]


# GET HeadMaster by id
@router.get(
	path="headmaster/{int:headmaster_id}",
	response={200: HeadMasterOut, 404: DetailOut},
	tags=["HeadMaster"],
	summary="Get a HeadMaster",
	description="Get a HeadMaster by id",
)
def get_headmaster(request, headmaster_id: int):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail": "HeadMaster does not exist."}
	return 200, HeadMasterOut.from_orm(headmaster)


# POST HeadMaster
@router.post(
	path="headmasters",
	response={200: OkOut, 409: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["HeadMaster"],
	summary="Create a HeadMaster",
	description="Create a HeadMaster",
)
def create_headmaster(request, payload: HeadMasterIn = Form(...)):
	new_headmaster = create_memberSubType("HM", payload)
	if new_headmaster == 4041:
		return 404, {"detail": "School does not exist."}
	if new_headmaster == 4042:
		return 409, {"detail": "School already has a HeadMaster."}
	if new_headmaster == 404:
		return 404, {"detail": "Role Error."}
	if new_headmaster == 409:
		return 409, {"detail": "This username already exist."}
	return 200, {
		"detail": "HeadMaster sucessfully created.",
		"model": HeadMasterOut.from_orm(new_headmaster),
	}


# PUT HeadMaster by id
@router.put(
	path="headmaster/{int:headmaster_id}",
	response={200: OkOut, 409: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["HeadMaster"],
	summary="Update a HeadMaster",
	description="Update a HeadMaster by id",
)
def update_headmaster(request, headmaster_id: int, payload: HeadMasterPut = Form(...)):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail": "HeadMaster does not exist."}
	for attr, value in payload.dict().items():
		if attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=value)
			except:
				return 404, {"detail": "School does not exist."}
			if HeadMaster.objects.filter(school=school).exists():
				if HeadMaster.objects.get(school=school).id != headmaster.id:
					return 409, {"detail": "School already has a HeadMaster."}
			headmaster.school = school
		elif attr == "personal_info":
			for attr2, value2 in value.items():
				setattr(headmaster.member.personal_info, attr2, value2)
	headmaster.member.personal_info.save()
	headmaster.member.save()
	headmaster.save()
	return 200, {
		"detail": "HeadMaster sucessfully updated.",
		"model": HeadMasterOut.from_orm(headmaster),
	}


# PATCH HeadMaster by id
@router.patch(
	path="headmaster/{int:headmaster_id}",
	response={200: OkOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["HeadMaster"],
	summary="Update a HeadMaster",
	description="Update a HeadMaster by id",
)
def patch_headmaster(request, headmaster_id: int, payload: HeadMasterPatch = Form(...)):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail": "HeadMaster does not exist."}
	for attr, value in payload.dict(exclude_unset=True, exclude_none=True).items():
		if attr == "school_id":
			try:
				school = my_get_object_or_404(School, id=value)
			except:
				return 404, {"detail": "School does not exist."}
			if HeadMaster.objects.filter(school=school).exists():
				if HeadMaster.objects.get(school=school).id != headmaster.id:
					return 409, {"detail": "School already has a HeadMaster."}
			headmaster.school = school
		elif attr == "personal_info":
			for attr2, value2 in payload.personal_info.dict(exclude_unset=True).items():
				setattr(headmaster.member.personal_info, attr2, value2)
	headmaster.member.personal_info.save()
	headmaster.member.save()
	headmaster.save()
	return 200, {
		"detail": "HeadMaster sucessfully patched.",
		"model": HeadMasterOut.from_orm(headmaster),
	}


# DELETE HeadMaster by id
@router.delete(
	path="headmaster/{int:headmaster_id}",
	response={200: DetailOut, 404: DetailOut},
	auth=AuthBearer(),
	tags=["HeadMaster"],
	summary="Delete a HeadMaster",
	description="Delete a HeadMaster by id",
)
def delete_headmaster(request, headmaster_id: int):
	try:
		headmaster = my_get_object_or_404(HeadMaster, id=headmaster_id)
	except:
		return 404, {"detail": "HeadMaster does not exist."}
	delete_memberSubType(headmaster)
	return 200, {"detail": f"HeadMaster with id {headmaster_id} sucessfully deleted."}


# GET HeadMaster by school id
@router.get(
	path="school/{int:school_id}/headmaster",
	response={200: HeadMasterOut, 404: DetailOut},
	tags=["HeadMaster"],
	summary="Get a HeadMaster by school id",
	description="Get a HeadMaster by school id",
)
def get_headmaster_by_school_id(request, school_id: int):
	try:
		school = my_get_object_or_404(School, id=school_id)
	except:
		return 404, {"detail": "School does not exist."}
	try:
		headmaster = my_get_object_or_404(HeadMaster, school=school)
	except:
		return 404, {"detail": "HeadMaster does not exist."}
	return 200, HeadMasterOut.from_orm(headmaster)
