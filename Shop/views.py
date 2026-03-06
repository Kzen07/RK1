
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
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

	in_wishlist = False
	if request.user.is_authenticated:
		wishlist = Wishlist.objects.filter(user=request.user).first()
		if wishlist:
			in_wishlist = wishlist.products.filter(id=product.id).exists()

	context = {
		'product': product,
		'reviews': reviews,
		'average_rating': average_rating,
		'in_wishlist': in_wishlist,
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

	error = None
	if request.method == 'POST':
		if not request.user.is_authenticated:
			return redirect('login')

		if Review.objects.filter(product=product, user=request.user).exists():
			error = 'Вы уже оставляли отзыв на этот товар.'
		else:
			rating = request.POST.get('rating')
			title = request.POST.get('title', '').strip()
			text = request.POST.get('text', '').strip()

			if not rating or not title:
				error = 'Заполните оценку и заголовок.'
			else:
				Review.objects.create(
					product=product,
					user=request.user,
					rating=int(rating),
					title=title,
					text=text,
				)
				return redirect('product_reviews', product_id=product_id)

	context = {
		'product': product,
		'reviews': reviews,
		'error': error,
		'page_title': f'Отзывы на {product.name}'
	}
	return render(request, 'product_reviews.html', context)


def cart_view(request):
	if not request.user.is_authenticated:
		return redirect('login')

	cart, _ = Cart.objects.get_or_create(user=request.user)
	items = cart.items.select_related('product').all()
	total = cart.get_total()

	context = {
		'cart': cart,
		'items': items,
		'total': total,
		'page_title': 'Корзина'
	}
	return render(request, 'cart.html', context)


def add_to_cart(request, product_id):
	if not request.user.is_authenticated:
		return redirect('login')

	product = get_object_or_404(Product, id=product_id)
	cart, _ = Cart.objects.get_or_create(user=request.user)
	item, created = CartItem.objects.get_or_create(cart=cart, product=product)
	if not created:
		item.quantity += 1
		item.save()

	return redirect('cart')


def remove_from_cart(request, item_id):
	if not request.user.is_authenticated:
		return redirect('login')

	item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
	item.delete()
	return redirect('cart')


def update_cart(request, item_id):
	if not request.user.is_authenticated:
		return redirect('login')

	item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
	quantity = int(request.POST.get('quantity', 1))
	if quantity < 1:
		item.delete()
	else:
		item.quantity = quantity
		item.save()
	return redirect('cart')


def add_to_wishlist(request, product_id):
	if not request.user.is_authenticated:
		return redirect('login')

	product = get_object_or_404(Product, id=product_id)
	wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
	wishlist.products.add(product)
	return redirect('product_detail', product_slug=product.slug)


def remove_from_wishlist(request, product_id):
	if not request.user.is_authenticated:
		return redirect('login')

	product = get_object_or_404(Product, id=product_id)
	wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
	wishlist.products.remove(product)
	return redirect('user_profile', user_id=request.user.id)


def checkout_view(request):
	if not request.user.is_authenticated:
		return redirect('login')

	cart = get_object_or_404(Cart, user=request.user)
	items = cart.items.select_related('product').all()

	if not items.exists():
		return redirect('cart')

	total = cart.get_total()
	order = Order.objects.create(user=request.user, total_price=total, status='pending')

	for item in items:
		OrderItem.objects.create(
			order=order,
			product=item.product,
			quantity=item.quantity,
			price=item.product.price,
		)

	cart.items.all().delete()

	return redirect('order_detail', order_id=order.id)


def login_view(request):
	if request.user.is_authenticated:
		return redirect('catalog')

	error = None
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(request.POST.get('next') or 'catalog')
		else:
			error = 'Неверный логин или пароль.'

	return render(request, 'login.html', {'error': error, 'next': request.GET.get('next', '')})


def logout_view(request):
	logout(request)
	return redirect('catalog')


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
