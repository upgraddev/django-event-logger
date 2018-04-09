from django.conf import settings
from django.db import models


class Pet(models.Model):
    app_label = 'Random'
    name = models.CharField(max_length=255)


class Person(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    @property
    def _field_history_user(self):
        return self.created_by


class Owner(Person):
    pet = models.ForeignKey(Pet, blank=True, null=True)


class Human(models.Model):
    age = models.IntegerField(blank=True, null=True)
    is_female = models.BooleanField(default=True)
    body_temp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)


class PizzaOrder(models.Model):
    STATUS_ORDERED = 'ORDERED'
    STATUS_COOKING = 'COOKING'
    STATUS_COMPLETE = 'COMPLETE'

    STATUS_CHOICES = (
        (STATUS_ORDERED, 'Ordered'),
        (STATUS_COOKING, 'Cooking'),
        (STATUS_COMPLETE, 'Complete'),
    )
    status = models.CharField(max_length=64, choices=STATUS_CHOICES)
