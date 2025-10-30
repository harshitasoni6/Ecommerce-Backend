from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from applications.products.models import Category, Product
from applications.orders.models import Order, OrderItem
from applications.cart.models import Cart, CartItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create users
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('admin123')
        admin.save()
        
        seller1, _ = User.objects.get_or_create(
            username='seller1',
            defaults={
                'email': 'seller1@example.com',
                'role': 'seller',
                'first_name': 'John',
                'last_name': 'Seller'
            }
        )
        seller1.set_password('seller123')
        seller1.save()
        
        seller2, _ = User.objects.get_or_create(
            username='seller2',
            defaults={
                'email': 'seller2@example.com',
                'role': 'seller',
                'first_name': 'Jane',
                'last_name': 'Vendor'
            }
        )
        seller2.set_password('seller123')
        seller2.save()
        
        customer1, _ = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer1@example.com',
                'role': 'customer',
                'first_name': 'Alice',
                'last_name': 'Customer'
            }
        )
        customer1.set_password('customer123')
        customer1.save()
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Books and magazines'},
            {'name': 'Home & Garden', 'description': 'Home improvement and gardening'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(cat)
        
        # Create products
        products_data = [
            # Seller 1 products
            {'name': 'Laptop Pro 15', 'seller': seller1, 'category': categories[0], 'price': 1299.99, 'stock': 15, 'description': 'High-performance laptop with 16GB RAM and 512GB SSD'},
            {'name': 'Wireless Mouse', 'seller': seller1, 'category': categories[0], 'price': 29.99, 'stock': 50, 'description': 'Ergonomic wireless mouse with long battery life'},
            {'name': 'USB-C Hub', 'seller': seller1, 'category': categories[0], 'price': 49.99, 'stock': 30, 'description': '7-in-1 USB-C hub with multiple ports'},
            {'name': 'Mechanical Keyboard', 'seller': seller1, 'category': categories[0], 'price': 89.99, 'stock': 20, 'description': 'RGB mechanical keyboard with blue switches'},
            
            # Seller 2 products
            {'name': 'Cotton T-Shirt', 'seller': seller2, 'category': categories[1], 'price': 19.99, 'stock': 100, 'description': '100% cotton comfortable t-shirt'},
            {'name': 'Denim Jeans', 'seller': seller2, 'category': categories[1], 'price': 59.99, 'stock': 40, 'description': 'Classic fit denim jeans'},
            {'name': 'Running Shoes', 'seller': seller2, 'category': categories[4], 'price': 79.99, 'stock': 25, 'description': 'Lightweight running shoes with cushioned sole'},
            {'name': 'Winter Jacket', 'seller': seller2, 'category': categories[1], 'price': 129.99, 'stock': 15, 'description': 'Warm winter jacket with hood'},
            {'name': 'Python Programming Book', 'seller': seller2, 'category': categories[2], 'price': 39.99, 'stock': 30, 'description': 'Comprehensive guide to Python programming'},
            {'name': 'Garden Tools Set', 'seller': seller2, 'category': categories[3], 'price': 45.99, 'stock': 20, 'description': 'Complete set of essential garden tools'},
        ]
        
        for prod_data in products_data:
            Product.objects.get_or_create(
                name=prod_data['name'],
                seller=prod_data['seller'],
                defaults={
                    'category': prod_data['category'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'description': prod_data['description'],
                    'is_active': True
                }
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('Users created:'))
        self.stdout.write('  - admin / admin123 (Admin)')
        self.stdout.write('  - seller1 / seller123 (Seller)')
        self.stdout.write('  - seller2 / seller123 (Seller)')
        self.stdout.write('  - customer1 / customer123 (Customer)')

# ======================
# Run with: python manage.py create_sample_data
# ======================

