
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phone = models.CharField(max_length=20, blank=True)
	address = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return self.user.username

class Product(models.Model):
	CATEGORY_CHOICES = [
		('computer', 'Компьютер'),
		('notebook', 'Ноутбук'),
		('phone', 'Телефон'),
	]
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

	def __str__(self):
		return self.name
