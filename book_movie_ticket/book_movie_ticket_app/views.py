from .models import *
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from datetime import datetime
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView

def homepage(request):
    if request.user.is_anonymous:
        return render(request, 'home.html') 
    # return HttpResponse(request.user)
    return book_ticket(request) # if user is logged in, redirect to book_ticket page
    
def book_ticket(request):
    username = request.user.username
    name = request.user.name
    age = request.user.age
    user_tickets = Ticket.objects.filter(user=request.user)
    for ticket in user_tickets:
        ticket.date_time = datetime.strptime(str(ticket.date_time).split('+')[0], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
    return render(request, 'book_ticket.html', {'username': username, 'name': name, 'age': age, 'user_tickets': user_tickets})
   
def user_login(request):
    show_login_form = True # to show login form 
    if request.method != 'POST':
        messages.error(request,"Vui lòng đăng nhập hoặc đăng ký để đặt vé")
        return render(request, 'home.html', {'show_login_form': show_login_form})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('rememberMe')
        
        if remember_me == 'on':
            request.session.set_expiry(1209600) # remember user account for 14 days
        
        if not username or not password:
            messages.error(request, "Vui lòng nhập tên tài khoản và mật khẩu!")
            return render(request, 'home.html', {'show_login_form': show_login_form})
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff == True:
                return redirect('/admin/')
            return book_ticket(request)
        else:
            messages.error(request, "Tên tài khoản hoặc mật khẩu không đúng!")
            return render(request, 'home.html', {'show_login_form': show_login_form})
        
def user_logout(request):
    logout(request)
    return homepage(request)
    
def user_register(request):
    show_register_form = True # to show register form
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        name = request.POST.get('name')
        age = request.POST.get('age')
        if not username or not password or not name or not age:
            messages.error(request, "Vui lòng điền đầy đủ thông tin!")
            return render(request, 'home.html', {'show_register_form': show_register_form})
                
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại! Vui lòng chọn tên đăng nhập khác!")
            return render(request, 'home.html', {'show_register_form': show_register_form})
        
        if password != password_confirm:
            messages.error(request, "Mật khẩu không trùng khớp!")
            return render(request, 'home.html', {'show_register_form': show_register_form})
        
        age = int(age)
        if age < 0 or age > 100:
            messages.error(request, "Tuổi không hợp lệ!")
            return render(request, 'home.html', {'show_register_form': show_register_form})
        
        user = CustomUser.objects.create_user(username=username, password=password, name=name, age=age)
        user.save()
        register_sucess = True # to show register success message
        show_register_form = False
        messages.success(request, "Đăng ký tài khoản thành công!")
        return render(request, 'home.html', {'register_sucess': register_sucess, 'show_register_form': show_register_form})
    else:
        return render(request, 'home.html', {'show_register_form': show_register_form})

def movie_schedule(request):
    return render(request, 'movie_schedule.html')

def contact(request):
    return render(request, 'contact.html')

def movie_list(request):
    form = BookTicketForm()
    movies = Movie.objects.all()
    rooms = Room.objects.all()
    seats = Seat.objects.all()
    return render(request, 'movie_list.html', {'movies': movies, 'rooms': rooms, 'seats': seats, 'form': form})

def get_seats(request):
    room_id = request.GET.get('room_id')
    seats = Seat.objects.filter(room_id=room_id)
    return render(request, 'book_ticket/seat_selection.html', {'seats': seats})

def user_booking(request):
    if request.method == 'POST':
        room = Room.objects.get(id=request.POST.get('room_id'))
        type = request.POST.get('type')
        date_time = request.POST.get('date_time')
        movie = Movie.objects.get(id=request.POST.get('movie_id'))
        selected_seats = request.POST.getlist('selected_seats[]')
        selected_seats = list(set(selected_seats))
        
        user = request.user
        
        tickets = []
        for seat_id in selected_seats:
            seat = Seat.objects.get(id=seat_id)
            if Ticket.objects.filter(seat=seat).exists():
                continue
            ticket = Ticket(
            movie=movie,
            user=user,
            room=room,
            seat=seat,
            price = 100000 if type == 'Adult' else 50000,
            type=type,
            date_time=date_time,
            )
            tickets.append(ticket)

        Ticket.objects.bulk_create(tickets)
        Seat.objects.filter(id__in=selected_seats).update(is_available=False)
        return HttpResponse('Success')
    else:
        return HttpResponse('Failed')
    
