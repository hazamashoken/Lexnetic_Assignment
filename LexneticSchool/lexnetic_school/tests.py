from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.http import Http404
from django.test import Client
from ninja import Form

from lexnetic_school.api import (
	generate_username_password,
	create_memberSubType,
	get_subtype,
	create_django_user,
	list_members,
	get_member,
)

from lexnetic_school.apis.class_ import (
	list_classes,
	get_class,
	create_class,
	update_class,
	patch_class,
)
from lexnetic_school.apis.headmaster import (
	list_headmasters,
	get_headmaster,
	create_headmaster,
	update_headmaster,
	patch_headmaster,
)
from lexnetic_school.apis.school import (
	list_schools,
	get_school,
	create_school,
	update_school,
	patch_school,
)
from lexnetic_school.apis.student import (
	list_students,
	get_student,
	create_student,
	update_student,
	patch_student,
)
from lexnetic_school.apis.teacher import (
	list_teachers,
	get_teacher,
	create_teacher,
	update_teacher,
	patch_teacher,
)

from lexnetic_school.schemas import (
	HeadMasterOut,
	HeadMasterIn,
	HeadMasterPut,
	HeadMasterPatch,
	SchoolOut,
	SchoolIn,
	SchoolPatch,
	ClassOut,
	ClassIn,
	ClassPatch,
	TeacherOut,
	TeacherIn,
	TeacherPut,
	TeacherPatch,
	StudentOut,
	StudentIn,
	StudentPut,
	StudentPatch,
	MemberOut,
	MemberIn,
	MemberPatch,
	PersonalInfoOut,
	PersonalInfoIn,
	PersonalInfoPatch,
)

from lexnetic_school.models import (
	Member,
	PersonalInfo,
	Student,
	Teacher,
	HeadMaster,
	School,
	Class,
)

# Create your tests here.

######################
# DATA SETS FOR TEST #
######################

