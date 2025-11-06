from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Items, Category, Tag, Cart, CartItem, HomeHero
from .forms import SignupForm, CheckoutForm


class ModelsTestCase(TestCase):
    """Test cases for models"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name="Furniture")
        self.tag = Tag.objects.create(caption="Featured")
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a simple image file for testing
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/jpeg'
        )
        
        self.item = Items.objects.create(
            Category=self.category,
            name="Test Item",
            description="Test Description",
            price=99.99,
            image1=image,
            available=True,
            slug="test-item"
        )
        self.item.Tag.add(self.tag)
    
    def test_category_str(self):
        """Test Category string representation"""
        self.assertEqual(str(self.category), "Furniture")
    
    def test_tag_str(self):
        """Test Tag string representation"""
        self.assertEqual(str(self.tag), "Featured")
    
    def test_items_str(self):
        """Test Items string representation"""
        self.assertEqual(str(self.item), "Test Item")
    
    def test_items_has_tag(self):
        """Test Items has tag relationship"""
        self.assertIn(self.tag, self.item.Tag.all())
    
    def test_cart_creation(self):
        """Test Cart creation for user"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(str(cart), f"Cart({self.user.username})")
        self.assertIsNotNone(cart.created_at)
    
    def test_cartitem_creation(self):
        """Test CartItem creation"""
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, item=self.item, quantity=2)
        self.assertEqual(str(cart_item), f"{self.item.name} x 2")
        self.assertEqual(cart_item.quantity, 2)
    
    def test_homehero_str(self):
        """Test HomeHero string representation"""
        image = SimpleUploadedFile(
            name='hero.jpg',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/jpeg'
        )
        hero = HomeHero.objects.create(
            title="Test Hero",
            subtitle="Test Subtitle",
            image=image,
            is_active=True
        )
        self.assertEqual(str(hero), "Test Hero")


class ViewsTestCase(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name="Furniture")
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/jpeg'
        )
        
        self.item = Items.objects.create(
            Category=self.category,
            name="Test Item",
            description="Test Description",
            price=99.99,
            image1=image,
            available=True,
            slug="test-item"
        )
    
    def test_startingpage_view(self):
        """Test homepage view"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_item_details_view(self):
        """Test item details view"""
        response = self.client.get(reverse('item-details', kwargs={'slug': 'test-item'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_item_details_404(self):
        """Test item details view with invalid slug"""
        response = self.client.get(reverse('item-details', kwargs={'slug': 'non-existent'}))
        self.assertEqual(response.status_code, 404)
    
    def test_add_to_cart_authenticated(self):
        """Test adding item to cart for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add-to-cart'), {'post_id': self.item.id})
        self.assertEqual(response.status_code, 200)
        
        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, item=self.item)
        self.assertEqual(cart_item.quantity, 1)
    
    def test_add_to_cart_anonymous(self):
        """Test adding item to cart for anonymous user"""
        response = self.client.post(reverse('add-to-cart'), {'post_id': self.item.id})
        self.assertEqual(response.status_code, 200)
        
        # Check session cart
        session = self.client.session
        self.assertIn(self.item.id, session.get('cart_list', []))
    
    def test_cart_list_authenticated(self):
        """Test cart list view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, item=self.item, quantity=2)
        
        response = self.client.get(reverse('cart-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_cart_list_anonymous(self):
        """Test cart list view for anonymous user"""
        session = self.client.session
        session['cart_list'] = [self.item.id]
        session.save()
        
        response = self.client.get(reverse('cart-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_checkout_requires_login(self):
        """Test checkout view requires authentication"""
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
    
    def test_checkout_authenticated(self):
        """Test checkout view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, item=self.item, quantity=1)
        
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Item')
    
    def test_wishlist_requires_login(self):
        """Test wishlist view requires authentication"""
        response = self.client.get(reverse('wish-list'))
        self.assertEqual(response.status_code, 302)  # Redirects to login


class FormsTestCase(TestCase):
    """Test cases for forms"""
    
    def test_signup_form_valid(self):
        """Test valid signup form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_signup_form_password_mismatch(self):
        """Test signup form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_signup_form_duplicate_email(self):
        """Test signup form with duplicate email"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_signup_form_invalid_email(self):
        """Test signup form with invalid email"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_checkout_form_valid(self):
        """Test valid checkout form"""
        form_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'address_line1': '123 Main St',
            'address_line2': 'Apt 4B',
            'city': 'New York',
            'state': 'NY',
            'postal_code': '10001'
        }
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_checkout_form_missing_required_fields(self):
        """Test checkout form with missing required fields"""
        form_data = {
            'full_name': 'John Doe',
            # Missing email, address_line1, city, postal_code
        }
        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_checkout_form_invalid_email(self):
        """Test checkout form with invalid email"""
        form_data = {
            'full_name': 'John Doe',
            'email': 'invalid-email',
            'address_line1': '123 Main St',
            'city': 'New York',
            'postal_code': '10001'
        }
        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())


class ContextProcessorTestCase(TestCase):
    """Test cases for context processors"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name="Furniture")
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
            content_type='image/jpeg'
        )
        
        self.item = Items.objects.create(
            Category=self.category,
            name="Test Item",
            description="Test Description",
            price=99.99,
            image1=image,
            available=True,
            slug="test-item"
        )
    
    def test_cart_context_authenticated(self):
        """Test cart context processor for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, item=self.item, quantity=3)
        
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['cart_count'], 3)
    
    def test_cart_context_anonymous(self):
        """Test cart context processor for anonymous user"""
        session = self.client.session
        session['cart_list'] = [self.item.id, 999]  # One valid, one invalid
        session.save()
        
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['cart_count'], 1)
    
    def test_cart_context_empty(self):
        """Test cart context processor with empty cart"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['cart_count'], 0)
