from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Sum, F
from datetime import timedelta
from .models import UserProfile, Farmer, ChickStock, ChickRequest, Sale, FeedStock
from .forms import CustomUserCreationForm

# Public view for farmers to track requests and serves as the homepage
def public_track_requests(request):
    requests = []
    error = None
    youth_nin = request.GET.get('youth_nin')
    if youth_nin:
        try:
            farmer = Farmer.objects.get(farmer_nin=youth_nin)
            requests = ChickRequest.objects.filter(farmer=farmer).order_by('-request_date')
        except Farmer.DoesNotExist:
            error = "No farmer found with that Youth NIN."
    return render(request, "track_requests_public.html", {'requests': requests, 'error': error})

# Login view for staff (brooder_manager and sales_rep)
def loginpage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
                role = user.userprofile.role
                if role == 'brooder_manager':
                    return redirect('brooder_manager_dashboard')
                elif role == 'sales_rep':
                    return redirect('sales_rep_dashboard')
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found. Please contact an administrator.")
                logout(request)
        
        messages.error(request, "Invalid username or password.")
            
    return render(request, "login.html")

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('public_track_requests')

# Admin-only user registration view with role selection
@staff_member_required
def admin_register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Ensure staff users have the correct flag
            user.save()
            # Link the UserProfile to the newly created user
            role = form.cleaned_data.get("role")
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, "User created successfully.")
            return redirect('admin:index')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})

# Brooder Manager dashboard with chick stock, pending requests, recent sales
@login_required
def brooder_manager_dashboard(request):
    if request.user.userprofile.role != 'brooder_manager':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    chick_stock = ChickStock.objects.all()
    pending_requests = ChickRequest.objects.filter(request_status='Pending')
    recent_sales = Sale.objects.order_by('-sale_date')[:5]
    return render(request, "brooder_manager_dashboard.html", {
        'chick_stock': chick_stock,
        'pending_requests': pending_requests,
        'recent_sales': recent_sales,
    })

# Brooder Manager approve/reject requests
@login_required
@staff_member_required
def manage_requests(request):
    if request.user.userprofile.role != 'brooder_manager':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    if request.method == 'POST':
        action = request.POST.get('action')
        req_id = request.POST.get('request_id')
        chick_request = get_object_or_404(ChickRequest, id=req_id)
        if action == 'approve':
            stock = ChickStock.objects.filter(
                chick_type__iexact=chick_request.chick_type,
                chick_breed__iexact=chick_request.chick_breed,
            ).first()
            if not stock or stock.chick_quantity < chick_request.quantity_requested:
                messages.error(request, "Insufficient stock for approval.")
            else:
                chick_request.request_status = 'Approved'
                chick_request.approval_date = now()
                chick_request.save()
                stock.chick_quantity -= chick_request.quantity_requested
                stock.save()
                messages.success(request, f"Request {req_id} approved.")
        elif action == 'reject':
            chick_request.request_status = 'Rejected'
            chick_request.save()
            messages.success(request, f"Request {req_id} rejected.")
        return redirect('manage_requests')
    
    pending_requests = ChickRequest.objects.filter(request_status='Pending')
    denied_requests = ChickRequest.objects.filter(request_status='Rejected')
    
    return render(request, "manage_requests.html", {
        'pending_requests': pending_requests,
        'denied_requests': denied_requests,
    })

