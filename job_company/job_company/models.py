from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change this to avoid conflict
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change this to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser'
    )


class Event(models.Model):
    name = models.CharField(max_length=255)
    guests = models.IntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    city = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='employees')
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name