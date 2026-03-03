from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	phone = models.CharField(max_length=20, blank=True, null=True)
	address = models.CharField(max_length=255, blank=True, null=True)
	is_premium = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Профиль {self.user.username}"


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name_plural = "Категории"

	def __str__(self):
		return self.name


class Product(models.Model):
	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True, null=True)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	stock = models.IntegerField(default=0)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.name


class Cart(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
	products = models.ManyToManyField(Product, through='CartItem', related_name='carts')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Корзина {self.user.username}"

	def get_total(self):
		return sum(item.get_subtotal() for item in self.items.all())


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def get_subtotal(self):
		return self.product.price * self.quantity

	def __str__(self):
		return f"{self.product.name} в корзине {self.cart.user.username}"


class Order(models.Model):
	STATUS_CHOICES = [
		('pending', 'В ожидании'),
		('processing', 'Обработка'),
		('shipped', 'Отправлено'),
		('delivered', 'Доставлено'),
		('cancelled', 'Отменено'),
	]
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	is_paid = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Заказ #{self.id} - {self.user.username}"


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	price = models.DecimalField(max_digits=10, decimal_places=2)

	def get_subtotal(self):
		return self.price * self.quantity

	def __str__(self):
		return f"{self.product.name} в заказе #{self.order.id}"


class Review(models.Model):
	RATING_CHOICES = [
		(1, '⭐'),
		(2, '⭐⭐'),
		(3, '⭐⭐⭐'),
		(4, '⭐⭐⭐⭐'),
		(5, '⭐⭐⭐⭐⭐'),
	]
	
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
	rating = models.IntegerField(choices=RATING_CHOICES)
	title = models.CharField(max_length=200)
	text = models.TextField(blank=True, null=True)
	is_verified_purchase = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ['product', 'user']
		ordering = ['-created_at']

	def __str__(self):
		return f"Отзыв {self.user.username} на {self.product.name}"


class Wishlist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
	products = models.ManyToManyField(Product, related_name='wishlists')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Список желаний {self.user.username}"