# Brooder Manager manage chick stock
@login_required
@staff_member_required
def manage_stock(request):
    if request.user.userprofile.role != 'brooder_manager':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    chick_types = ChickRequest.CHICK_TYPE_CHOICES
    chick_breeds = ChickRequest.CHICK_BREED_CHOICES
    if request.method == 'POST':
        batch_number = request.POST.get('batch_number')
        chick_type = request.POST.get('chick_type')
        chick_breed = request.POST.get('chick_breed')
        chick_price = request.POST.get('chick_price')
        chick_quantity = request.POST.get('chick_quantity')
        chicks_period = request.POST.get('chicks_period')
        registered_by = request.user.username
        try:
            chick_quantity = int(chick_quantity)
            chicks_period = int(chicks_period)
            chick_price = int(chick_price)
            if chick_quantity < 0 or chicks_period < 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Quantity, price, and age must be positive integers.")
        else:
            ChickStock.objects.create(
                batch_number=batch_number,
                chick_type=chick_type,
                chick_breed=chick_breed,
                chick_price=chick_price,
                chick_quantity=chick_quantity,
                chicks_period=chicks_period,
                registered_by=registered_by,
                date_added=now(),
            )
            messages.success(request, "Chick stock added.")
            return redirect('manage_stock')
    stocks = ChickStock.objects.all()
    return render(request, "manage_stock.html", {'stocks': stocks, 'chick_types': chick_types, 'chick_breeds': chick_breeds})

# Brooder Manager manages feed stock
@login_required
@staff_member_required
def manage_feed_stock(request, pk=None):
    if request.user.userprofile.role != 'brooder_manager':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    
    feed_item = None
    if pk:
        feed_item = get_object_or_404(FeedStock, pk=pk)
        
    if request.method == 'POST':
        if 'delete' in request.POST:
            if feed_item:
                feed_item.delete()
                messages.success(request, "Feed stock item deleted successfully.")
            return redirect('manage_feed_stock')

        # Logic for adding or updating
        name = request.POST.get('name')
        feed_type = request.POST.get('feed_type')
        feed_brand = request.POST.get('feed_brand')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        buying_price = request.POST.get('buying_price')
        selling_price = request.POST.get('selling_price')
        supplier = request.POST.get('supplier')
        supplier_contact = request.POST.get('supplier_contact')

        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
            buying_price = float(buying_price) if buying_price else None
            selling_price = float(selling_price) if selling_price else None
        except (ValueError, TypeError):
            messages.error(request, "Please enter valid numbers for quantity and prices.")
            return redirect('manage_feed_stock', pk=pk or '')

        if feed_item:
            feed_item.name = name
            feed_item.feed_type = feed_type
            feed_item.feed_brand = feed_brand
            feed_item.quantity = quantity
            feed_item.unit_price = unit_price
            feed_item.buying_price = buying_price
            feed_item.selling_price = selling_price
            feed_item.supplier = supplier
            feed_item.supplier_contact = supplier_contact
            feed_item.save()
            messages.success(request, "Feed stock item updated successfully.")
        else:
            FeedStock.objects.create(
                name=name,
                feed_type=feed_type,
                feed_brand=feed_brand,
                quantity=quantity,
                unit_price=unit_price,
                buying_price=buying_price,
                selling_price=selling_price,
                supplier=supplier,
                supplier_contact=supplier_contact
            )
            messages.success(request, "Feed stock item added successfully.")
        return redirect('manage_feed_stock')

    feeds = FeedStock.objects.all()
    return render(request, "manage_feed_stock.html", {'feeds': feeds, 'feed_item': feed_item})

# Sales Rep dashboard showing pending requests and recent sales
@login_required
def sales_rep_dashboard(request):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    pending_requests = ChickRequest.objects.filter(request_status='Pending')
    recent_sales = Sale.objects.order_by('-sale_date')[:5]
    denied_requests = ChickRequest.objects.filter(request_status='Rejected')
    return render(request, "sales_rep_dashboard.html", {
        'pending_requests': pending_requests,
        'recent_sales': recent_sales,
        'denied_requests': denied_requests,
    })

