from django.test import TestCase
from django.test import Client
from unittest import skip
from django.urls import reverse

from .models import ProbateContract, Profile
from .tasks import check_dead_wallets
from .utils import send_heirs_mail
from mywish2.settings import config

import json


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

    @skip('Probate contracts did not deploy')
    def test_check_dead_wallets(self):
        check_dead_wallets(config.TEST_ENDPOINT, True)
        first_probate = ProbateContract.objects.first()
        second_probate = ProbateContract.objects.last()
        self.assertEqual(first_probate.dead, True)
        self.assertEqual(second_probate.dead, True)

    def test_send_mails(self):
        done = send_heirs_mail(owner_mail='my@mail.ru', heirs_mail_list=['some@gmail.com', 'another@mail.ru'])
        self.assertEqual(done, None)

class CreationContractTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Profile.objects.create(owner_address='0xt0e0s0t0a0d0d0r0e0s0s0')
        cls.client = Client()

    def test_new_crowdsale(self):
        data = {
            'owner_address': '0xt0e0s0t0a0d0d0r0e0s0s0',
            'contract_name': 'test name',
            'contract_address': '0xtestcontractaddress'
        }
        response = self.client.post(path=reverse('new_crowdsale'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_new_wedding(self):
        data = {
            'owner_address': '0xt0e0s0t0a0d0d0r0e0s0s0',
            'contract_address': '0xtestcontractaddress',
            'contract_name': 'test name',
            'mail_list': [
                'test@mail.ru',
                'another@gmail.com'
            ]
        }
        response = self.client.post(path=reverse('new_wedding'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_new_probate(self):
        data = {
            'owner_address': '0xt0e0s0t0a0d0d0r0e0s0s0',
            'contract_address': '0xtestcontractaddress',
            'contract_name': 'test name',
            'mail_list': [
                'test@mail.ru',
                'another@gmail.com'
            ],
            'identifier': 1234567890,
            'owner_mail': 'ownertest@mail.ru'
        }
        response = self.client.post(path=reverse('new_probate'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_new_token(self):
        data = {
            'owner_address': '0xt0e0s0t0a0d0d0r0e0s0s0',
            'contract_name': 'test name',
            'address_list': [
                '0xtestcontractaddress',
                '0xtestcontractaddress2'
            ],
            'contract_address': '0xtestcontractaddress'
        }
        response = self.client.post(path=reverse('new_token'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
