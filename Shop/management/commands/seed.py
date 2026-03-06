from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, Cart, Wishlist, UserProfile, Order, OrderItem, Review


CATEGORIES = [
    {"name": "Электроника", "slug": "electronics", "description": "Телефоны, ноутбуки, гаджеты"},
    {"name": "Одежда", "slug": "clothing", "description": "Мужская и женская одежда"},
    {"name": "Книги", "slug": "books", "description": "Художественная и учебная литература"},
    {"name": "Спорт", "slug": "sport", "description": "Товары для спорта и фитнеса"},
]

PRODUCTS = [
    {"name": "iPhone 15", "slug": "iphone-15", "price": "899.99", "stock": 10, "category": "electronics", "description": "Смартфон Apple iPhone 15 128GB"},
    {"name": "MacBook Air M2", "slug": "macbook-air-m2", "price": "1199.99", "stock": 5, "category": "electronics", "description": "Ноутбук Apple MacBook Air с чипом M2"},
    {"name": "AirPods Pro", "slug": "airpods-pro", "price": "249.99", "stock": 20, "category": "electronics", "description": "Беспроводные наушники Apple AirPods Pro"},
    {"name": "Samsung Galaxy S24", "slug": "samsung-galaxy-s24", "price": "799.99", "stock": 15, "category": "electronics", "description": "Флагманский смартфон Samsung"},
    {"name": "Футболка базовая", "slug": "basic-tshirt", "price": "19.99", "stock": 100, "category": "clothing", "description": "Хлопковая базовая футболка"},
    {"name": "Джинсы slim fit", "slug": "slim-jeans", "price": "49.99", "stock": 50, "category": "clothing", "description": "Классические джинсы slim fit"},
    {"name": "Кроссовки Nike Air", "slug": "nike-air", "price": "89.99", "stock": 30, "category": "clothing", "description": "Удобные кроссовки Nike Air Max"},
    {"name": "Мастер и Маргарита", "slug": "master-margarita", "price": "9.99", "stock": 40, "category": "books", "description": "М.А. Булгаков — классика русской литературы"},
    {"name": "Чистый код", "slug": "clean-code", "price": "29.99", "stock": 25, "category": "books", "description": "Роберт Мартин — руководство по написанию качественного кода"},
    {"name": "Гантели 10кг", "slug": "dumbbells-10kg", "price": "34.99", "stock": 20, "category": "sport", "description": "Разборные гантели 10 кг"},
    {"name": "Коврик для йоги", "slug": "yoga-mat", "price": "24.99", "stock": 35, "category": "sport", "description": "Нескользящий коврик для йоги и фитнеса"},
]

USERS = [
    {"username": "alice", "password": "pass1234", "email": "alice@example.com", "phone": "+7 701 111 2233", "address": "Алматы, ул. Абая 10"},
    {"username": "bob", "password": "pass1234", "email": "bob@example.com", "phone": "+7 702 333 4455", "address": "Астана, пр. Республики 5"},
]


class Command(BaseCommand):
    help = "Заполнить базу данных тестовыми данными"

    def handle(self, *args, **kwargs):
        self.stdout.write("Создаём категории...")
        categories = {}
        for data in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=data["slug"], defaults=data)
            categories[data["slug"]] = cat

        self.stdout.write("Создаём товары...")
        products = {}
        for data in PRODUCTS:
            cat = categories[data.pop("category")]
            product, _ = Product.objects.get_or_create(
                slug=data["slug"],
                defaults={**data, "category": cat}
            )
            products[product.slug] = product

        self.stdout.write("Создаём пользователей...")
        users = []
        for data in USERS:
            if User.objects.filter(username=data["username"]).exists():
                user = User.objects.get(username=data["username"])
            else:
                user = User.objects.create_user(
                    username=data["username"],
                    password=data["password"],
                    email=data["email"],
                )
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={"phone": data["phone"], "address": data["address"]}
                )
                Cart.objects.get_or_create(user=user)
                Wishlist.objects.get_or_create(user=user)
            users.append(user)

        self.stdout.write("Создаём заказы...")
        product_list = list(products.values())

        order1 = Order.objects.create(user=users[0], total_price="1149.98", status="delivered", is_paid=True)
        OrderItem.objects.get_or_create(order=order1, product=product_list[0], defaults={"quantity": 1, "price": product_list[0].price})
        OrderItem.objects.get_or_create(order=order1, product=product_list[2], defaults={"quantity": 1, "price": product_list[2].price})

        order2 = Order.objects.create(user=users[1], total_price="49.99", status="processing", is_paid=False)
        OrderItem.objects.get_or_create(order=order2, product=product_list[5], defaults={"quantity": 1, "price": product_list[5].price})

        self.stdout.write("Создаём отзывы...")
        Review.objects.get_or_create(
            product=product_list[0], user=users[0],
            defaults={"rating": 5, "title": "Отличный телефон!", "text": "Очень доволен покупкой, рекомендую.", "is_verified_purchase": True}
        )
        Review.objects.get_or_create(
            product=product_list[1], user=users[1],
            defaults={"rating": 4, "title": "Хороший ноутбук", "text": "Быстрый, лёгкий, но дорогой.", "is_verified_purchase": False}
        )
        Review.objects.get_or_create(
            product=product_list[7], user=users[0],
            defaults={"rating": 5, "title": "Шедевр", "text": "Читал три раза — каждый раз открываю что-то новое.", "is_verified_purchase": True}
        )

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! Создано:\n"
            f"  {len(CATEGORIES)} категории\n"
            f"  {len(PRODUCTS)} товаров\n"
            f"  {len(USERS)} пользователей (пароль: pass1234)\n"
            f"  2 заказа\n"
            f"  3 отзыва"
        ))
