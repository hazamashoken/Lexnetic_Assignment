from django.test import TestCase
from django.contrib.auth.models import User

from lexnetic_school.api import \
	generate_username_password,\
	get_subtype, \
	create_django_user

from lexnetic_school.schemas import Member, PersonalInfo, Student, Teacher, HeadMaster
# Create your tests here.

class GenerateUsernamePasswordTest(TestCase):
	def test_generate_username_password_1(self):
		personal_info = PersonalInfo(
				first_name="Thanapol",
				middle_name="Khonvum",
				last_name="Liangsoonthornsit",
				email="earth@gmail.com",
				phone="0812345678",
				address="Bangkok"
		)
		member = Member(personal_info=personal_info, role="ST", school_id=1, username="earth")
		username, password = generate_username_password(member)
		self.assertEqual(username, "tliangso")
		self.assertEqual(password, "@42Bangkok")

	def test_generate_username_password_2(self):
		personal_info = PersonalInfo(
				first_name="Armel",
				middle_name="Khonvum",
				last_name="Oudin",
				email="earth@gmail.com",
				phone="0812345678",
				address="Bangkok"
		)
		member = Member(personal_info=personal_info, role="ST", school_id=1, username="earth")
		username, password = generate_username_password(member)
		self.assertEqual(username, "aoudin")
		self.assertEqual(password, "@42Bangkok")

	def test_generate_username_password_3(self):
		personal_info = PersonalInfo(
				first_name="Samboon",
				middle_name="Khonvum",
				last_name="Poolprasart",
				email="earth@gmail.com",
				phone="0812345678",
				address="Bangkok"
		)
		member = Member(personal_info=personal_info, role="ST", school_id=1, username="earth")
		username, password = generate_username_password(member)
		self.assertEqual(username, "spoolpra")
		self.assertEqual(password, "@42Bangkok")


class GetSubTypeTest(TestCase):
	def test_get_subtype(self):
		studentType = get_subtype("ST")
		teacherType = get_subtype("TE")
		headmasterType = get_subtype("HM")
		self.assertEqual(studentType, Student)
		self.assertEqual(teacherType, Teacher)
		self.assertEqual(headmasterType, HeadMaster)

class CreateDjangoUserTest(TestCase):
	def test_create_django_user_with_no_username(self):
		personal_info = PersonalInfo(
				first_name="Thanapol",
				middle_name="Khonvum",
				last_name="Liangsoonthornsit",
				email="earth@gmail.com",
				phone="0812345678",
				address="Bangkok"
		)
		member = Member(personal_info=personal_info, role="ST", school_id=1)
		django_user = create_django_user(member, is_staff=False)
		self.assertEqual(type(django_user), User)
		self.assertEqual(django_user.username, "tliangso")

	def test_create_django_user_with_username(self):
		personal_info = PersonalInfo(
				first_name="Thanapol",
				middle_name="Khonvum",
				last_name="Liangsoonthornsit",
				email="earth@gmail.com",
				phone="0812345678",
				address="Bangkok"
		)
		member = Member(personal_info=personal_info, role="ST", school_id=1, username="earth")
		django_user = create_django_user(member, is_staff=False)
		self.assertEqual(type(django_user), User)
		self.assertEqual(django_user.username, "earth")