SCHOOL_IN_1 = SchoolIn(
	name="Lexnetic School",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_IN_1_PUT = SchoolIn(
	name="42 Bangkok",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_IN_1_PATCH = SchoolPatch(
	name="12 Bangkok",
)

SCHOOL_IN_2 = SchoolIn(
	name="Lexnetic School",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_1 = School(
	id="1",
	name="Lexnetic School",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_1_PUT = School(
	id="1",
	name="42 Bangkok",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_1_PATCH = School(
	id="1",
	name="12 Bangkok",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

SCHOOL_2 = School(
	id="2",
	name="Lexnetic School",
	address="Bangkok Thailand",
	email="lexsch@gmail.com",
	phone="0812345678",
)

PERSONAL_INFO_IN_1 = PersonalInfoIn(
	first_name="Thanapol",
	middle_name="Khonvum",
	last_name="Liangsoonthornsit",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_IN_2 = PersonalInfoIn(
	first_name="Armel",
	middle_name="Khonvum",
	last_name="Oudin",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_IN_3 = PersonalInfoIn(
	first_name="Samboon",
	middle_name="Khonvum",
	last_name="Poolprasart",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_IN_4 = PersonalInfoIn(
	first_name="Thanapat",
	middle_name="Khonvum",
	last_name="Liangsoonthornsit",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_1 = PersonalInfo(
	first_name="Thanapol",
	middle_name="Khonvum",
	last_name="Liangsoonthornsit",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_1_1 = PersonalInfo(
	first_name="Thanapol",
	middle_name="Khonvum",
	last_name="Liangsoonthornsit",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_2 = PersonalInfo(
	first_name="Armel",
	middle_name="Khonvum",
	last_name="Oudin",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_3 = PersonalInfo(
	first_name="Samboon",
	middle_name="Khonvum",
	last_name="Poolprasart",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

PERSONAL_INFO_4 = PersonalInfo(
	first_name="Thanapat",
	middle_name="Khonvum",
	last_name="Liangsoonthornsit",
	email="earth@gmail.com",
	phone="0812345678",
	address="Bangkok",
)

HEADMASTER_IN_1_SCH_1 = HeadMasterIn(
	school_id="1", username="tliangso", personal_info=PERSONAL_INFO_IN_1
)

HEADMASTER_IN_1_SCH_1_PUT = HeadMasterIn(
	school_id="1", personal_info=PERSONAL_INFO_IN_2
)

HEADMASTER_IN_1_SCH_1_PATCH = HeadMasterPatch(
	school_id="1",
	personal_info=PersonalInfoPatch(
		first_name="Thanapat",
	),
)

HEADMASTER_IN_1_SCH_2_PUT = HeadMasterIn(
	school_id="2", personal_info=PERSONAL_INFO_IN_1
)

HEADMASTER_IN_1_SCH_2 = HeadMasterIn(
	school_id="2", username="tliangso", personal_info=PERSONAL_INFO_IN_1
)

HEADMASTER_IN_2_SCH_1 = HeadMasterIn(
	school_id="1",
	username="khovnum",
	personal_info=PERSONAL_INFO_IN_4,
)

HEADMASTER_IN_2_SCH_2 = HeadMasterIn(
	school_id="2",
	username="khovnum",
	personal_info=PERSONAL_INFO_IN_4,
)

HEADMASTER_1_SCH_1 = HeadMaster(
	id="1",
	school=SCHOOL_1,
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Head Master",
		personal_info=PERSONAL_INFO_1,
	),
)

HEADMASTER_1_SCH_1_PUT = HeadMaster(
	id="1",
	school=SCHOOL_1,
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Head Master",
		personal_info=PERSONAL_INFO_2,
	),
)

HEADMASTER_1_SCH_1_PATCH = HeadMaster(
	id="1",
	school=SCHOOL_1,
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Head Master",
		personal_info=PERSONAL_INFO_4,
	),
)

TEACHER_IN_1_SCH_1 = TeacherIn(
	school_id="1", username="tliangso", personal_info=PERSONAL_INFO_IN_1
)

TEACHER_IN_1_SCH_1_PUT = TeacherIn(
	school_id="1", username="tliangso", personal_info=PERSONAL_INFO_IN_2
)

TEACHER_IN_2_SCH_1_PATCH = TeacherPatch(
	personal_info=PersonalInfoPatch(
		first_name="Thanapat",
	),
)

TEACHER_IN_1_SCH_2 = TeacherIn(
	school_id="2", username="tliangso", personal_info=PERSONAL_INFO_IN_1
)

TEACHER_IN_2_SCH_1 = TeacherIn(
	school_id="1", username="aoudin", personal_info=PERSONAL_INFO_IN_2
)

TEACHER_1_SCH_1 = Teacher(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Teacher",
		personal_info=PERSONAL_INFO_1,
	),
)

TEACHER_1_SCH_1_PUT = Teacher(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Teacher",
		personal_info=PERSONAL_INFO_2,
	),
)

TEACHER_2_SCH_1_PATCH = Teacher(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="aoudin",
		role="Teacher",
		personal_info=PersonalInfo(
			first_name="Thanapat",
			middle_name="Khonvum",
			last_name="Oudin",
			email="earth@gmail.com",
			phone="0812345678",
			address="Bangkok",
		),
	),
)

TEACHER_2_SCH_1 = Teacher(
	id="2",
	member=Member(
		school=SCHOOL_1,
		username="aoudin",
		role="Teacher",
		personal_info=PERSONAL_INFO_2,
	),
)

TEACHER_2_SCH_1_ID_1 = Teacher(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="aoudin",
		role="Teacher",
		personal_info=PERSONAL_INFO_2,
	),
)

CLASS_IN_1_TE_1_SCH_1 = ClassIn(teacher_id="1", school_id="1", year="2563")

CLASS_IN_1_TE_1_SCH_1_PUT = ClassIn(teacher_id="1", school_id="1", year="2566")

CLASS_IN_1_TE_1_SCH_1_PATCH = ClassPatch(year="1000")

CLASS_IN_1_TE_1_SCH_2 = ClassIn(teacher_id="1", school_id="2", year="2563")

CLASS_IN_1_TE_2_SCH_1 = ClassIn(teacher_id="2", school_id="1", year="2563")

CLASS_1_TE_1_SCH_1 = Class(
	id="1", teacher=TEACHER_1_SCH_1, school=SCHOOL_1, year="2563"
)

CLASS_1_TE_1_SCH_1_PUT = Class(
	id="1", teacher=TEACHER_2_SCH_1_ID_1, school=SCHOOL_1, year="2566"
)

CLASS_1_TE_1_SCH_1_PATCH = Class(
	id="1", teacher=TEACHER_2_SCH_1_ID_1, school=SCHOOL_1, year="1000"
)

CLASS_IN_2_TE_1_SCH_1 = ClassIn(teacher_id="2", school_id="1", year="2563")

CLASS_1_TE_2_SCH_1 = Class(
	id="1", teacher=TEACHER_2_SCH_1, school=SCHOOL_1, year="2563"
)

STUDENT_IN_1_CL_1_SCH_1 = StudentIn(
	class_id="1", school_id="1", intake_year="2563", personal_info=PERSONAL_INFO_IN_1
)

STUDENT_IN_3_CL_1_SCH_1_PUT = StudentIn(
	class_id="1", school_id="1", intake_year="2563", personal_info=PERSONAL_INFO_IN_3
)

STUDENT_3_CL_1_SCH_1_PUT = Student(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="spoolpra",
		role="Student",
		personal_info=PERSONAL_INFO_3,
	),
	f_class=CLASS_1_TE_1_SCH_1,
	intake_year="2563",
)

STUDENT_IN_2_CL_1_SCH_1_WITH_USERNAME = StudentIn(
	class_id="1",
	school_id="1",
	intake_year="2563",
	username="aoudin",
	personal_info=PERSONAL_INFO_IN_2,
)


STUDENT_IN_1_CL_1_SCH_2 = StudentIn(
	class_id="1", school_id="2", intake_year="2563", personal_info=PERSONAL_INFO_IN_1
)

STUDENT_IN_1_CL_2_SCH_1 = StudentIn(
	class_id="2", school_id="1", intake_year="2563", personal_info=PERSONAL_INFO_IN_1
)

STUDENT_IN_2_CL_1_SCH_1 = StudentIn(
	class_id="1", school_id="1", intake_year="2563", personal_info=PERSONAL_INFO_IN_2
)

STUDENT_IN_3_CL_1_SCH_1 = StudentIn(
	class_id="1", school_id="1", intake_year="2563", personal_info=PERSONAL_INFO_IN_3
)

STUDENT_IN_3_CL_1_SCH_1_PATCH = StudentPatch(
	intake_year="1000"
)

STUDENT_1_CL_1_SCH_1 = Student(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="tliangso",
		role="Student",
		personal_info=PERSONAL_INFO_1,
	),
	f_class=CLASS_1_TE_1_SCH_1,
	intake_year="2563",
)

STUDENT_2_CL_1_SCH_1 = Student(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="aoudin",
		role="Student",
		personal_info=PERSONAL_INFO_2,
	),
	f_class=CLASS_1_TE_1_SCH_1,
	intake_year="2563",
)

STUDENT_3_CL_1_SCH_1 = Student(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="spoolpra",
		role="Student",
		personal_info=PERSONAL_INFO_3,
	),
	f_class=CLASS_1_TE_1_SCH_1,
	intake_year="2563",
)

STUDENT_3_CL_1_SCH_1_PATCH = Student(
	id="1",
	member=Member(
		school=SCHOOL_1,
		username="spoolpra",
		role="Student",
		personal_info=PERSONAL_INFO_3,
	),
	f_class=CLASS_1_TE_1_SCH_1,
	intake_year="1000",
)


# test username and password generation with different name
class GenerateUsernamePasswordTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_generate_username_password_1(self):
		personal_info = PERSONAL_INFO_1
		personal_info.save()

		member = Member(personal_info=personal_info, role="ST", school_id=1)
		username, password = generate_username_password(member)
		member.username = username
		member.save()

		self.assertEqual(username, "tliangso")
		self.assertEqual(password, "@42Bangkok")

	def test_generate_username_password_2(self):
		personal_info = PERSONAL_INFO_2
		personal_info.save()

		member = Member(personal_info=personal_info, role="ST", school_id=1)
		username, password = generate_username_password(member)
		member.username = username
		member.save()

		self.assertEqual(username, "aoudin")
		self.assertEqual(password, "@42Bangkok")

	def test_generate_username_password_3(self):
		personal_info = PERSONAL_INFO_3
		personal_info.save()

		member = Member(personal_info=personal_info, role="ST", school_id=1)
		username, password = generate_username_password(member)
		member.username = username
		member.save()

		self.assertEqual(username, "spoolpra")
		self.assertEqual(password, "@42Bangkok")

	def test_generate_username_password_with_duplicate_username(self):
		personal_info_1 = PERSONAL_INFO_1
		personal_info_1.save()
		personal_info_2 = PERSONAL_INFO_1_1
		personal_info_2.save()

		member_1 = Member(personal_info=personal_info_1, role="ST", school_id=1)
		username_1, password_1 = generate_username_password(member_1)
		member_1.username = username_1
		member_1.save()

		member_2 = Member(personal_info=personal_info_2, role="ST", school_id=1)
		username_2, password_2 = generate_username_password(member_2)
		member_2.username = username_2
		member_2.save()

		self.assertEqual(username_1, "tliangso")
		self.assertEqual(password_1, "@42Bangkok")
		self.assertEqual(username_2, "thliangs")
		self.assertEqual(password_2, "@42Bangkok")


# test create member subtype
class GetSubTypeTest(TestCase):
	def test_get_subtype(self):
		studentType = get_subtype("ST")
		teacherType = get_subtype("TE")
		headmasterType = get_subtype("HM")
		self.assertEqual(studentType, Student)
		self.assertEqual(teacherType, Teacher)
		self.assertEqual(headmasterType, HeadMaster)


# test create Django user
class CreateDjangoUserTest(TestCase):
	def test_create_django_user_with_no_username(self):
		personal_info = PERSONAL_INFO_1
		member = Member(personal_info=personal_info, role="ST", school_id=1)
		django_user = create_django_user(member, is_staff=False)
		self.assertEqual(type(django_user), User)
		self.assertEqual(django_user.username, "tliangso")

	def test_create_django_user_with_username(self):
		personal_info = PERSONAL_INFO_1
		member = Member(
			personal_info=personal_info, role="ST", school_id=1, username="earth"
		)
		django_user = create_django_user(member, is_staff=False)
		self.assertEqual(type(django_user), User)
		self.assertEqual(django_user.username, "earth")


# test create school
class CreateSchoolTest(TestCase):
	def test_create_school(self):
		school = create_school(None, payload=SCHOOL_IN_1)
		self.assertEqual(
			school,
			(
				200,
				{
					"detail": "School sucessfully created.",
					"model": SchoolOut.from_orm(SCHOOL_1),
				},
			),
		)


# test create headmaster on different conditions and error output
class CreateHeadMasterTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_create_headmaster(self):
		headmaster = create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		self.assertEqual(
			headmaster,
			(
				200,
				{
					"detail": "HeadMaster sucessfully created.",
					"model": HeadMasterOut.from_orm(HEADMASTER_1_SCH_1),
				},
			),
		)

	def test_create_headmaster_no_school(self):
		headmaster = create_headmaster(None, payload=HEADMASTER_IN_1_SCH_2)
		self.assertEqual(headmaster, (404, {"detail": "School does not exist."}))

	def test_create_headmaster_school_with_headmaster(self):
		headmaster = create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		headmaster = create_headmaster(None, payload=HEADMASTER_IN_2_SCH_1)
		self.assertEqual(
			headmaster, (409, {"detail": "School already has a HeadMaster."})
		)

	def test_create_headmaster_username_exist(self):
		create_school(None, payload=SCHOOL_IN_2)
		headmaster_1 = create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		headmaster_2 = create_headmaster(None, payload=HEADMASTER_IN_1_SCH_2)
		self.assertEqual(
			headmaster_1,
			(
				200,
				{
					"detail": "HeadMaster sucessfully created.",
					"model": HeadMasterOut.from_orm(HEADMASTER_1_SCH_1),
				},
			),
		)
		self.assertEqual(
			headmaster_2, (409, {"detail": "This username already exist."})
		)


# test create teacher on different conditions and error output
class CreateTeacherTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_create_teacher(self):
		teacher = create_teacher(None, payload=TEACHER_IN_1_SCH_1)
		self.assertEqual(
			teacher,
			(
				200,
				{
					"detail": "Teacher sucessfully created.",
					"model": TeacherOut.from_orm(TEACHER_1_SCH_1),
				},
			),
		)

	def test_create_teacher_no_school(self):
		teacher = create_teacher(None, payload=TEACHER_IN_1_SCH_2)
		self.assertEqual(teacher, (404, {"detail": "School does not exist."}))

	def test_create_teacher_username_exist(self):
		create_school(None, payload=SCHOOL_IN_2)
		teacher_1 = create_teacher(None, payload=TEACHER_IN_1_SCH_1)
		teacher_2 = create_teacher(None, payload=TEACHER_IN_1_SCH_2)
		self.assertEqual(
			teacher_1,
			(
				200,
				{
					"detail": "Teacher sucessfully created.",
					"model": TeacherOut.from_orm(TEACHER_1_SCH_1),
				},
			),
		)
		self.assertEqual(teacher_2, (409, {"detail": "This username already exist."}))


class CreateClassTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)

	def test_create_class(self):
		class_ = create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)
		self.assertEqual(
			class_,
			(
				200,
				{
					"detail": "Class sucessfully created.",
					"model": ClassOut.from_orm(CLASS_1_TE_1_SCH_1),
				},
			),
		)

	def test_create_class_no_school(self):
		class_ = create_class(None, payload=CLASS_IN_1_TE_1_SCH_2)
		self.assertEqual(class_, (404, {"detail": "School does not exist."}))

	def test_create_class_no_teacher(self):
		class_ = create_class(None, payload=CLASS_IN_1_TE_2_SCH_1)
		self.assertEqual(class_, (404, {"detail": "Teacher does not exist."}))


class CreateStudentTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)

	def test_create_student(self):
		student = create_student(None, payload=STUDENT_IN_2_CL_1_SCH_1)
		self.assertEqual(
			student,
			(
				200,
				{
					"detail": "Student sucessfully created.",
					"model": StudentOut.from_orm(STUDENT_2_CL_1_SCH_1),
				},
			),
		)

	def test_create_student_no_school(self):
		student = create_student(None, payload=STUDENT_IN_1_CL_1_SCH_2)
		self.assertEqual(student, (404, {"detail": "School does not exist."}))

	def test_create_student_no_class(self):
		student = create_student(None, payload=STUDENT_IN_1_CL_2_SCH_1)
		self.assertEqual(student, (404, {"detail": "Class does not exist."}))

	def test_create_student_username_exist(self):
		student_1 = create_student(None, payload=STUDENT_IN_2_CL_1_SCH_1_WITH_USERNAME)
		student_2 = create_student(None, payload=STUDENT_IN_2_CL_1_SCH_1_WITH_USERNAME)
		self.assertEqual(
			student_1,
			(
				200,
				{
					"detail": "Student sucessfully created.",
					"model": StudentOut.from_orm(STUDENT_2_CL_1_SCH_1),
				},
			),
		)
		self.assertEqual(student_2, (409, {"detail": "Username already exists."}))


class GETSchoolTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_get_school(self):
		school = get_school(None, school_id=1)
		self.assertEqual(school, (200, SchoolOut.from_orm(SCHOOL_1)))

	def test_get_school_no_school(self):
		school = get_school(None, school_id=2)
		self.assertEqual(school, (404, {"detail": "School does not exist."}))


class GETHeadMasterTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)

	def test_get_headmaster(self):
		headmaster = get_headmaster(None, headmaster_id=1)
		self.assertEqual(headmaster, (200, HeadMasterOut.from_orm(HEADMASTER_1_SCH_1)))

	def test_get_headmaster_no_headmaster(self):
		headmaster = get_headmaster(None, headmaster_id=2)
		self.assertEqual(headmaster, (404, {"detail": "HeadMaster does not exist."}))


class GETTeacherTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)

	def test_get_teacher(self):
		teacher = get_teacher(None, teacher_id=1)
		self.assertEqual(teacher, (200, TeacherOut.from_orm(TEACHER_1_SCH_1)))

	def test_get_teacher_no_teacher(self):
		teacher = get_teacher(None, teacher_id=2)
		self.assertEqual(teacher, (404, {"detail": "Teacher does not exist."}))


class GETClassTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)

	def test_get_class(self):
		class_ = get_class(None, class_id=1)
		self.assertEqual(class_, (200, ClassOut.from_orm(CLASS_1_TE_1_SCH_1)))

	def test_get_class_no_class(self):
		class_ = get_class(None, class_id=2)
		self.assertEqual(class_, (404, {"detail": "Class does not exist."}))


class GETStudentTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)
		create_student(None, payload=STUDENT_IN_2_CL_1_SCH_1)

	def test_get_student(self):
		student = get_student(None, student_id=1)
		self.assertEqual(student, (200, StudentOut.from_orm(STUDENT_2_CL_1_SCH_1)))

	def test_get_student_no_student(self):
		student = get_student(None, student_id=2)
		self.assertEqual(student, (404, {"detail": "Student does not exist."}))


class GETMemberTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)
		create_student(None, payload=STUDENT_IN_3_CL_1_SCH_1)

	def test_get_member(self):
		member = get_member(None, member_id=1)
		member_out = MemberOut.from_orm(HEADMASTER_1_SCH_1.member)
		member_out.id = 1
		self.assertEqual(member, (200, member_out))

		member = get_member(None, member_id=2)
		member_out = MemberOut.from_orm(TEACHER_2_SCH_1.member)
		member_out.id = 2
		self.assertEqual(member, (200, member_out))

		member = get_member(None, member_id=3)
		member_out = MemberOut.from_orm(STUDENT_3_CL_1_SCH_1.member)
		member_out.id = 3
		self.assertEqual(member, (200, member_out))

	def test_get_member_no_member(self):
		member = get_member(None, member_id=9)
		self.assertEqual(member, (404, {"detail": "Member does not exist."}))


class PUTSchoolTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_put_school(self):
		school = update_school(None, school_id=1, payload=SCHOOL_IN_1_PUT)
		self.assertEqual(
			school,
			(
				200,
				{
					"detail": "School sucessfully updated.",
					"model": SchoolOut.from_orm(SCHOOL_1_PUT),
				},
			),
		)

	def test_put_school_no_school(self):
		school = update_school(None, school_id=2, payload=SCHOOL_IN_2)
		self.assertEqual(school, (404, {"detail": "School does not exist."}))


class PUTHeadMasterTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)

	def test_put_headmaster(self):
		headmaster = update_headmaster(
			None, headmaster_id=1, payload=HEADMASTER_IN_1_SCH_1_PUT
		)
		self.assertEqual(
			headmaster,
			(
				200,
				{
					"detail": "HeadMaster sucessfully updated.",
					"model": HeadMasterOut.from_orm(HEADMASTER_1_SCH_1_PUT),
				},
			),
		)

	def test_put_headmaster_no_headmaster(self):
		headmaster = update_headmaster(
			None, headmaster_id=2, payload=HEADMASTER_IN_2_SCH_1
		)
		self.assertEqual(headmaster, (404, {"detail": "HeadMaster does not exist."}))

	def test_put_headmaster_school_does_not_exist(self):
		headmaster = update_headmaster(
			None, headmaster_id=1, payload=HEADMASTER_IN_1_SCH_2
		)
		self.assertEqual(headmaster, (404, {"detail": "School does not exist."}))

	def test_put_headmaster_school_with_headmaster(self):
		create_school(None, payload=SCHOOL_IN_2)
		create_headmaster(None, payload=HEADMASTER_IN_2_SCH_2)
		headmaster = update_headmaster(
			None, headmaster_id=1, payload=HEADMASTER_IN_1_SCH_2_PUT
		)
		self.assertEqual(
			headmaster, (409, {"detail": "School already has a HeadMaster."})
		)


class PUTTeacherTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_teacher(None, payload=TEACHER_IN_1_SCH_1)

	def test_put_teacher(self):
		teacher = update_teacher(None, teacher_id=1, payload=TEACHER_IN_1_SCH_1_PUT)
		self.assertEqual(
			teacher,
			(
				200,
				{
					"detail": "Teacher sucessfully updated.",
					"model": TeacherOut.from_orm(TEACHER_1_SCH_1_PUT),
				},
			),
		)

	def test_put_teacher_no_teacher(self):
		teacher = update_teacher(None, teacher_id=2, payload=TEACHER_IN_2_SCH_1)
		self.assertEqual(teacher, (404, {"detail": "Teacher does not exist."}))


class PUTClassTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)

	def test_put_class(self):
		class_ = update_class(None, class_id=1, payload=CLASS_IN_1_TE_1_SCH_1_PUT)
		self.assertEqual(
			class_,
			(
				200,
				{
					"detail": "Class sucessfully updated.",
					"model": ClassOut.from_orm(CLASS_1_TE_1_SCH_1_PUT),
				},
			),
		)

	def test_put_class_no_class(self):
		class_ = update_class(None, class_id=2, payload=CLASS_IN_2_TE_1_SCH_1)
		self.assertEqual(class_, (404, {"detail": "Class does not exist."}))

	def test_put_class_teacher_does_not_exist(self):
		class_ = update_class(None, class_id=1, payload=CLASS_IN_1_TE_2_SCH_1)
		self.assertEqual(class_, (404, {"detail": "Teacher does not exist."}))


class PUTStudentTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)
		create_student(None, payload=STUDENT_IN_3_CL_1_SCH_1)

	def test_put_student(self):
		student = update_student(
			None, student_id=1, payload=STUDENT_IN_3_CL_1_SCH_1_PUT
		)
		self.assertEqual(
			student,
			(
				200,
				{
					"detail": "Student sucessfully updated.",
					"model": StudentOut.from_orm(STUDENT_3_CL_1_SCH_1_PUT),
				},
			),
		)

	def test_put_student_no_student(self):
		student = update_student(None, student_id=2, payload=STUDENT_IN_2_CL_1_SCH_1)
		self.assertEqual(student, (404, {"detail": "Student does not exist."}))

	def test_put_student_class_does_not_exist(self):
		student = update_student(None, student_id=1, payload=STUDENT_IN_1_CL_2_SCH_1)
		self.assertEqual(student, (404, {"detail": "Class does not exist."}))


class PATCHSchoolTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)

	def test_patch_school(self):
		school = patch_school(None, school_id=1, payload=SCHOOL_IN_1_PATCH)
		self.assertEqual(
			school,
			(
				200,
				{
					"detail": "School sucessfully patched.",
					"model": SchoolOut.from_orm(SCHOOL_1_PATCH),
				},
			),
		)

	def test_patch_school_no_school(self):
		school = patch_school(None, school_id=2, payload=SCHOOL_IN_2)
		self.assertEqual(school, (404, {"detail": "School does not exist."}))


class PATCHHeadMasterTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)

	def test_patch_headmaster(self):
		headmaster = patch_headmaster(
			None, headmaster_id=1, payload=HEADMASTER_IN_1_SCH_1_PATCH
		)
		self.assertEqual(
			headmaster,
			(
				200,
				{
					"detail": "HeadMaster sucessfully patched.",
					"model": HeadMasterOut.from_orm(HEADMASTER_1_SCH_1_PATCH),
				},
			),
		)

	def test_patch_headmaster_no_headmaster(self):
		headmaster = patch_headmaster(
			None, headmaster_id=2, payload=HEADMASTER_IN_2_SCH_1
		)
		self.assertEqual(headmaster, (404, {"detail": "HeadMaster does not exist."}))


class PATCHTeacherTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)

	def test_patch_teacher(self):
		teacher = patch_teacher(None, teacher_id=1, payload=TEACHER_IN_2_SCH_1_PATCH)
		self.assertEqual(
			teacher,
			(
				200,
				{
					"detail": "Teacher sucessfully patched.",
					"model": TeacherOut.from_orm(TEACHER_2_SCH_1_PATCH),
				},
			),
		)

	def test_patch_teacher_no_teacher(self):
		teacher = patch_teacher(None, teacher_id=2, payload=TEACHER_IN_1_SCH_1)
		self.assertEqual(teacher, (404, {"detail": "Teacher does not exist."}))

class PATCHClassTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)

	def test_patch_class(self):
		class_ = patch_class(None, class_id=1, payload=CLASS_IN_1_TE_1_SCH_1_PATCH)
		self.assertEqual(
			class_,
			(
				200,
				{
					"detail": "Class sucessfully patched.",
					"model": ClassOut.from_orm(CLASS_1_TE_1_SCH_1_PATCH),
				},
			),
		)

	def test_patch_class_no_class(self):
		class_ = patch_class(None, class_id=2, payload=CLASS_IN_2_TE_1_SCH_1)
		self.assertEqual(class_, (404, {"detail": "Class does not exist."}))

class PATCHStudentTest(TestCase):
	def setUp(self):
		create_school(None, payload=SCHOOL_IN_1)
		create_headmaster(None, payload=HEADMASTER_IN_1_SCH_1)
		create_teacher(None, payload=TEACHER_IN_2_SCH_1)
		create_class(None, payload=CLASS_IN_1_TE_1_SCH_1)
		create_student(None, payload=STUDENT_IN_3_CL_1_SCH_1)

	def test_patch_student(self):
		student = patch_student(
			None, student_id=1, payload=STUDENT_IN_3_CL_1_SCH_1_PATCH
		)
		self.assertEqual(
			student,
			(
				200,
				{
					"detail": "Student sucessfully patched.",
					"model": StudentOut.from_orm(STUDENT_3_CL_1_SCH_1_PATCH),
				},
			),
		)

	def test_patch_student_no_student(self):
		student = patch_student(None, student_id=2, payload=STUDENT_IN_2_CL_1_SCH_1)
		self.assertEqual(student, (404, {"detail": "Student does not exist."}))

	def test_patch_student_class_does_not_exist(self):
		student = patch_student(None, student_id=1, payload=STUDENT_IN_1_CL_2_SCH_1)
		self.assertEqual(student, (404, {"detail": "Class does not exist."}))
