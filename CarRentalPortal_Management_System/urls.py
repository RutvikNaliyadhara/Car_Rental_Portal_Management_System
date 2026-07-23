from django.contrib import admin
from django.urls import path
from carRental.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('about', about, name='about'),
    path('carlist', carlist, name='carlist'),
    path('carDetails/<int:pid>', carDetails, name='carDetails'),
    path('contact', contact, name='contact'),
    path('admin_login', admin_login, name='admin_login'),
    path('user_login', user_login, name='user_login'),
    path('signup', signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
    path('brands', brands, name='brands'),
    path('editBrand/<int:pid>', editBrand, name='editBrand'),
    path('deleteBrand/<int:pid>', deleteBrand, name='deleteBrand'),
    path('addVehicle', addVehicle, name='addVehicle'),
    path('manageVehicle', manageVehicle, name='manageVehicle'),
    path('editVehicle/<int:pid>', editVehicle, name='editVehicle'),
    path('deleteVehicle/<int:pid>', deleteVehicle, name='deleteVehicle'),
    path('newBooking', newBooking, name='newBooking'),
    path('confirmBooking', confirmBooking, name='confirmBooking'),
    path('cancelBooking', cancelBooking, name='cancelBooking'),
    path('allBooking', allBooking, name='allBooking'),
    path('deleteBooking/<int:pid>', deleteBooking, name='deleteBooking'),
    path('viewBooking/<int:pid>', viewBooking, name='viewBooking'),
    path('unreadQuery', unreadQuery, name='unreadQuery'),
    path('readQuery', readQuery, name='readQuery'),
    path('viewQuery/<int:pid>', viewQuery, name='viewQuery'),
    path('deleteQuery/<int:pid>', deleteQuery, name='deleteQuery'),
    path('regUser', regUser, name='regUser'),
    path('search', search, name='search'),
    path('betweendateReport', betweendateReport, name='betweendateReport'),
    path('deleteUser/<int:pid>', deleteUser, name='deleteUser'),
    path('changePassword', changePassword, name='changePassword'),
    path('logout/', Logout, name='logout'),

    path('userindex', userindex, name='userindex'),
    path('vehicleDetails/<int:pid>', vehicleDetails, name='vehicleDetails'),
    path('userabout', userabout, name='userabout'),
    path('usercarlist', usercarlist, name='usercarlist'),
    path('myProfile', myProfile, name='myProfile'),
    path('myBooking', myBooking, name='myBooking'),
    path('mybookingDtls/<int:pid>', mybookingDtls, name='mybookingDtls'),
    path('mychangePassword', mychangePassword, name='mychangePassword'),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
