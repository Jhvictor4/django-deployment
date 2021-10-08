import heapq
from bisect import bisect_left
from functools import reduce

from django.db.models import F
from django.test import TestCase


# Create your tests here.
from rest_framework import status

from seminar.models import User
from survey.models import OperatingSystem, SurveyResult


class TestExample(TestCase):

    def add(self, a, b):
        return a + b

    def setUp(self):
        OperatingSystem.objects.create(
            name='os'
        )
        self.user = User.objects.create_user(
            email='user@user.com',
            password='password'
        )

    def test_check(self):

        cnt = OperatingSystem.objects.filter(name='os').count()
        self.assertEqual(cnt, 1)

        survey = SurveyResult.objects.filter(
            rdb__gt=F('python')
        )
        self.assertNumQueries(2)
        
        client = self.client
        
        client.force_login(self.user)
        response = client.get('/api/v1/user/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_test(self):

        def fun(x, y):
            print(x, y)
            if y != 0:
                return y * x
            else:
                return x

        ls = [-1, 1, 0, -3, 3]
        print(reduce(fun, ls))
        from collections import deque
        bisect_left
        heapq
        from itertools import