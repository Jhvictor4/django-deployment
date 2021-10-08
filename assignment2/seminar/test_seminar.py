from django.test import Client, TestCase
from django.utils import timezone
from rest_framework import status
import json
import datetime

from user.models import User
from seminar.models import Seminar, UserSeminar, InstructorProfile, ParticipantProfile
from user.serializers import jwt_token_of

class PostSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_token = 'JWT ' + jwt_token_of(part)
        ParticipantProfile.objects.create(user=part)

        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'JWT ' + jwt_token_of(partinst)
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'JWT ' + jwt_token_of(inst)
        InstructorProfile.objects.create(user=inst)

        inst2 = User.objects.create_user(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_token = 'JWT ' + jwt_token_of(inst2)
        self.inst2_id = inst2.id
        InstructorProfile.objects.create(user=inst2)

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            is_instructor=False
        )
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            is_instructor=True
        )

    def test_post_seminar_unauthorized(self):
        response = self.client.post(         # Unauthorized
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_noninstructor(self):
        response = self.client.post(         # Not instructor
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.part_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_already_instructor(self):
        response = self.client.post(         # Already instructing another seminar
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_incomplete_request(self):
        response = self.client.post(         # Name blank
            '/api/v1/seminar/',
            json.dumps({
                "name": "",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No capacity
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No count
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No time
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_wrong_request(self):
        response = self.client.post(         # capacity not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": "a",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # capacity < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": -1,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": "a",
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": -1,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # time format wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # online wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
                "online": "dd"
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar(self):
        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertTrue(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.partinst_id)
        self.assertEqual(instructor["username"], "partinst")
        self.assertEqual(instructor["email"], "partinst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)

        seminar = Seminar.objects.get(id=data["id"])
        self.assertEqual(seminar.name, "seminar2")
        self.assertEqual(seminar.capacity, 9)
        self.assertEqual(seminar.count, 4)
        self.assertTrue(hasattr(seminar, "time"))
        self.assertTrue(seminar.online)
        userseminar = seminar.user_seminars.get()
        self.assertEqual(userseminar.user.username, "partinst")
        self.assertEqual(userseminar.role, "instructor")
        self.assertIsNone(userseminar.dropped_at)

        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
                "online": "F",
            }),
            HTTP_AUTHORIZATION=self.inst2_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertFalse(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst2_id)
        self.assertEqual(instructor["username"], "inst2")
        self.assertEqual(instructor["email"], "inst2@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)

        seminar = Seminar.objects.get(id=data["id"])
        self.assertEqual(seminar.name, "seminar2")
        self.assertEqual(seminar.capacity, 9)
        self.assertEqual(seminar.count, 4)
        self.assertTrue(hasattr(seminar, "time"))
        self.assertFalse(seminar.online)
        userseminar = seminar.user_seminars.get()
        self.assertEqual(userseminar.user.username, "inst2")
        self.assertEqual(userseminar.role, "instructor")
        self.assertIsNone(userseminar.dropped_at)

        self.assertEqual(Seminar.objects.count(), 3)
        self.assertEqual(UserSeminar.objects.count(), 4)


class PutSeminarSeminaridTestCase(TestCase):
    client = Client()

    def setUp(self):
        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'JWT ' + jwt_token_of(partinst)
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'JWT ' + jwt_token_of(inst)
        self.inst_id = inst.id
        InstructorProfile.objects.create(user=inst)

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
            online=False,
        )
        self.seminar_id = seminar.id
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            is_instructor=False,
            dropped_at=timezone.localtime(),
        )
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            is_instructor=True
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=11,
            count=6,
            time=datetime.time(hour=15, minute=40),
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar2,
            is_instructor=True
        )

    def test_put_seminar_seminarid_unauthorized(self):
        response = self.client.put(         # Unauthorized
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_not_instructor(self):
        response = self.client.put(         # Not instructor of the seminar
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_wrong_id(self):
        response = self.client.put(         # wrong id
            '/api/v1/seminar/3/',
            json.dumps({
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "seminar1")

    def test_put_seminar_seminarid_wrong_request(self):
        response = self.client.put(         # Capacity smaller than number of participants
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "capacity": 0,
                "name": "Seminar1",
                "online": "T",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.capacity, 10)
        self.assertEqual(seminar.name, "seminar1")
        self.assertFalse(seminar.online)

        response = self.client.put(         # Capacity not number
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "capacity": "a",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.capacity, 10)

        response = self.client.put(         # count < 0
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "count": -1,
                "name": "Seminar1",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)
        self.assertEqual(seminar.name, "seminar1")

        response = self.client.put(         # count not number
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "count": "z",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)

        response = self.client.put(         # time wrong format
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "time": "12",
                "count": 7,
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.count, 5)

        response = self.client.put(         # wrong online
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "online": "d"
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertFalse(seminar.online)

    def test_put_seminar_seminarid(self):
        response = self.client.put(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            json.dumps({
                "name": "Seminar1",
                "capacity": 1,
                "count": 20,
                "time": "10:10",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar_id)
        self.assertEqual(data["name"], "Seminar1")
        self.assertEqual(data["capacity"], 1)
        self.assertEqual(data["count"], 20)
        self.assertEqual(data["time"], "10:10")
        self.assertFalse(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst_id)
        self.assertEqual(instructor["username"], "inst")
        self.assertEqual(instructor["email"], "inst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertIn("participants", data)
        self.assertEqual(len(data["participants"]), 1)
        participant = data["participants"][0]
        self.assertEqual(participant["id"], self.partinst_id)
        self.assertEqual(participant["username"], "partinst")
        self.assertEqual(participant["email"], "partinst@mail.com")
        self.assertEqual(participant["first_name"], "")
        self.assertEqual(participant["last_name"], "")
        self.assertIn("joined_at", participant)
        self.assertFalse(participant["is_active"])
        self.assertIsNotNone(participant["dropped_at"])

        seminar = Seminar.objects.get(id=self.seminar_id)
        self.assertEqual(seminar.name, "Seminar1")
        self.assertEqual(seminar.capacity, 1)
        self.assertEqual(seminar.count, 20)
        self.assertFalse(seminar.online)


class GetSeminarSeminaridTestCase(TestCase):
    client = Client()

    def setUp(self):
        inst = User.objects.create(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_id = inst.id
        InstructorProfile.objects.create(user=inst)
        self.inst_token = 'JWT ' + jwt_token_of(isnt)

        inst2 = User.objects.create(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_id = inst2.id
        InstructorProfile.objects.create(user=inst2)

        part = User.objects.create(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_id = part.id
        ParticipantProfile.objects.create(user=part)

        partinst = User.objects.create(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_id = partinst.id
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        seminar = Seminar.objects.create(
            name="seminar",
            capacity=10,
            count=5,
            time=timezone.localtime(),
        )
        self.seminar_id = seminar.id
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=inst2,
            seminar=seminar,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=part,
            seminar=seminar,
            is_instructor=False,
            dropped_at=timezone.localtime(),
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            is_instructor=False
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=11,
            count=6,
            time=timezone.localtime(),
            online=False,
        )
        self.seminar2_id = seminar2.id
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar2,
            is_instructor=True
        )

    def test_get_seminar_seminarid_wrong_id(self):
        response = self.client.get(         # wrong id
            '/api/v1/seminar/10/',
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_seminar(self):
        response = self.client.get(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar_id),
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar_id)
        self.assertEqual(data["name"], "seminar")
        self.assertEqual(data["capacity"], 10)
        self.assertEqual(data["count"], 5)
        self.assertIn("time", data)
        self.assertTrue(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 2)

        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst_id)
        self.assertEqual(instructor["username"], "inst")
        self.assertEqual(instructor["email"], "inst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)

        instructor2 = data["instructors"][1]
        self.assertEqual(instructor2["id"], self.inst2_id)
        self.assertEqual(instructor2["username"], "inst2")
        self.assertEqual(instructor2["email"], "inst2@mail.com")
        self.assertEqual(instructor2["first_name"], "")
        self.assertEqual(instructor2["last_name"], "")
        self.assertIn("joined_at", instructor2)
        self.assertIn("participants", data)
        self.assertEqual(len(data["participants"]), 2)

        participant = data["participants"][0]
        self.assertEqual(participant["id"], self.part_id)
        self.assertEqual(participant["username"], "part")
        self.assertEqual(participant["email"], "part@mail.com")
        self.assertEqual(participant["first_name"], "")
        self.assertEqual(participant["last_name"], "")
        self.assertIn("joined_at", participant)
        self.assertFalse(participant["is_active"])
        self.assertIsNotNone(participant["dropped_at"])

        participant2 = data["participants"][1]
        self.assertEqual(participant2["id"], self.partinst_id)
        self.assertEqual(participant2["username"], "partinst")
        self.assertEqual(participant2["email"], "partinst@mail.com")
        self.assertEqual(participant2["first_name"], "")
        self.assertEqual(participant2["last_name"], "")
        self.assertIn("joined_at", participant2)
        self.assertTrue(participant2["is_active"])
        self.assertIsNone(participant2["dropped_at"])

        response = self.client.get(         # Correct
            '/api/v1/seminar/{}/'.format(self.seminar2_id),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 11)
        self.assertEqual(data["count"], 6)
        self.assertIn("time", data)
        self.assertFalse(data["online"])
        self.assertIn("instructors", data)
        self.assertEqual(len(data["instructors"]), 1)

        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.partinst_id)
        self.assertEqual(instructor["username"], "partinst")
        self.assertEqual(instructor["email"], "partinst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)

        self.assertEqual(len(data["participants"]), 0)


class GetSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        part1 = User.objects.create_user(
            username="part1",
            password="password",
            email="part1@mail.com",
        )
        self.part1_id = part1.id
        ParticipantProfile.objects.create(user=part1)
        self.part1_token = 'JWT ' + jwt_token_of(part1)

        part2 = User.objects.create_user(
            username="part2",
            password="password",
            email="part2@mail.com",
        )
        self.part2_id = part2.id
        ParticipantProfile.objects.create(user=part2)

        inst1 = User.objects.create_user(
            username="inst1",
            password="password",
            email="inst1@mail.com",
        )
        self.inst1_id = inst1.id
        InstructorProfile.objects.create(user=inst1)

        inst2 = User.objects.create_user(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_id = inst2.id
        InstructorProfile.objects.create(user=inst2)

        inst3 = User.objects.create_user(
            username="inst3",
            password="password",
            email="inst3@mail.com",
        )
        self.inst3_id = inst3.id
        InstructorProfile.objects.create(user=inst3)

        seminar1 = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=timezone.localtime()
        )
        self.seminar1_id = seminar1.id
        UserSeminar.objects.create(
            user=part1,
            seminar=seminar1,
            is_instructor=False
        )
        UserSeminar.objects.create(
            user=part2,
            seminar=seminar1,
            is_instructor=False,
            dropped_at=timezone.localtime(),
        )
        UserSeminar.objects.create(
            user=inst1,
            seminar=seminar1,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=inst2,
            seminar=seminar1,
            is_instructor=True
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=10,
            count=5,
            time=timezone.localtime()
        )
        self.seminar2_id = seminar2.id
        UserSeminar.objects.create(
            user=inst3,
            seminar=seminar2,
            is_instructor=True
        )

    def test_get_seminar(self):
        response = self.client.get(         # Correct
            '/api/v1/seminar/',
            HTTP_AUTHORIZATION=self.part1_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 2)

        seminar = data[0]
        self.assertEqual(seminar["name"], "seminar2")
        self.assertEqual(seminar["participant_count"], 0)
        instructors = seminar["instructors"]
        self.assertEqual(len(instructors), 1)

        inst3 = instructors[0]
        self.assertEqual(inst3["id"], self.inst3_id)
        self.assertEqual(inst3["username"], "inst3")
        self.assertEqual(inst3["email"], "inst3@mail.com")
        self.assertEqual(inst3["first_name"], "")
        self.assertEqual(inst3["last_name"], "")
        self.assertIn("joined_at", inst3)

        seminar = data[1]
        self.assertEqual(seminar["name"], "seminar1")
        self.assertEqual(seminar["participant_count"], 1)
        instructors = seminar["instructors"]
        self.assertEqual(len(instructors), 2)

        inst1 = instructors[0]
        self.assertEqual(inst1["id"], self.inst1_id)
        self.assertEqual(inst1["username"], "inst1")
        self.assertEqual(inst1["email"], "inst1@mail.com")
        self.assertEqual(inst1["first_name"], "")
        self.assertEqual(inst1["last_name"], "")
        self.assertIn("joined_at", inst1)

        inst2 = instructors[1]
        self.assertEqual(inst2["id"], self.inst2_id)
        self.assertEqual(inst2["username"], "inst2")
        self.assertEqual(inst2["email"], "inst2@mail.com")
        self.assertEqual(inst2["first_name"], "")
        self.assertEqual(inst2["last_name"], "")
        self.assertIn("joined_at", inst2)

    def test_get_seminar_name(self):
        response = self.client.get(         # Correct
            '/api/v1/seminar/?name=2',
            HTTP_AUTHORIZATION=self.part1_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 1)

        seminar = data[0]
        self.assertEqual(seminar["name"], "seminar2")

    def test_get_seminar_earliest(self):
        response = self.client.get(         # Correct
            '/api/v1/seminar/?order=earliest&sth=dd',
            HTTP_AUTHORIZATION=self.part1_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]["name"], "seminar1")
        self.assertEqual(data[1]["name"], "seminar2")


class PostSeminarSeminaridUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        partinst1 = User.objects.create_user(
            username="partinst1",
            password="password",
            email="partinst1@mail.com",
        )
        self.partinst1_token = 'JWT ' + jwt_token_of(partinst1)
        ParticipantProfile.objects.create(user=partinst1)
        InstructorProfile.objects.create(user=partinst1)

        part1 = User.objects.create_user(
            username="part1",
            password="password",
            email="part1@mail.com",
        )
        self.part1_token = 'JWT ' + jwt_token_of(part1)
        ParticipantProfile.objects.create(user=part1)

        partinst2 = User.objects.create_user(
            username="partinst2",
            password="password",
            email="partinst2@mail.com",
        )
        self.partinst2_token = 'JWT ' + jwt_token_of(partinst2)
        ParticipantProfile.objects.create(user=partinst2)
        InstructorProfile.objects.create(user=partinst2)

        partinst3 = User.objects.create_user(
            username="partinst3",
            password="password",
            email="partinst3@mail.com",
        )
        self.partinst3_token = 'JWT ' + jwt_token_of(partinst3)
        ParticipantProfile.objects.create(user=partinst3)
        InstructorProfile.objects.create(user=partinst3)

        partinst4 = User.objects.create_user(
            username="partinst4",
            password="password",
            email="partinst4@mail.com",
        )
        self.partinst4_token = 'JWT ' + jwt_token_of(partinst4)
        ParticipantProfile.objects.create(user=partinst4, accepted=False)
        InstructorProfile.objects.create(user=partinst4)

        part3 = User.objects.create_user(
            username="part3",
            password="password",
            email="part3@mail.com",
        )
        self.part3_token = 'JWT ' + jwt_token_of(part3)
        ParticipantProfile.objects.create(user=part3)

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'JWT ' + jwt_token_of(inst)
        InstructorProfile.objects.create(user=inst)

        part2 = User.objects.create_user(
            username="part2",
            password="password",
            email="part2@mail.com",
        )
        self.part2_token = 'JWT ' + jwt_token_of(part2)
        ParticipantProfile.objects.create(user=part2)

        seminar1 = Seminar.objects.create(
            name="semianr1",
            capacity=1,
            count=5,
            time=timezone.localtime(),
        )
        self.seminar1_id = seminar1.id
        UserSeminar.objects.create(
            user=partinst1,
            seminar=seminar1,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=part1,
            seminar=seminar1,
            is_instructor=False
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=2,
            count=5,
            time=timezone.localtime(),
        )
        self.seminar2_id = seminar2.id
        UserSeminar.objects.create(
            user=partinst2,
            seminar=seminar2,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=partinst3,
            seminar=seminar2,
            is_instructor=False,
            dropped_at=timezone.localtime(),
        )

    def test_post_seminar_seminarid_unauthorized(self):
        response = self.client.post(         # unauthorized
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(UserSeminar.objects.filter(seminar__name="seminar2").count(), 2)

    def test_post_seminar_seminarid_wrong_seminarid(self):
        response = self.client.post(         # wrong seminarid
            '/api/v1/seminar/99/user/',
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_wrong_role(self):
        response = self.client.post(         # Wrong role
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "p",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # role blank
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No role
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No instructor profile
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(         # No participant profile
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_not_accepted(self):
        response = self.client.post(         # Not accepted
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst4_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_user_capacity_full(self):
        response = self.client.post(         # Seminar capacity full
            '/api/v1/seminar/{}/user/'.format(self.seminar1_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part2_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_user_instructing_another_seminar(self):
        response = self.client.post(         # Instructing another seminar
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst1_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_user_already_member_of_seminar(self):
        response = self.client.post(         # Already a member of the seminar
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst2_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # Already a member of the seminar
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst2_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # Already a member of the seminar
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(UserSeminar.objects.count(), 4)

    def test_post_seminar_seminarid_user(self):
        response = self.client.post(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst1_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 1)
        participants = data["participants"]
        self.assertEqual(len(participants), 2)
        participant1 = participants[0]
        self.assertEqual(participant1["username"], "partinst3")
        self.assertFalse(participant1["is_active"])
        participant2 = participants[1]
        self.assertEqual(participant2["username"], "partinst1")
        self.assertTrue(participant2["is_active"])

        self.assertEqual(UserSeminar.objects.count(), 5)
        self.assertTrue(UserSeminar.objects.filter(
            user__username="partinst1",
            seminar__name="seminar2",
            role="participant"
        ).exists())

        response = self.client.post(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.partinst4_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 2)
        instructor1 = instructors[0]
        self.assertEqual(instructor1["username"], "partinst2")
        instructor2 = instructors[1]
        self.assertEqual(instructor2["username"], "partinst4")
        participants = data["participants"]
        self.assertEqual(len(participants), 2)

        self.assertEqual(UserSeminar.objects.count(), 6)
        self.assertTrue(UserSeminar.objects.filter(
            user__username="partinst4",
            seminar__name="seminar2",
            role="instructor"
        ).exists())

        response = self.client.post(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "participant",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part3_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 2)
        participants = data["participants"]
        self.assertEqual(len(participants), 3)
        participant1 = participants[0]
        self.assertEqual(participant1["username"], "partinst3")
        self.assertFalse(participant1["is_active"])
        participant2 = participants[1]
        self.assertEqual(participant2["username"], "partinst1")
        self.assertTrue(participant2["is_active"])
        participant3 = participants[2]
        self.assertEqual(participant3["username"], "part3")
        self.assertTrue(participant2["is_active"])

        self.assertEqual(UserSeminar.objects.count(), 7)
        self.assertTrue(UserSeminar.objects.filter(
            user__username="part3",
            seminar__name="seminar2",
            role="participant"
        ).exists())

        response = self.client.post(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            json.dumps({"role": "instructor",}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 3)
        instructor1 = instructors[0]
        self.assertEqual(instructor1["username"], "partinst2")
        instructor2 = instructors[1]
        self.assertEqual(instructor2["username"], "partinst4")
        instructor3 = instructors[2]
        self.assertEqual(instructor3["username"], "inst")
        participants = data["participants"]
        self.assertEqual(len(participants), 3)

        self.assertEqual(UserSeminar.objects.count(), 8)
        self.assertTrue(UserSeminar.objects.filter(
            user__username="inst",
            seminar__name="seminar2",
            role="instructor"
        ).exists())


class DeleteSeminarSeminaridUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        part1 = User.objects.create_user(
            username="part1",
            email="part1@mail.com",
            password="password"
        )
        self.part1_id = part1.id
        self.part1_token = 'JWT ' + jwt_token_of(part1)
        ParticipantProfile.objects.create(user=part1)

        part2 = User.objects.create_user(
            username="part2",
            email="part2@mail.com",
            password="password"
        )
        self.part2_id = part2.id
        self.part2_token = 'JWT ' + jwt_token_of(part2)
        ParticipantProfile.objects.create(user=part2)

        partinst = User.objects.create_user(
            username="partinst",
            email="partinst@mail.com",
            password="password"
        )
        self.partinst_id = partinst.id
        self.partinst_token = 'JWT ' + jwt_token_of(partinst)
        ParticipantProfile.objects.create(user=partinst)
        InstructorProfile.objects.create(user=partinst)

        inst = User.objects.create_user(
            username="inst",
            email="inst@mail.com",
            password="password"
        )
        self.inst_id = inst.id
        self.inst_token = 'JWT ' + jwt_token_of(inst)
        InstructorProfile.objects.create(user=inst)

        seminar1 = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=timezone.localtime()
        )
        self.seminar1_id = seminar1.id
        UserSeminar.objects.create(
            user=part1,
            seminar=seminar1,
            is_instructor=False,
            dropped_at=timezone.localtime()
        )
        UserSeminar.objects.create(
            user=part2,
            seminar=seminar1,
            is_instructor=False
        )
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar1,
            is_instructor=True
        )

        seminar2 = Seminar.objects.create(
            name="seminar2",
            capacity=10,
            count=5,
            time=timezone.localtime()
        )
        self.seminar2_id = seminar2.id
        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar2,
            is_instructor=False
        )
        UserSeminar.objects.create(
            user=inst,
            seminar=seminar2,
            is_instructor=True
        )
        UserSeminar.objects.create(
            user=part2,
            seminar=seminar2,
            is_instructor=False
        )

    def test_delete_seminar_seminarid_user_unauthorized(self):
        response = self.client.delete(         # unauthorized
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_seminar_seminarid_user_wrong_seminarid(self):
        response = self.client.delete(         # Wrong seminarid
            '/api/v1/seminar/99/user/',
            HTTP_AUTHORIZATION=self.partinst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_seminar_seminarid_user_instructor(self):
        response = self.client.delete(         # Instructor
            '/api/v1/seminar/{}/user/'.format(self.seminar1_id),
            HTTP_AUTHORIZATION=self.partinst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(         # Instructor
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(UserSeminar.objects.filter(role="instructor", dropped_at=None).count(), 2)
        self.assertEqual(UserSeminar.objects.count(), 6)

    def test_delete_seminar_seminarid_user_not_attending(self):
        response = self.client.delete(         # Already dropped
            '/api/v1/seminar/{}/user/'.format(self.seminar1_id),
            HTTP_AUTHORIZATION=self.part1_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(         # Not attending
            '/api/v1/seminar/{}/user/'.format(self.seminar1_id),
            HTTP_AUTHORIZATION=self.inst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIsNone(
            UserSeminar.objects.get(user__username="inst", seminar__name="seminar2").dropped_at
        )
        self.assertEqual(UserSeminar.objects.count(), 6)

    def test_delete_seminar_seminarid_user(self):
        response = self.client.delete(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar2_id),
            HTTP_AUTHORIZATION=self.partinst_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar2_id)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 10)
        self.assertEqual(data["count"], 5)
        self.assertIn("time", data)
        self.assertTrue(data["online"])
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 1)
        instructor = instructors[0]
        self.assertEqual(instructor["id"], self.inst_id)
        self.assertEqual(instructor["username"], "inst")
        self.assertEqual(instructor["email"], "inst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        participants = data["participants"]
        self.assertEqual(len(participants), 2)
        participant1 = participants[0]
        self.assertEqual(participant1["id"], self.partinst_id)
        self.assertEqual(participant1["username"], "partinst")
        self.assertEqual(participant1["email"], "partinst@mail.com")
        self.assertEqual(participant1["first_name"], "")
        self.assertEqual(participant1["last_name"], "")
        self.assertIn("joined_at", participant1)
        self.assertFalse(participant1["is_active"])
        self.assertIsNotNone(participant1["dropped_at"])
        participant2 = participants[1]
        self.assertEqual(participant2["id"], self.part2_id)
        self.assertEqual(participant2["username"], "part2")
        self.assertEqual(participant2["email"], "part2@mail.com")
        self.assertEqual(participant2["first_name"], "")
        self.assertEqual(participant2["last_name"], "")
        self.assertIn("joined_at", participant2)
        self.assertTrue(participant2["is_active"])
        self.assertIsNone(participant2["dropped_at"])

        response = self.client.delete(         # Correct
            '/api/v1/seminar/{}/user/'.format(self.seminar1_id),
            HTTP_AUTHORIZATION=self.part2_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.seminar1_id)
        instructors = data["instructors"]
        self.assertEqual(len(instructors), 1)
        instructor = instructors[0]
        self.assertEqual(instructor["id"], self.partinst_id)
        participants = data["participants"]
        self.assertEqual(len(participants), 2)
        participant1 = participants[0]
        self.assertEqual(participant1["id"], self.part1_id)
        self.assertFalse(participant1["is_active"])
        self.assertIsNotNone(participant1["dropped_at"])
        participant2 = participants[1]
        self.assertEqual(participant2["id"], self.part2_id)
        self.assertFalse(participant2["is_active"])
        self.assertIsNotNone(participant2["dropped_at"])

        self.assertIsNotNone(
            UserSeminar.objects.get(user__username="part2", seminar__name="seminar1").dropped_at
        )
        self.assertIsNotNone(
            UserSeminar.objects.get(user__username="partinst", seminar__name="seminar2").dropped_at
        )
        self.assertIsNone(
            UserSeminar.objects.get(user__username="part2", seminar__name="seminar2").dropped_at
        )
        self.assertEqual(UserSeminar.objects.count(), 6)
        self.assertEqual(UserSeminar.objects.filter(dropped_at=None).count(), 3)