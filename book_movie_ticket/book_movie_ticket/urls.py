"""
URL configuration for book_movie_ticket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from book_movie_ticket_app import views
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "Hệ thống quản lý rạp phim CinemaPlus"
admin.site.site_title = "Hệ thống quản lý rạp phim CinemaPlus"
admin.site.index_title = "Quản lý rạp phim CinemaPlus"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='trang-chu/')),
    path('trang-chu/', views.homepage, name='homepage'),
    path('lich-chieu/', views.movie_schedule, name='movie_schedule'),
    path('lien-he/', views.contact, name='contact'),
    path('dat-ve/', views.user_login, name='user_login'),
    path('dangxuat/', views.user_logout, name='user_logout'),
    path('dang-ky/', views.user_register, name='user_register'),
    path('phim/', views.movie_list, name='movie_list'),
    path('lay-ghe/', views.get_seats, name='get_seats'),
    path('dat-ve-phim/',views.user_booking, name='user_booking'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
