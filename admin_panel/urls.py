"""admin_panel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path ,include
from dashboard import views
from customer.views import toggle_store_data

urlpatterns = [
    path('admin/', admin.site.urls),
    #  path("create-order/<int:user_id>/", views.create_order),
    # path("verify-payment/", views.verify_payment),
    path("get-urls/", views.get_urls),
    path("add-url-page/", views.add_url_page,name="add_url_page"),
    path("chatbot/<int:user_id>", views.chatbot_page),
    path("api/", include("dashboard.urls")),
    path("customer/", include("customer.urls")),
    path("verify-user/", views.verify_user),
    path("user-list/", views.user_list,name='user_list'),
    path("", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('toggle-store-data/', toggle_store_data, name='toggle_store_data'),

]
