from django.test import TestCase
from .models import ProbateContract, Profile
from .tasks import check_dead_wallets
from mywish2.settings import config

from unittest import skip


@skip('Probate contracts did not deploy')
class ProbateStatusTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_profile = Profile.objects.create(owner_address='0x00a0a0aaa0a0a0aaaa0a')
        cls.user_profile2 = Profile.objects.create(owner_address='0x00a0a0aaa00a00aaaa0a')
        ProbateContract.objects.create(address='0x0a0aaa0aa0a0a0a0aaaa0',
                                       mails_array=['test@gmail.com', 'tt@mail.ru'],
                                       dead=False, identifier='165753223',
                                       owner=cls.user_profile, owner_mail='owner@gmail.com',
                                       test_noda=True)

        ProbateContract.objects.create(address='0x0a0aaa0aa0a0a0a00aa0',
                                       mails_array=['tt@mail.ru'],
                                       dead=False, identifier='165123223',
                                       owner=cls.user_profile2, owner_mail='owner@gmail.com',
                                       test_noda=True)

    def test_check_dead_wallets(self):
        check_dead_wallets(config.TEST_ENDPOINT, True)
        first_probate = ProbateContract.objects.first()
        second_probate = ProbateContract.objects.last()
        self.assertEqual(first_probate.dead, True)
        self.assertEqual(second_probate.dead, True)
