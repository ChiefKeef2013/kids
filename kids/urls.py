from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('enroll/<int:group_id>/', views.enroll_child, name='enroll'),
    path('api/group/<int:group_id>/capacity/', views.check_group_capacity, name='check_capacity'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload-certificate/<int:subscription_id>/', views.upload_certificate, name='upload_certificate'),
    path('export/attendance/', views.export_attendance, name='export_attendance'),
    path('login/', auth_views.LoginView.as_view(template_name='kids/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]