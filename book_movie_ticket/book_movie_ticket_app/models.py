from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models import Max
from django.db.models import F
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('Phải có tên đăng nhập'))
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
                        help_text=_('Yêu cầu 30 ký tự hoặc ít hơn. Chỉ chứa chữ cái, số và các ký tự @/./+/-/_'),
                        error_messages={
                            'unique': _("Tên đăng nhập đã tồn tại."),
                        },
                        null=False, blank=False
                        )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Chỉ định người dùng có tất cả các quyền quản trị hệ thống.'
        ), 
    )                                              
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Chỉ định người dùng có quyền truy cập vào trang quản trị (admin).'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Chỉ định người dùng được coi là "active". Hủy chọn để vô hiệu hóa tài khoản này.'
        ),
    )
    last_login = models.DateTimeField(_('Lần đăng nhập cuối'), blank=True, null=True)
    USERNAME_FIELD = 'username'
    objects = CustomUserManager()
    
    name = models.CharField(_('Tên'), max_length=30, null=False, blank=False)
    age = models.IntegerField(_('Tuổi'), null=False, blank=False)
    
    REQUIRED_FIELDS = ['name', 'age']
    
    def get_name(self):
        return self.name
    
    def get_age(self):
        return self.age
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')
        ordering = ['username']
        
class BaseUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = _('Thông tin người dùng')
        verbose_name_plural = _('Thông tin người dùng')
        
class Movie(models.Model):
    id = models.AutoField(_('Mã phim'), primary_key=True)
    title = models.CharField(_('Tên phim'), max_length=100, null=False, blank=False)
    genre = models.CharField(_('Thể loại'), max_length=100, null=False, blank=False)
    duration = models.IntegerField(_('Thời lượng'), null=False, blank=False)
    director = models.CharField(_('Đạo diễn'), max_length=100, null=False, blank=False)
    release_date = models.DateField(_('Ngày công chiếu'), null=False, blank=False)
    description = models.TextField(_('Mô tả'), null=False, blank=False)
    # poster = models.URLField(_('Ảnh bìa'), null=False, blank=False)
    poster = models.ImageField(_('Ảnh bìa'), upload_to='movie_poster/', null=False, blank=False)
    
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Phim')
        verbose_name_plural = _('Phim')
        ordering = ['id']
        
class Room(models.Model):
    id = models.AutoField(_('Mã phòng'), primary_key=True)
    name = models.CharField(_('Tên phòng'), max_length=100, null=False, blank=False, help_text=_('VD: A, B, C...'))
    capacity = models.IntegerField(_('Sức chứa'), null=False, blank=False)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Phòng chiếu')
        verbose_name_plural = _('Phòng chiếu')
        ordering = ['id']
        
class Ticket(models.Model):
    id = models.AutoField(_('Mã vé'), primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Người đặt'))
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_('Phòng chiếu'))
    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    price = models.IntegerField(_('Giá vé'), null=True, blank=True)
    type = models.CharField(_('Loại vé'), max_length=100, null=False, blank=False, choices=[('Adult', 'Người lớn'), ('Child', 'Trẻ em')],)
    date_time = models.DateTimeField(_('Ngày giờ chiếu'), null=False, blank=False)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = _('Vé')
        verbose_name_plural = _('Vé')
        ordering = ['id']
            
class Seat(models.Model):
    id = models.AutoField(_('Mã ghế'), primary_key=True)
    seat_number = models.IntegerField(_('Số ghế'), null=False, blank=False)
    is_available = models.BooleanField(_('Trạng thái'), default=True, null=False, blank=False, choices=[(True, 'Còn trống'), (False, 'Đã đặt')])
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.seat_number)

    # Create seats when a room is created
    @receiver(post_save, sender=Room)
    def create_seats(sender, instance, created, **kwargs):
        if created:
            for i in range(1, instance.capacity+1):
                Seat.objects.create(room=instance, seat_number=i)     
                
    # Update the seat status when a ticket is created
    @receiver(post_save, sender=Ticket)
    def update_seat_status(sender, instance, created, **kwargs):
        if created:
            Seat.objects.filter(id=instance.seat_id).update(is_available=False)
        elif instance._state.adding is False:
            Seat.objects.filter(id=instance.seat_id).update(is_available=True) 

    class Meta:
        verbose_name = _('Ghế')
        verbose_name_plural = _('Ghế')
        ordering = ['id']
        