# Sales Rep submit chick requests on behalf of farmers
@login_required
@staff_member_required
def submit_request(request):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    chick_types = ChickRequest.CHICK_TYPE_CHOICES
    chick_breeds = ChickRequest.CHICK_BREED_CHOICES
    farmer_types = ChickRequest.FARMER_TYPES
    if request.method == 'POST':
        farmer_nin = request.POST.get('farmer_nin')
        chick_type = request.POST.get('chick_type')
        chick_breed = request.POST.get('chick_breed')
        quantity_requested = request.POST.get('quantity_requested')
        farmer_type = request.POST.get('farmer_type')
        
        try:
            quantity_requested = int(quantity_requested)
            farmer = Farmer.objects.get(farmer_nin=farmer_nin)
            
            # Check for returning farmer's eligibility
            last_request = ChickRequest.objects.filter(farmer=farmer, request_status='Fulfilled').order_by('-request_date').first()
            if last_request and (now().date() - last_request.request_date.date()).days < 120:
                messages.warning(request, f"This farmer is a returning customer and must wait at least 4 months before a new request. They can request again on {last_request.request_date.date() + timedelta(days=120)}.")
                return redirect('submit_request')

        except (ValueError, Farmer.DoesNotExist):
            messages.error(request, "Invalid input or farmer not registered.")
            return redirect('submit_request')
        
        limit = 100 if farmer.farmer_type == 'Starter' else 500
        if quantity_requested > limit:
            messages.error(request, f"Quantity exceeds the limit of {limit} for farmer type.")
            return redirect('submit_request')
        available_stock = ChickStock.objects.filter(
            chick_type__iexact=chick_type,
            chick_breed__iexact=chick_breed,
        ).aggregate(total=Sum('chick_quantity'))['total'] or 0
        if quantity_requested > available_stock:
            messages.error(request, "Requested quantity exceeds available stock.")
            return redirect('submit_request')
        ChickRequest.objects.create(
            farmer=farmer,
            farmer_type=farmer_type,
            chick_type=chick_type,
            chick_breed=chick_breed,
            quantity_requested=quantity_requested,
            request_date=now(),
            request_status='Pending',
            delivered='NO',
            payment_status='pending'
        )
        messages.success(request, "Chick request submitted.")
        return redirect('submit_request')
    return render(request, "submit_request.html", {
        'chick_types': chick_types,
        'chick_breeds': chick_breeds,
        'farmer_types': farmer_types,
    })

# Sales Rep process sales and mark requests fulfilled
@login_required
@staff_member_required
def process_sales(request):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')
    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        chick_request = get_object_or_404(ChickRequest, id=req_id)
        if chick_request.request_status != 'Approved':
            messages.error(request, "Only approved requests can be processed.")
            return redirect('process_sales')
        chick_request.request_status = 'Fulfilled'
        chick_request.save()
        price_per_unit = 1650
        quantity = chick_request.quantity_requested
        total_amount = price_per_unit * quantity
        feed_due_date = now().date() + timedelta(days=60)
        
        # Reduce feed stock quantity
        feed_bags_to_reduce = 2  # Assuming 2 bags per sale for now
        try:
            generic_feed = FeedStock.objects.get(name__iexact='generic feed')
            if generic_feed.quantity >= feed_bags_to_reduce:
                generic_feed.quantity -= feed_bags_to_reduce
                generic_feed.save()
            else:
                messages.warning(request, "Not enough feed stock to deduct for this sale.")
        except FeedStock.DoesNotExist:
            messages.warning(request, "Generic feed stock item not found.")
            
        Sale.objects.create(
            customer=chick_request.farmer,
            chick_request=chick_request,
            sale_date=now(),
            quantity_sold=quantity,
            amount=total_amount,
            feed_bags_eligible=feed_bags_to_reduce,
            feed_payment_due_date=feed_due_date,
            payment_status='pending',
            payment_method='cash',
        )
        messages.success(request, f"Sale processed for request {req_id}.")
        return redirect('process_sales')
    approved_requests = ChickRequest.objects.filter(request_status='Approved')
    return render(request, "process_sales.html", {'approved_requests': approved_requests})

