#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.utils import six

from event_logger.models import EventLog

from .models import Human, Owner, Person, Pet, PizzaOrder


class EventLoggerTests(TestCase):

    def test_readme(self):
        # No EventLog objects yet
        assert EventLog.objects.count() == 0

        # Creating an object will make one
        pizza_order = PizzaOrder.objects.create(status='ORDERED')
        assert EventLog.objects.count() == 1

        # This object has some fields on it
        history = EventLog.objects.get()
        assert history.model_name == 'PizzaOrder'
        assert history.field_name == 'status'
        assert history.before == None
        assert history.after == 'ORDERED'
        assert history.timestamp is not None

        # Updating that particular field creates a new FieldHistory
        pizza_order.status = 'COOKING'
        pizza_order.save()
        assert EventLog.objects.count() == 2

        updated_history = EventLog.objects.last()
        assert updated_history.model_name == 'PizzaOrder'
        assert updated_history.field_name == 'status'
        assert updated_history.before == 'ORDERED'
        assert updated_history.after == 'COOKING'
        assert updated_history.timestamp is not None

    def test_new_object_creates_field_history(self):
        # No FieldHistory objects yet
        self.assertEqual(EventLog.objects.count(), 0)

        Person.objects.create(name='Initial Name')

        # Creating an object will make one
        self.assertEqual(EventLog.objects.count(), 1)

        # This object has some fields on it
        history = EventLog.objects.get()
        self.assertEqual(history.model_name, 'Person')
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.after, 'Initial Name')
        self.assertIsNotNone(history.timestamp)

    # TODO: Re-purpose test case to check for additional fields (HTTP Call)
    # def test_field_history_user_is_from_request_user(self):
    #     user = get_user_model().objects.create(
    #         username='test',
    #         email='test@test.com')
    #     user.set_password('password')
    #     user.save()
    #     self.client.login(username='test', password='password')

    #     response = self.client.get(reverse("index"))

    #     # Make sure the view worked
    #     self.assertEqual(response.status_code, 200)
    #     order = PizzaOrder.objects.get()
    #     history = order.get_status_history().get()
    #     self.assertEqual(history.object, order)
    #     self.assertEqual(history.field_name, 'status')
    #     self.assertEqual(history.field_value, 'ORDERED')
    #     self.assertIsNotNone(history.date_created)
    #     self.assertEqual(history.user, user)

    def test_updated_object_creates_additional_field_history(self):
        person = Person.objects.create(name='Initial Name')

        # Updating that particular field creates a new FieldHistory
        person.name = 'Updated Name'
        person.save()
        self.assertEqual(EventLog.objects.count(), 2)

        histories = EventLog.objects# get_for_model_and_field(person, 'name')

        updated_history = histories.order_by('-timestamp').first()
        self.assertEqual(updated_history.model_name, 'Person')
        self.assertEqual(updated_history.field_name, 'name')
        self.assertEqual(updated_history.after, 'Updated Name')
        self.assertIsNotNone(updated_history.timestamp)

        # One more time for good measure
        person.name = 'Updated Again'
        person.save()
        self.assertEqual(EventLog.objects.count(), 3)

        histories = EventLog.objects.filter(object_id=person.id, field_name='name')

        third_history = histories.order_by('-timestamp').first()
        self.assertEqual(third_history.model_name, 'Person')
        self.assertEqual(third_history.field_name, 'name')
        self.assertEqual(third_history.after, 'Updated Again')
        self.assertIsNotNone(third_history.timestamp)



    def test_field_history_is_not_created_if_field_value_did_not_change(self):
        person = Person.objects.create(name='Initial Name')

        self.assertEqual(EventLog.objects.count(), 1)

        # The value of person did not change, so don't create a new FieldHistory
        person.name = 'Initial Name'
        person.save()

        self.assertEqual(EventLog.objects.count(), 1)

    def test_field_history_works_with_integer_field(self):
        Human.objects.create(age=18)

        self.assertEqual(EventLog.objects.filter(field_name='age').count(), 1)
        history = EventLog.objects.filter(field_name='age').first()

        self.assertEqual(history.model_name, 'Human')
        self.assertEqual(history.field_name, 'age')
        self.assertEqual(history.after, str(18))
        self.assertIsNotNone(history.timestamp)

    def test_field_history_works_with_decimal_field(self):
        Human.objects.create(body_temp=98.6)

        self.assertEqual(EventLog.objects.filter(field_name='body_temp').count(), 1)
        history = EventLog.objects.filter(field_name='body_temp').first()

        self.assertEqual(history.model_name, 'Human')
        self.assertEqual(history.field_name, 'body_temp')
        self.assertEqual(history.after, str(98.6))
        self.assertIsNotNone(history.timestamp)

    def test_field_history_works_with_boolean_field(self):
        Human.objects.create(is_female=True)

        self.assertEqual(EventLog.objects.count(), 1)
        history = EventLog.objects.filter(field_name='is_female').first()

        self.assertEqual(history.model_name, 'Human')
        self.assertEqual(history.field_name, 'is_female')
        self.assertEqual(history.after, 'True')
        self.assertIsNotNone(history.timestamp)

    def test_field_history_works_with_date_field(self):
        birth_date = datetime.date(1991, 11, 6)
        Human.objects.create(birth_date=birth_date)

        self.assertEqual(EventLog.objects.filter(field_name='birth_date').count(), 1)
        history = EventLog.objects.filter(field_name='birth_date').first()

        self.assertEqual(history.model_name, 'Human')
        self.assertEqual(history.field_name, 'birth_date')
        self.assertEqual(history.after, str(birth_date))
        self.assertIsNotNone(history.timestamp)

    def test_field_history_tracks_multiple_fields_changed_at_same_time(self):
        human = Human.objects.create(
            birth_date=datetime.date(1991, 11, 6),
            is_female=True,
            body_temp=98.6,
            age=18,
        )

        self.assertEqual(EventLog.objects.count(), 4)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='birth_date').count(), 1)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='is_female').count(), 1)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='body_temp').count(), 1)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='age').count(), 1)

        human.birth_date = datetime.date(1992, 11, 6)
        human.is_female = False
        human.body_temp = 100.0
        human.age = 21
        human.save()

        self.assertEqual(EventLog.objects.count(), 8)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='birth_date').count(), 2)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='is_female').count(), 2)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='body_temp').count(), 2)
        self.assertEqual(EventLog.objects.filter(object_id=human.id, field_name='age').count(), 2)

    def test_field_history_works_with_foreign_key_field(self):
        pet = Pet.objects.create(name='Garfield')
        Owner.objects.create(name='Jon', pet=pet)

        self.assertEqual(EventLog.objects.filter(field_name='pet_id').count(), 1)
        history = EventLog.objects.filter(field_name='pet_id').first()

        self.assertEqual(history.model_name, 'Owner')
        self.assertEqual(history.field_name, 'pet_id')
        self.assertEqual(history.after, str(pet.id))
        self.assertIsNotNone(history.timestamp)

    def test_field_history_works_with_field_of_parent_model(self):
        Owner.objects.create(name='Jon')

        history = EventLog.objects.first()

        self.assertEqual(history.model_name, 'Owner')
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.after, 'Jon')

    # TODO: Add tests for additional fields, request-updates and multiple-update handling script
