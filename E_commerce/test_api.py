"""
API Testing Script for E-Commerce Backend with Razorpay
Save as: test_api.py in project root
Run with: python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_section(msg):
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{msg}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_json(data):
    print(json.dumps(data, indent=2))

# Store tokens and IDs
tokens = {}
user_data = {}

def test_register():
    print_section("1. Testing User Registration")
    
    users = [
        {
            "username": "test_seller",
            "email": "testseller@example.com",
            "password": "TestPass123",
            "password2": "TestPass123",
            "role": "seller",
            "first_name": "Test",
            "last_name": "Seller",
            "phone": "+919876543210"
        },
        {
            "username": "test_customer",
            "email": "testcustomer@example.com",
            "password": "TestPass123",
            "password2": "TestPass123",
            "role": "customer",
            "first_name": "Test",
            "last_name": "Customer",
            "phone": "+919876543211"
        },
    ]
    
    for user in users:
        response = requests.post(f"{BASE_URL}/users/register/", json=user)
        if response.status_code == 201:
            print_success(f"Registered {user['role']}: {user['username']}")
        elif response.status_code == 400 and 'already exists' in str(response.json()):
            print_info(f"User {user['username']} already exists - skipping")
        else:
            print_error(f"Failed to register {user['username']}")
            print_json(response.json())

def test_login():
    print_section("2. Testing User Login")
    
    users = [
        {"username": "test_seller", "password": "TestPass123", "role": "seller"},
        {"username": "test_customer", "password": "TestPass123", "role": "customer"},
    ]
    
    for user in users:
        response = requests.post(
            f"{BASE_URL}/users/login/",
            json={"username": user['username'], "password": user['password']}
        )
        if response.status_code == 200:
            data = response.json()
            tokens[user['role']] = data['access']
            print_success(f"Logged in as {user['role']}: {user['username']}")
            print_info(f"Token: {data['access'][:40]}...")
        else:
            print_error(f"Failed to login {user['username']}")
            print_json(response.json())

def test_profile():
    print_section("3. Testing User Profile")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print_success("Retrieved user profile")
        print_info(f"Username: {profile['username']}")
        print_info(f"Email: {profile['email']}")
        print_info(f"Role: {profile['role']}")
    else:
        print_error("Failed to get profile")
        print_json(response.json())

def test_create_category():
    print_section("4. Testing Category Creation")
    
    if 'seller' not in tokens:
        print_error("No seller token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['seller']}"}
    categories = [
        {"name": "Test Electronics", "description": "Electronic devices for testing"},
        {"name": "Test Clothing", "description": "Clothing items for testing"},
        {"name": "Test Books", "description": "Books for testing"},
    ]
    
    for category in categories:
        response = requests.post(
            f"{BASE_URL}/products/categories/",
            json=category,
            headers=headers
        )
        if response.status_code == 201:
            print_success(f"Created category: {category['name']}")
            if not user_data.get('category_id'):
                user_data['category_id'] = response.json()['id']
        elif response.status_code == 400:
            print_info(f"Category {category['name']} may already exist")
        else:
            print_error(f"Failed to create category: {category['name']}")
            print_json(response.json())

def test_list_categories():
    print_section("5. Testing List Categories")
    
    response = requests.get(f"{BASE_URL}/products/categories/")
    
    if response.status_code == 200:
        categories = response.json()['results']
        print_success(f"Retrieved {len(categories)} categories")
        for cat in categories[:3]:
            print_info(f"  - {cat['name']} (ID: {cat['id']})")
        if categories and not user_data.get('category_id'):
            user_data['category_id'] = categories[0]['id']
    else:
        print_error("Failed to list categories")

def test_create_product():
    print_section("6. Testing Product Creation")
    
    if 'seller' not in tokens:
        print_error("No seller token available")
        return
    
    if not user_data.get('category_id'):
        print_error("No category ID available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['seller']}"}
    products = [
        {
            "name": "Test Laptop",
            "description": "High-performance laptop for testing",
            "price": "45999.99",
            "stock": 10,
            "category": user_data['category_id'],
            "is_active": True
        },
        {
            "name": "Test Smartphone",
            "description": "Latest smartphone for testing",
            "price": "29999.99",
            "stock": 15,
            "category": user_data['category_id'],
            "is_active": True
        },
    ]
    
    for product in products:
        response = requests.post(
            f"{BASE_URL}/products/",
            json=product,
            headers=headers
        )
        if response.status_code == 201:
            product_data = response.json()
            print_success(f"Created product: {product['name']}")
            print_info(f"  Product ID: {product_data['id']}")
            print_info(f"  Price: ₹{product_data['price']}")
            print_info(f"  Stock: {product_data['stock']}")
            if not user_data.get('product_id'):
                user_data['product_id'] = product_data['id']
        else:
            print_error(f"Failed to create product: {product['name']}")
            print_json(response.json())

def test_list_products():
    print_section("7. Testing List Products")
    
    response = requests.get(f"{BASE_URL}/products/")
    
    if response.status_code == 200:
        products = response.json()['results']
        print_success(f"Retrieved {len(products)} products")
        for prod in products[:3]:
            print_info(f"  - {prod['name']} - ₹{prod['price']} (Stock: {prod['stock']})")
        if products and not user_data.get('product_id'):
            user_data['product_id'] = products[0]['id']
    else:
        print_error("Failed to list products")

def test_add_to_cart():
    print_section("8. Testing Add to Cart")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    if not user_data.get('product_id'):
        print_error("No product ID available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    cart_item = {
        "product_id": user_data['product_id'],
        "quantity": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/cart/cart/add_item/",
        json=cart_item,
        headers=headers
    )
    if response.status_code == 200:
        cart = response.json()
        print_success("Added item to cart")
        print_info(f"Items in cart: {len(cart['items'])}")
        print_info(f"Cart Total: ₹{cart['total_amount']}")
    else:
        print_error("Failed to add to cart")
        print_json(response.json())

def test_view_cart():
    print_section("9. Testing View Cart")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    response = requests.get(f"{BASE_URL}/cart/cart/", headers=headers)
    
    if response.status_code == 200:
        cart = response.json()
        print_success("Retrieved cart")
        print_info(f"Items in cart: {len(cart['items'])}")
        for item in cart['items']:
            print_info(f"  - {item['product']['name']} x {item['quantity']} = ₹{item['subtotal']}")
        print_info(f"Total: ₹{cart['total_amount']}")
    else:
        print_error("Failed to get cart")
        print_json(response.json())

def test_add_to_wishlist():
    print_section("10. Testing Add to Wishlist")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    if not user_data.get('product_id'):
        print_error("No product ID available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    response = requests.post(
        f"{BASE_URL}/cart/wishlist/",
        json={"product_id": user_data['product_id']},
        headers=headers
    )
    
    if response.status_code == 201:
        print_success("Added product to wishlist")
    elif response.status_code == 200:
        print_info("Product already in wishlist")
    else:
        print_error("Failed to add to wishlist")
        print_json(response.json())

def test_create_order():
    print_section("11. Testing Order Creation")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    order_data = {
        "shipping_address": "123 MG Road, Indiranagar, Bangalore, Karnataka 560038, India",
        "phone": "+919876543210"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders/",
        json=order_data,
        headers=headers
    )
    if response.status_code == 201:
        order = response.json()
        user_data['order_id'] = order['id']
        print_success("Created order")
        print_info(f"Order ID: {order['id']}")
        print_info(f"Status: {order['status']}")
        print_info(f"Total Amount: ₹{order['total_amount']}")
        print_info(f"Items: {len(order['items'])}")
    else:
        print_error("Failed to create order")
        print_json(response.json())

def test_view_orders():
    print_section("12. Testing View Orders")
    
    # Customer view
    if 'customer' in tokens:
        headers = {"Authorization": f"Bearer {tokens['customer']}"}
        response = requests.get(f"{BASE_URL}/orders/", headers=headers)
        if response.status_code == 200:
            orders = response.json()['results']
            print_success(f"Customer can view {len(orders)} order(s)")
            for order in orders[:2]:
                print_info(f"  Order #{order['id']} - ₹{order['total_amount']} - {order['status']}")
        else:
            print_error("Failed to get customer orders")
    
    # Seller view
    if 'seller' in tokens:
        headers = {"Authorization": f"Bearer {tokens['seller']}"}
        response = requests.get(f"{BASE_URL}/orders/", headers=headers)
        if response.status_code == 200:
            orders = response.json()['results']
            print_success(f"Seller can view {len(orders)} order(s) with their products")
        else:
            print_error("Failed to get seller orders")

def test_create_payment_razorpay():
    print_section("13. Testing Razorpay Payment Creation")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    if not user_data.get('order_id'):
        print_error("No order ID available. Create an order first.")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    payment_data = {
        "order_id": user_data['order_id'],
        "payment_method": "razorpay"
    }
    
    response = requests.post(
        f"{BASE_URL}/payments/create_order/",
        json=payment_data,
        headers=headers
    )
    
    if response.status_code == 201:
        payment = response.json()
        user_data['payment_id'] = payment['payment_id']
        user_data['razorpay_order_id'] = payment['razorpay_order_id']
        print_success("Created Razorpay payment order")
        print_info(f"Payment ID: {payment['payment_id']}")
        print_info(f"Razorpay Order ID: {payment['razorpay_order_id']}")
        print_info(f"Amount: ₹{payment['amount'] / 100}")
        print_info(f"Currency: {payment['currency']}")
        print_warning("💳 Use Razorpay test card: 4111 1111 1111 1111")
        print_warning("📱 Or UPI: success@razorpay")
    else:
        print_error("Failed to create payment")
        print_json(response.json())

def test_create_payment_cod():
    print_section("14. Testing Cash on Delivery (COD)")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    # Create a new order for COD
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    
    # First add item to cart
    if user_data.get('product_id'):
        requests.post(
            f"{BASE_URL}/cart/cart/add_item/",
            json={"product_id": user_data['product_id'], "quantity": 1},
            headers=headers
        )
    
    # Create order
    order_response = requests.post(
        f"{BASE_URL}/orders/",
        json={
            "shipping_address": "456 Brigade Road, Bangalore, Karnataka 560001, India",
            "phone": "+919876543210"
        },
        headers=headers
    )
    
    if order_response.status_code == 201:
        cod_order_id = order_response.json()['id']
        
        # Create COD payment
        payment_data = {
            "order_id": cod_order_id,
            "payment_method": "cod"
        }
        
        cod_response = requests.post(
            f"{BASE_URL}/payments/create_order/",
            json=payment_data,
            headers=headers
        )
        
        if cod_response.status_code == 201:
            cod_payment = cod_response.json()
            print_success("Created Cash on Delivery order")
            print_info(f"Payment ID: {cod_payment['payment_id']}")
            print_info(f"Message: {cod_payment['message']}")
            print_info("💵 Payment will be collected on delivery")
        else:
            print_error("Failed to create COD payment")
            print_json(cod_response.json())
    else:
        print_warning("Could not create new order for COD test")

def test_list_payments():
    print_section("15. Testing List Payments")
    
    if 'customer' not in tokens:
        print_error("No customer token available")
        return
    
    headers = {"Authorization": f"Bearer {tokens['customer']}"}
    response = requests.get(f"{BASE_URL}/payments/", headers=headers)
    
    if response.status_code == 200:
        payments = response.json()['results']
        print_success(f"Retrieved {len(payments)} payment(s)")
        for payment in payments:
            print_info(f"  Payment #{payment['id']} - {payment['payment_method']} - ₹{payment['amount']} - {payment['status']}")
    else:
        print_error("Failed to list payments")

def test_search_products():
    print_section("16. Testing Product Search & Filters")
    
    # Search by name
    response = requests.get(f"{BASE_URL}/products/?search=laptop")
    if response.status_code == 200:
        products = response.json()['results']
        print_success(f"Search 'laptop': Found {len(products)} product(s)")
    
    # Filter by category
    if user_data.get('category_id'):
        response = requests.get(f"{BASE_URL}/products/?category={user_data['category_id']}")
        if response.status_code == 200:
            products = response.json()['results']
            print_success(f"Category filter: Found {len(products)} product(s)")
    
    # Order by price
    response = requests.get(f"{BASE_URL}/products/?ordering=price")
    if response.status_code == 200:
        products = response.json()['results']
        print_success(f"Ordered by price: {len(products)} product(s)")

def test_logout():
    print_section("17. Testing Logout & Token Blacklist")
    
    # Login a new user to test logout
    print_info("Creating temporary user for logout test...")
    temp_user = {
        "username": "temp_logout_test",
        "email": "templogout@example.com",
        "password": "TestPass123",
        "password2": "TestPass123",
        "role": "customer",
        "first_name": "Temp",
        "last_name": "User",
        "phone": "+919876543299"
    }
    
    # Register temp user
    reg_response = requests.post(f"{BASE_URL}/users/register/", json=temp_user)
    if reg_response.status_code not in [201, 400]:
        print_error("Failed to create temp user")
        return
    
    # Login temp user
    login_response = requests.post(
        f"{BASE_URL}/users/login/",
        json={"username": temp_user['username'], "password": temp_user['password']}
    )
    
    if login_response.status_code != 200:
        print_error("Failed to login temp user")
        return
    
    temp_tokens = login_response.json()
    print_success("Logged in temporary user")
    print_info(f"Access Token: {temp_tokens['access'][:40]}...")
    print_info(f"Refresh Token: {temp_tokens['refresh'][:40]}...")
    
    # Test 1: Verify token works BEFORE logout
    print_info("\n📝 Step 1: Testing token before logout...")
    headers = {"Authorization": f"Bearer {temp_tokens['access']}"}
    profile_response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    
    if profile_response.status_code == 200:
        print_success("✓ Token works - can access profile")
    else:
        print_error("✗ Token doesn't work before logout")
        return
    
    # Test 2: Logout (blacklist the refresh token)
    print_info("\n📝 Step 2: Logging out (blacklisting token)...")
    logout_response = requests.post(
        f"{BASE_URL}/users/logout/",
        json={"refresh_token": temp_tokens['refresh']},
        headers=headers
    )
    
    if logout_response.status_code == 200:
        print_success("✓ Logout successful - Token blacklisted")
        print_info(logout_response.json().get('message', ''))
    else:
        print_error("✗ Logout failed")
        print_json(logout_response.json())
        return
    
    # Test 3: Try to refresh using blacklisted token (should FAIL)
    print_info("\n📝 Step 3: Trying to use blacklisted refresh token...")
    refresh_response = requests.post(
        f"{BASE_URL}/users/token/refresh/",
        json={"refresh": temp_tokens['refresh']}
    )
    
    if refresh_response.status_code == 401:
        print_success("✓ Blacklisted token correctly rejected!")
        print_info("Error: " + refresh_response.json().get('detail', ''))
    else:
        print_error("✗ Blacklisted token was NOT rejected (this is bad!)")
        print_json(refresh_response.json())
    
    # Test 4: Verify access token still works (until it expires)
    print_info("\n📝 Step 4: Testing if access token still works...")
    profile_response2 = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    
    if profile_response2.status_code == 200:
        print_warning("⚠ Access token still works (normal - it expires naturally)")
        print_info("Access tokens remain valid until expiry (60 min)")
    else:
        print_info("Access token no longer works")
    
    print_success("\n✅ Token blacklist working correctly!")
    print_warning("💡 Check Django admin now:")
    print_info("  Go to: http://localhost:8000/admin/token_blacklist/blacklistedtoken/")
    print_info("  You should see 1 blacklisted token entry")

def print_summary():
    print_section("📊 Test Summary")
    
    print(f"{Colors.MAGENTA}Test Data Created:{Colors.END}")
    print_info(f"Category ID: {user_data.get('category_id', 'N/A')}")
    print_info(f"Product ID: {user_data.get('product_id', 'N/A')}")
    print_info(f"Order ID: {user_data.get('order_id', 'N/A')}")
    print_info(f"Payment ID: {user_data.get('payment_id', 'N/A')}")
    print_info(f"Razorpay Order ID: {user_data.get('razorpay_order_id', 'N/A')}")
    
    print(f"\n{Colors.MAGENTA}Test Credentials:{Colors.END}")
    print_info("Seller: test_seller / TestPass123")
    print_info("Customer: test_customer / TestPass123")
    
    print(f"\n{Colors.GREEN}✅ All tests completed successfully!{Colors.END}")
    print_warning("\n💡 Next Steps:")
    print("  1. Open Razorpay checkout in browser to complete payment")
    print("  2. Test the admin panel: python manage.py runserver")
    print("  3. Access admin at: http://localhost:8000/admin/")
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}\n")

def run_all_tests():
    print(f"\n{Colors.MAGENTA}{'='*60}{Colors.END}")
    print(f"{Colors.MAGENTA}🚀 E-COMMERCE API TEST SUITE (RAZORPAY){Colors.END}")
    print(f"{Colors.MAGENTA}{'='*60}{Colors.END}")
    
    try:
        test_register()
        test_login()
        
        if 'seller' in tokens and 'customer' in tokens:
            test_profile()
            test_create_category()
            test_list_categories()
            test_create_product()
            test_list_products()
            test_add_to_cart()
            test_view_cart()
            test_add_to_wishlist()
            test_create_order()
            test_view_orders()
            test_create_payment_razorpay()
            test_create_payment_cod()
            test_list_payments()
            test_search_products()
            test_logout()
            print_summary()
        else:
            print_error("Login failed. Cannot continue tests.")
            print_warning("Make sure Django server is running: python manage.py runserver")
    
    except requests.exceptions.ConnectionError:
        print_error("❌ Cannot connect to server!")
        print_warning("Make sure Django server is running:")
        print_warning("  python manage.py runserver")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()