# New view to list all sales
@login_required
@staff_member_required
def view_all_sales(request):
    sales = Sale.objects.order_by('-sale_date')
    return render(request, "all_sales.html", {'sales': sales})


@login_required
def register_farmer(request):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied. Only Sales Representatives can register farmers.")
        return redirect('loginpage')
    
    if request.method == 'POST':
        farmer_name = request.POST.get('farmer_name')
        farmer_nin = request.POST.get('farmer_nin')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        farmer_type = request.POST.get('farmer_type')
        registration_date = request.POST.get('registration_date')
        recommender_name = request.POST.get('recommender_name')
        recommender_nin = request.POST.get('recommender_nin')
        recommender_tel = request.POST.get('recommender_tel')
        email = request.POST.get('email')

        if Farmer.objects.filter(farmer_nin=farmer_nin).exists():
            messages.error(request, "A farmer with this NIN already exists.")
        else:
            Farmer.objects.create(
                farmer_name=farmer_name,
                farmer_nin=farmer_nin,
                gender=gender,
                date_of_birth=date_of_birth,
                phone_number=phone_number,
                address=address,
                farmer_type=farmer_type,
                registration_date = registration_date,
                recommender_nin=recommender_nin,
                recommender_tel=recommender_tel,
                email=email,
            )
            messages.success(request, "Farmer registered successfully!")
            return redirect('list_farmers')

    farmer_types = ChickRequest.FARMER_TYPES
    return render(request, "register_farmer.html", {'farmer_types': farmer_types})

@login_required
def list_farmers(request):
    farmers = Farmer.objects.all().order_by('farmer_name')
    return render(request, 'list_farmers.html', {'farmers': farmers})

@login_required
def farmer_detail(request, pk):
    farmer = get_object_or_404(Farmer, pk=pk)
    return render(request, 'farmer_detail.html', {'farmer': farmer})

@login_required
def farmer_update(request, pk):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied. Only Sales Representatives can update farmer details.")
        return redirect('loginpage')
    
    farmer = get_object_or_404(Farmer, pk=pk)
    if request.method == 'POST':
        farmer.farmer_name = request.POST.get('farmer_name')
        farmer.gender = request.POST.get('gender')
        farmer.date_of_birth = request.POST.get('date_of_birth')
        farmer.phone_number = request.POST.get('phone_number')
        farmer.address = request.POST.get('address')
        farmer.farmer_type = request.POST.get('farmer_type')
        farmer.recommender_name = request.POST.get('recommender_name')
        farmer.recommender_nin = request.POST.get('recommender_nin')
        farmer.recommender_tel = request.POST.get('recommender_tel')
        farmer.email = request.POST.get('email')
        farmer.registration_date = request.POST.get('registration_date')
        farmer.save()
        messages.success(request, "Farmer details updated successfully!")
        return redirect('farmer_detail', pk=farmer.pk)

    farmer_types = ChickRequest.FARMER_TYPES
    return render(request, 'farmer_update.html', {'farmer': farmer, 'farmer_types': farmer_types})

@login_required
def farmer_delete(request, pk):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied. Only Sales Representatives can delete farmer records.")
        return redirect('loginpage')
    
    farmer = get_object_or_404(Farmer, pk=pk)
    if request.method == 'POST':
        farmer.delete()
        messages.success(request, "Farmer record deleted successfully!")
        return redirect('list_farmers')

    return render(request, 'farmer_delete.html', {'farmer': farmer})


# Chick Request CRUD
@login_required
@staff_member_required
def chick_request_detail(request, pk):
    chick_request = get_object_or_404(ChickRequest, pk=pk)
    return render(request, 'chick_request_detail.html', {'chick_request': chick_request})

@login_required
@staff_member_required
def chick_request_update(request, pk):
    chick_request = get_object_or_404(ChickRequest, pk=pk)
    if request.method == 'POST':
        # Update logic here based on form data
        messages.success(request, 'Request updated successfully.')
        return redirect('chick_request_detail', pk=pk)
    return render(request, 'chick_request_update.html', {'chick_request': chick_request})

