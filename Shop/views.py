
from django.shortcuts import render, redirect
from .models import Product

def registration_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		phone = request.POST.get('phone')
		address = request.POST.get('address')
		from django.contrib.auth.models import User
		from .models import UserProfile
		if username and password:
			user = User.objects.create_user(username=username, password=password)
			UserProfile.objects.create(user=user, phone=phone, address=address)
			return redirect('catalog')
	return render(request, 'registration.html')

def catalog_view(request):
	products = Product.objects.all()
	return render(request, 'catalog.html', {'products': products})

