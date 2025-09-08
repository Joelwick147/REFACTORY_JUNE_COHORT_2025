"""
URL configuration for chicks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app2 import views

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    # Public & Authentication
    path('', views.public_track_requests, name='public_track_requests'),
    path('login/', views.loginpage, name='loginpage'),
    path('logout/', views.logout_view, name='logout_view'),
    path('admin-register/', views.admin_register, name='admin_register'),

    # Brooder Manager Dashboard
    path('brooder-manager/dashboard/', views.brooder_manager_dashboard, name='brooder_manager_dashboard'),
    path('brooder-manager/manage-requests/', views.manage_requests, name='manage_requests'),
    path('brooder-manager/manage-stock/', views.manage_stock, name='manage_stock'),
    path('brooder-manager/manage-feed-stock/', views.manage_feed_stock, name='manage_feed_stock'),
    path('brooder-manager/report/', views.brooder_manager_report, name='brooder_manager_report'),
    # Sales Representative Dashboard
    path('sales-rep/dashboard/', views.sales_rep_dashboard, name='sales_rep_dashboard'),
    path('sales-rep/submit-request/', views.submit_request, name='submit_request'),
    path('sales-rep/process-sales/', views.process_sales, name='process_sales'),
    path('sales-rep/view-all-sales/', views.view_all_sales, name='view_all_sales'),

    # CRUD for Farmers
    path('farmers/', views.list_farmers, name='list_farmers'),
    path('farmers/register/', views.register_farmer, name='register_farmer'),
    path('farmers/<int:pk>/', views.farmer_detail, name='farmer_detail'),
    path('farmers/update/<int:pk>/', views.farmer_update, name='farmer_update'),
    path('farmers/delete/<int:pk>/', views.farmer_delete, name='farmer_delete'),

    # CRUD for Chick Requests
    path('requests/<int:pk>/', views.chick_request_detail, name='chick_request_detail'),
    path('requests/update/<int:pk>/', views.chick_request_update, name='chick_request_update'),
    path('requests/delete/<int:pk>/', views.chick_request_delete, name='chick_request_delete'),

    # CRUD for Chick Stock
    path('stock/<int:pk>/', views.chick_stock_detail, name='chick_stock_detail'),
    path('stock/update/<int:pk>/', views.chick_stock_update, name='chick_stock_update'),
    path('stock/delete/<int:pk>/', views.chick_stock_delete, name='chick_stock_delete'),

    # CRUD for Feed Stock
    path('feed-stock/detail/<int:pk>/', views.feed_stock_detail, name='feed_stock_detail'),
    path('feed-stock/update/<int:pk>/', views.feed_stock_update, name='feed_stock_update'),
    path('feed-stock/delete/<int:pk>/', views.feed_stock_delete, name='feed_stock_delete'),

    # CRUD for Sales
    path('sales/detail/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/update/<int:pk>/', views.sale_update, name='sale_update'),
    path('sales/delete/<int:pk>/', views.sale_delete, name='sale_delete'),
    
    #Sales
    path('dashboard/', views.sales_rep_dashboard, name='sales_rep_dashboard'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('process-sales/', views.process_sales, name='process_sales'),
    path('report/', views.sales_rep_report, name='sales_rep_report'),
    
    
]

    