@login_required
@staff_member_required
def chick_request_delete(request, pk):
    chick_request = get_object_or_404(ChickRequest, pk=pk)
    if request.method == 'POST':
        chick_request.delete()
        messages.success(request, 'Request deleted successfully.')
        return redirect('manage_requests')
    return render(request, 'chick_request_delete.html', {'chick_request': chick_request})

# Chick Stock CRUD
@login_required
@staff_member_required
def chick_stock_detail(request, pk):
    chick_stock = get_object_or_404(ChickStock, pk=pk)
    return render(request, 'chick_stock_detail.html', {'chick_stock': chick_stock})

@login_required
@staff_member_required
def chick_stock_update(request, pk):
    chick_stock = get_object_or_404(ChickStock, pk=pk)
    if request.method == 'POST':
        chick_stock.batch_number = request.POST.get('batch_number', chick_stock.batch_number)
        chick_stock.chick_type = request.POST.get('chick_type', chick_stock.chick_type)
        chick_stock.chick_breed = request.POST.get('chick_breed', chick_stock.chick_breed)
        chick_stock.chick_price = request.POST.get('chick_price', chick_stock.chick_price)
        chick_stock.chick_quantity = request.POST.get('chick_quantity', chick_stock.chick_quantity)
        chick_stock.chicks_period = request.POST.get('chicks_period', chick_stock.chicks_period)
        chick_stock.save()
        messages.success(request, 'Chick stock updated successfully.')
        return redirect('chick_stock_detail', pk=pk)
    return render(request, 'chick_stock_update.html', {'chick_stock': chick_stock})

@login_required
@staff_member_required
def chick_stock_delete(request, pk):
    chick_stock = get_object_or_404(ChickStock, pk=pk)
    if request.method == 'POST':
        chick_stock.delete()
        messages.success(request, 'Stock deleted successfully.')
        return redirect('manage_stock')
    return render(request, 'chick_stock_delete.html', {'chick_stock': chick_stock})

# Feed Stock CRUD
@login_required
@staff_member_required
def feed_stock_detail(request, pk):
    feed_item = get_object_or_404(FeedStock, pk=pk)
    return render(request, 'feed_stock_detail.html', {'feed_item': feed_item})

@login_required
@staff_member_required
def feed_stock_update(request, pk):
    feed_item = get_object_or_404(FeedStock, pk=pk)
    if request.method == 'POST':
        feed_item.name = request.POST.get('name', feed_item.name)
        feed_item.feed_type = request.POST.get('feed_type', feed_item.feed_type)
        feed_item.feed_brand = request.POST.get('feed_brand', feed_item.feed_brand)
        feed_item.quantity = request.POST.get('quantity', feed_item.quantity)
        feed_item.unit_price = request.POST.get('unit_price', feed_item.unit_price)
        feed_item.buying_price = request.POST.get('buying_price', feed_item.buying_price)
        feed_item.selling_price = request.POST.get('selling_price', feed_item.selling_price)
        feed_item.supplier = request.POST.get('supplier', feed_item.supplier)
        feed_item.supplier_contact = request.POST.get('supplier_contact', feed_item.supplier_contact)
        feed_item.save()
        messages.success(request, 'Feed stock updated successfully.')
        return redirect('feed_stock_detail', pk=pk)
    return render(request, 'feed_stock_update.html', {'feed_item': feed_item})

@login_required
@staff_member_required
def feed_stock_delete(request, pk):
    feed_item = get_object_or_404(FeedStock, pk=pk)
    if request.method == 'POST':
        feed_item.delete()
        messages.success(request, 'Feed stock deleted successfully.')
        return redirect('manage_feed_stock')
    return render(request, 'feed_stock_delete.html', {'feed_item': feed_item})

