from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.catalog_view, name='catalog'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration/', views.registration_view, name='registration'),
    
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    
    # Категории
    path('categories/', views.categories_list, name='categories_list'),
    path('category/<str:category_slug>/', views.category_detail, name='category_detail'),
    
    # Товары
    path('product/<str:product_slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    
    # Заказы и профили
    path('user/<int:user_id>/orders/', views.user_orders, name='user_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('user/<int:user_id>/profile/', views.user_profile, name='user_profile'),
]
