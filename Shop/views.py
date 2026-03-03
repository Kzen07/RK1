
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import (
	UserProfile, Product, Category, Order, OrderItem, 
	Review, Cart, CartItem, Wishlist
)


def categories_list(request):
	categories = Category.objects.all()
	context = {
		'categories': categories,
		'page_title': 'Категории товаров'
	}
	return render(request, 'categories_list.html', context)


def category_detail(request, category_slug):
	category = get_object_or_404(Category, slug=category_slug)
	products = category.products.filter(is_active=True)
	context = {
		'category': category,
		'products': products,
		'page_title': f'Категория: {category.name}'
	}
	return render(request, 'category_detail.html', context)


def product_detail(request, product_slug):
	product = get_object_or_404(Product, slug=product_slug)
	reviews = product.reviews.all()
	average_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
	context = {
		'product': product,
		'reviews': reviews,
		'average_rating': average_rating,
		'page_title': product.name
	}
	return render(request, 'product_detail.html', context)


def user_orders(request, user_id):
	user = get_object_or_404(User, id=user_id)
	orders = user.orders.all()
	context = {
		'user': user,
		'orders': orders,
		'page_title': f'Заказы пользователя {user.username}'
	}
	return render(request, 'user_orders.html', context)


def order_detail(request, order_id):
	order = get_object_or_404(Order, id=order_id)
	items = order.items.all()
	context = {
		'order': order,
		'items': items,
		'page_title': f'Заказ #{order.id}'
	}
	return render(request, 'order_detail.html', context)


def catalog_view(request):
	products = Product.objects.filter(is_active=True)
	context = {
		'products': products,
		'page_title': 'Каталог товаров'
	}
	return render(request, 'catalog.html', context)


def product_reviews(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	reviews = product.reviews.all()
	context = {
		'product': product,
		'reviews': reviews,
		'page_title': f'Отзывы на {product.name}'
	}
	return render(request, 'product_reviews.html', context)


def cart_view(request):
	if not request.user.is_authenticated:
		return redirect('login')
	
	cart, created = Cart.objects.get_or_create(user=request.user)
	items = cart.items.all()
	total = cart.get_total()
	
	context = {
		'cart': cart,
		'items': items,
		'total': total,
		'page_title': 'Корзина'
	}
	return render(request, 'cart.html', context)


def registration_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		phone = request.POST.get('phone')
		address = request.POST.get('address')
		
		if username and password:
			try:
				user = User.objects.create_user(username=username, password=password)
				UserProfile.objects.create(user=user, phone=phone, address=address)
				Cart.objects.create(user=user)
				Wishlist.objects.create(user=user)
				login(request, user)
				return redirect('catalog')
			except:
				context = {'error': 'Пользователь уже существует'}
				return render(request, 'registration.html', context)
	
	return render(request, 'registration.html')


def user_profile(request, user_id):
	user = get_object_or_404(User, id=user_id)
	profile = get_object_or_404(UserProfile, user=user)
	orders = user.orders.all()
	wishlist = get_object_or_404(Wishlist, user=user)
	total_spent = sum(order.total_price for order in orders)
	
	context = {
		'user': user,
		'profile': profile,
		'orders': orders,
		'wishlist': wishlist,
		'total_spent': total_spent,
		'page_title': f'Профиль {user.username}'
	}
	return render(request, 'user_profile.html', context)