# Sale CRUD
@login_required
@staff_member_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sale_detail.html', {'sale': sale})

@login_required
@staff_member_required
def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.quantity_sold = request.POST.get('quantity_sold', sale.quantity_sold)
        sale.amount = request.POST.get('amount', sale.amount)
        sale.payment_status = request.POST.get('payment_status', sale.payment_status)
        sale.payment_method = request.POST.get('payment_method', sale.payment_method)
        sale.save()
        messages.success(request, 'Sale updated successfully.')
        return redirect('sale_detail', pk=pk)
    return render(request, 'sale_update.html', {'sale': sale})

@login_required
@staff_member_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sale deleted successfully.')
        return redirect('sales_rep_dashboard')
    return render(request, 'sale_delete.html', {'sale': sale})
    
# New report view for Brooder Manager
@login_required
@staff_member_required
def brooder_manager_report(request):
    if request.user.userprofile.role != 'brooder_manager':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')

    # Chick Stock Calculations
    total_chicks = ChickStock.objects.aggregate(Sum('chick_quantity'))['chick_quantity__sum'] or 0
    local_chicks = ChickStock.objects.filter(chick_type='Local').aggregate(Sum('chick_quantity'))['chick_quantity__sum'] or 0
    exotic_chicks = ChickStock.objects.filter(chick_type='Exotic').aggregate(Sum('chick_quantity'))['chick_quantity__sum'] or 0
    broiler_chicks = ChickStock.objects.filter(chick_breed='Broiler').aggregate(Sum('chick_quantity'))['chick_quantity__sum'] or 0
    layer_chicks = ChickStock.objects.filter(chick_breed='Layer').aggregate(Sum('chick_quantity'))['chick_quantity__sum'] or 0

    # Feed Stock Calculations
    total_feed_quantity = FeedStock.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Simple profit calculation based on current stock
    # This assumes all current stock will be sold at the selling price.
    total_potential_profit = FeedStock.objects.aggregate(
        total=Sum(F('selling_price') * F('quantity')) - Sum(F('buying_price') * F('quantity'))
    )['total'] or 0

    # Farmer Counts
    total_farmers = Farmer.objects.count()
    starter_farmers = Farmer.objects.filter(farmer_type='Starter').count()
    returning_farmers = Farmer.objects.filter(farmer_type='Returning').count()

    context = {
        'total_chicks': total_chicks,
        'local_chicks': local_chicks,
        'exotic_chicks': exotic_chicks,
        'broiler_chicks': broiler_chicks,
        'layer_chicks': layer_chicks,
        'total_feed_quantity': total_feed_quantity,
        'total_potential_profit': total_potential_profit,
        'total_farmers': total_farmers,
        'starter_farmers': starter_farmers,
        'returning_farmers': returning_farmers,
    }
    return render(request, 'report.html', context)

# New report view for Sales Rep
@login_required
@staff_member_required
def sales_rep_report(request):
    if request.user.userprofile.role != 'sales_rep':
        messages.error(request, "Permission denied.")
        return redirect('loginpage')

    # Calculate metrics for Sales Rep
    total_farmers = Farmer.objects.count()
    starter_farmers = Farmer.objects.filter(farmer_type='Starter').count()
    returning_farmers = Farmer.objects.filter(farmer_type='Returning').count()
    total_sales = Sale.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_requests_submitted = ChickRequest.objects.count()
    approved_requests = ChickRequest.objects.filter(request_status='Approved').count()
    denied_requests = ChickRequest.objects.filter(request_status='Rejected').count()
    
    context = {
        'total_farmers': total_farmers,
        'starter_farmers': starter_farmers,
        'returning_farmers': returning_farmers,
        'total_sales': total_sales,
        'total_requests_submitted': total_requests_submitted,
        'approved_requests': approved_requests,
        'denied_requests': denied_requests,
    }
    return render(request, 'report.html', context)