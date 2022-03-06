from django.test import TestCase
from django.test import Client
from web3 import Web3
from django.urls import reverse

from cblock.contracts.models import ProbateContract, Profile
from cblock.contracts.utils import send_heirs_mail

import json


class ProbateStatusTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user_profile = Profile.objects.create(owner_address='0x00a0a0aaa0a0a0aaaa0a')
        cls.user_profile2 = Profile.objects.create(owner_address='0x00a0a0aaa00a00aaaa0a')
        ProbateContract.objects.create(address=Web3.toChecksumAddress('0x0a970179dd1aAa0eEaC71787C4Bdf5a362F0877d'),
                                       mails=['test@gmail.com', 'tt@mail.ru'],
                                       dead=False, owner=cls.user_profile,
                                       owner_mail='owner@gmail.com', test_node=True)

        ProbateContract.objects.create(address=Web3.toChecksumAddress('0x0a980169dd1aAa0eEaC71787C4Bdf5a362F0877d'),
                                       mails=['tt@mail.ru'],
                                       dead=False, owner=cls.user_profile2,
                                       owner_mail='owner@gmail.com', test_node=True)

    def test_check_dead_wallets(self):
        first_probate = ProbateContract.objects.first()
        first_probate.change_dead_status()
        second_probate = ProbateContract.objects.last()
        self.assertEqual(first_probate.dead, True)
        self.assertEqual(second_probate.dead, False)

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
            'mails': [
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
            'mails': [
                'test@mail.ru',
                'another@gmail.com'
            ],
            'owner_mail': 'ownertest@mail.ru'
        }
        response = self.client.post(path=reverse('new_probate'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_new_token(self):
        data = {
            'owner_address': '0xt0e0s0t0a0d0d0r0e0s0s0',
            'contract_name': 'test name',
            'addresses': [
                '0xtestcontractaddress',
                '0xtestcontractaddress2'
            ],
            'contract_address': '0xtestcontractaddress'
        }
        response = self.client.post(path=reverse('new_token'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
