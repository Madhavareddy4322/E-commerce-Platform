from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from decimal import Decimal

from .models import Category, Product, Order, OrderItem, Wishlist, Review, Coupon
from .forms import CheckoutForm, ProductSearchForm, ReviewForm
from .cart import Cart


def home(request):
    categories = Category.objects.all()
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    search_form = ProductSearchForm(request.GET or None)
    query = Product.objects.filter(is_active=True)

    if search_form.is_valid():
        q = search_form.cleaned_data.get('q')
        if q:
            query = query.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )

    # Only show search results if query exists
    search_results = query[:8] if request.GET.get('q') else None

    context = {
        'categories': categories,
        'latest_products': latest_products,
        'search_form': search_form,
        'search_results': search_results,
    }
    return render(request, 'shop/home.html', context)


def product_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products_qs = category.products.filter(is_active=True)

    search_form = ProductSearchForm(request.GET or None)
    if search_form.is_valid():
        q = search_form.cleaned_data.get('q')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')

        if q:
            products_qs = products_qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q)
            )
        if min_price is not None:
            products_qs = products_qs.filter(price__gte=min_price)
        if max_price is not None:
            products_qs = products_qs.filter(price__lte=max_price)

    paginator = Paginator(products_qs, 6)  # 6 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get wishlist ids for current user (for heart icon)
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = list(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'category': category,
        'page_obj': page_obj,
        'search_form': search_form,
        'wishlist_product_ids': wishlist_product_ids,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    reviews = product.reviews.select_related('user')
    avg_rating = product.average_rating()
    review_count = product.review_count()

    can_review = False
    user_review = None
    review_form = None

    if request.user.is_authenticated:
        has_bought = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status__in=['PAID', 'SHIPPED', 'DELIVERED']
        ).exists()
        can_review = has_bought

        if has_bought:
            user_review = Review.objects.filter(user=request.user, product=product).first()
            if user_review:
                review_form = ReviewForm(instance=user_review)
            else:
                review_form = ReviewForm()

    context = {
        'product': product,
        'in_wishlist': in_wishlist,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'can_review': can_review,
        'user_review': user_review,
        'review_form': review_form,
    }
    return render(request, 'shop/product_detail.html', context)

# CART VIEWS

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


# CHECKOUT + ORDERS

@login_required
@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart_detail')

    applied_coupon = None
    discount_amount = Decimal('0.00')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data['address']
            coupon_code = form.cleaned_data['coupon_code'].strip()
            total = cart.get_total_price()

            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code)
                    if coupon.is_valid():
                        applied_coupon = coupon
                        discount_amount = (Decimal(coupon.discount_pct) / Decimal('100')) * total
                    else:
                        applied_coupon = None
                except Coupon.DoesNotExist:
                    applied_coupon = None

            order = Order.objects.create(
                user=request.user,
                address=address,
                total_amount=total,
                status='PAID',  # mock payment success
                coupon=applied_coupon,
                discount_amount=discount_amount
            )

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price'],
                )
                item['product'].stock -= item['quantity']
                item['product'].save()

            cart.clear()
            return render(request, 'shop/order_success.html', {'order': order})
    else:
        form = CheckoutForm()

    return render(request, 'shop/checkout.html', {
        'cart': cart,
        'form': form,
    })

@login_required
def my_orders(request):
    orders = request.user.orders.order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})


# WISHLIST

@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'shop/wishlist_list.html', {
        'wishlist_items': wishlist_items,
    })


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', slug=product.slug)


@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('wishlist_list')


# AUTH

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related('product')
    return render(request, 'shop/order_detail.html', {
        'order': order,
        'items': items,
    })


# ADMIN DASHBOARD

@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    start_month = today.replace(day=1)

    orders_today = Order.objects.filter(created_at__date=today, status='PAID')
    orders_this_month = Order.objects.filter(created_at__date__gte=start_month, status='PAID')

    total_orders_today = orders_today.count()
    revenue_this_month = orders_this_month.aggregate(total=Sum('total_amount'))['total'] or 0

    low_stock_products = Product.objects.filter(stock__lt=5, is_active=True)

    last_7 = []
    for i in range(7):
        day = today - timezone.timedelta(days=i)
        sum_for_day = Order.objects.filter(created_at__date=day, status='PAID') \
            .aggregate(total=Sum('total_amount'))['total'] or 0
        last_7.append({'date': day.strftime('%Y-%m-%d'), 'revenue': float(sum_for_day)})
    last_7 = list(reversed(last_7))

    return render(request, 'shop/admin_dashboard.html', {
        'total_orders_today': total_orders_today,
        'revenue_this_month': revenue_this_month,
        'low_stock_products': low_stock_products,
        'last_7': last_7,
    })

@login_required
def add_review(request, slug):
    # slug here should be like 'iphone-15', not '1'
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Check if user has bought the product
    has_bought = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status__in=['PAID', 'SHIPPED', 'DELIVERED']
    ).exists()
    if not has_bought:
        return redirect('product_detail', slug=slug)

    # Existing review or new
    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).first()

    if request.method == 'POST':
        if existing_review:
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

    return redirect('product_detail', slug=slug)
