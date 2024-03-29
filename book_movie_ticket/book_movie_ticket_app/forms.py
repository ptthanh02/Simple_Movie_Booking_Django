from django import forms
from django.forms import ModelForm
from .models import *
from datetime import date
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class CustomUserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'name', 'age', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tuổi'}),
        }
    
    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 18:
            raise forms.ValidationError("Bạn phải đủ 18 tuổi để đăng ký tài khoản.")
        return age
    
    def clean_password(self):
        password = self.cleaned_data['password']
        
        error_messages = {
            "This password is too short. It must contain at least 8 characters.": "Mật khẩu phải có ít nhất 8 ký tự.",
            "This password is too common.": "Mật khẩu quá phổ biến.",
            "This password is entirely numeric.": "Mật khẩu không được toàn số.",
            "This password is too similar to the username.": "Mật khẩu không được giống tên đăng nhập.",
            "The password is too similar to the email address.": "Mật khẩu không được giống email.",
            "The password is too similar to the first name.": "Mật khẩu không được giống tên.",
            "The password is too similar to the last name.": "Mật khẩu không được giống họ.",
            "The password is too similar to the common sequences.": "Mật khẩu không được giống chuỗi phổ biến."
        }
        
        try:
            validate_password(password)
        except ValidationError as error:
            error_messages_vietnamese = [error_messages.get(msg, msg) for msg in error.messages]
            raise forms.ValidationError("Mật khẩu không đúng định dạng. " + " ".join(error_messages_vietnamese))
        
        return password
    
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Mật khẩu hiện tại',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    confirm_password = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Mật khẩu hiện tại không chính xác.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Mật khẩu mới và xác nhận mật khẩu không khớp.')

        return cleaned_data

    def save(self):
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        
class MovieForm(ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'genre', 'release_date', 'director', 'description', 'poster']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên phim'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Đạo diễn'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Mô tả'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Ngày phát hành'}),
        }
            
    def clean_release_date(self):
        release_date = self.cleaned_data['release_date']
        if release_date > date.today():
            raise forms.ValidationError("Ngày phát hành không hợp lệ.")
        return release_date
    
class BookTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['room', 'type', 'date_time']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'placeholder': 'Ngày giờ chiếu'}),
        }

        
    

        
        