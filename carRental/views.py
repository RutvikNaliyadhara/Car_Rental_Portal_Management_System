import datetime
from datetime import datetime as dt, date
import json
import random

from django.contrib.auth import authenticate, logout, login
from django.db import transaction
from django.db.models import Q, Case, When
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from .models import *
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm


# Create your views here.

def index(request):
    vehicles = Vehicles.objects.all()
    return render(request, 'index.html', locals())


def about(request):
    return render(request, 'about.html')


def carlist(request):
    vehicles = Vehicles.objects.all()
    brand = Brands.objects.all()
    if request.method == "POST":
        brandid = request.POST['brand']
        fuelType = request.POST['fuelType']

        brands = Brands.objects.get(id=brandid)
        vehicles = Vehicles.objects.filter(Q(FuelType=fuelType) & Q(VehiclesBrand=brands))
        vehiclescount = Vehicles.objects.filter(Q(FuelType=fuelType) & Q(VehiclesBrand=brands)).count()
        return render(request, 'searchcarList.html', locals())
    return render(request, 'carlist.html', locals())


def auto_complete_expired_bookings():
    try:
        Booking.objects.filter(Status='Confirm', ToDate__lt=date.today()).update(
            Status='Completed',
            LastUpdationDate=date.today()
        )
    except Exception:
        pass


def carDetails(request, pid):
    auto_complete_expired_bookings()
    vehicle = Vehicles.objects.get(id=pid)
    vehicleid = vehicle.id
    vehiclebrand = vehicle.VehiclesBrand
    similarvehicle = Vehicles.objects.exclude(id=vehicleid).order_by(
        Case(
            When(VehiclesBrand=vehiclebrand, then=0),
            default=1
        ),
        '-id'
    )
    if not similarvehicle.exists():
        similarvehicle = Vehicles.objects.all()
    today = date.today().strftime('%Y-%m-%d')
    today_date = date.today()
    existing_bookings = Booking.objects.filter(
        VehicleId=vehicle,
        ToDate__gte=today_date
    ).exclude(Status__in=['Cancel', 'Completed']).order_by('FromDate')
    return render(request, 'carDetails.html', locals())


def contact(request):
    error = ""
    if request.method == "POST":
        Name = request.POST['Name']
        EmailId = request.POST['EmailId']
        ContactNo = request.POST['ContactNo']
        Message = request.POST['Message']

        try:
            Contactusquery.objects.create(Name=Name, EmailId=EmailId, ContactNo=ContactNo, Message=Message)
            error = "no"
        except:
            error = "yes"
    return render(request, 'contact.html', locals())


def admin_login(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    return render(request, 'admin_login.html', locals())


def signup(request):
    error = ""
    error_msg = ""
    if request.method == "POST":
        fname = request.POST.get('firstName', '').strip()
        lname = request.POST.get('lastName', '').strip()
        ContactNo = request.POST.get('ContactNo', '').strip()
        dob = request.POST.get('dob', '').strip()
        email = request.POST.get('emailid', '').strip()
        password = request.POST.get('password', '').strip()
        Country = request.POST.get('Country', '').strip()
        City = request.POST.get('City', '').strip()
        Address = request.POST.get('Address', '').strip()

        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            error = "user_exists"
            error_msg = f"An account with email '{email}' already exists! Please login instead."
        else:
            dob_date = None
            if dob:
                for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                    try:
                        dob_date = dt.strptime(dob, fmt).date()
                        break
                    except ValueError:
                        pass

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=fname,
                        last_name=lname
                    )
                    UserDetails.objects.create(
                        user=user,
                        ContactNo=ContactNo,
                        dob=dob_date,
                        Country=Country,
                        City=City,
                        Address=Address
                    )
                    error = "no"
            except Exception as e:
                error = "yes"
                error_msg = str(e)
    return render(request, 'signup.html', locals())


def user_login(request):
    error = ""
    if request.method == 'POST':
        e = request.POST['emailid']
        p = request.POST['password']
        user = authenticate(username=e, password=p)
        try:
            if user:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    return render(request, 'user_login.html', locals())


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    totaluser = UserDetails.objects.all().count()
    totalbooking = Booking.objects.all().count()
    totalbrand = Brands.objects.all().count()
    totalvehicle = Vehicles.objects.all().count()
    totalunread = Contactusquery.objects.filter(Status=None).count()
    totalread = Contactusquery.objects.filter(Status='yes').count()
    return render(request, 'admin/dashboard.html', locals())


def brands(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    brand = Brands.objects.all()
    try:
        if request.method == "POST":
            BrandName = request.POST['BrandName']
            try:
                Brands.objects.create(BrandName=BrandName)
                error = "no"
            except:
                error = "yes"
    except:
        pass
    return render(request, 'admin/brands.html', locals())


def editBrand(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    brand = Brands.objects.get(id=pid)
    if request.method == "POST":
        BrandName = request.POST['BrandName']

        brand.BrandName = BrandName

        try:
            brand.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/editBrand.html', locals())


def deleteBrand(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    brand = Brands.objects.get(id=pid)
    brand.delete()
    return redirect('brands')


def addVehicle(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    brands = Brands.objects.all()
    error = ""
    if request.method == "POST":
        brandid = request.POST['VehiclesBrand']
        brandsid = Brands.objects.get(id=brandid)

        VehiclesTitle = request.POST['VehiclesTitle']
        VehiclesOverview = request.POST['VehiclesOverview']
        PricePerDay = request.POST['PricePerDay']
        FuelType = request.POST['FuelType']
        ModelYear = request.POST['ModelYear']
        SeatingCapacity = request.POST['SeatingCapacity']
        Vimage1 = request.FILES['Vimage1']
        Vimage2 = request.FILES['Vimage2']
        Vimage3 = request.FILES['Vimage3']
        Vimage4 = request.FILES['Vimage4']
        Vimage5 = request.FILES['Vimage5']

        if 'AirConditioner' in request.POST:
            AirConditioner = request.POST['AirConditioner']
        else:
            AirConditioner = "no"

        if 'PowerDoorLocks' in request.POST:
            PowerDoorLocks = request.POST['PowerDoorLocks']
        else:
            PowerDoorLocks = "no"

        if 'AntiLockBrakingSystem' in request.POST:
            AntiLockBrakingSystem = request.POST['AntiLockBrakingSystem']
        else:
            AntiLockBrakingSystem = "no"

        if 'BrakeAssist' in request.POST:
            BrakeAssist = request.POST['BrakeAssist']
        else:
            BrakeAssist = "no"

        if 'PowerSteering' in request.POST:
            PowerSteering = request.POST['PowerSteering']
        else:
            PowerSteering = "no"

        if 'DriverAirbag' in request.POST:
            DriverAirbag = request.POST['DriverAirbag']
        else:
            DriverAirbag = "no"

        if 'PassengerAirbag' in request.POST:
            PassengerAirbag = request.POST['PassengerAirbag']
        else:
            PassengerAirbag = "no"

        if 'PowerWindows' in request.POST:
            PowerWindows = request.POST['PowerWindows']
        else:
            PowerWindows = "no"

        if 'CDPlayer' in request.POST:
            CDPlayer = request.POST['CDPlayer']
        else:
            CDPlayer = "no"

        if 'CentralLocking' in request.POST:
            CentralLocking = request.POST['CentralLocking']
        else:
            CentralLocking = "no"

        if 'CrashSensor' in request.POST:
            CrashSensor = request.POST['CrashSensor']
        else:
            CrashSensor = "no"

        if 'LeatherSeats' in request.POST:
            LeatherSeats = request.POST['LeatherSeats']
        else:
            LeatherSeats = "no"

        try:
            Vehicles.objects.create(VehiclesBrand=brandsid, VehiclesTitle=VehiclesTitle,
                                    VehiclesOverview=VehiclesOverview, PricePerDay=PricePerDay,
                                    FuelType=FuelType, ModelYear=ModelYear, SeatingCapacity=SeatingCapacity,
                                    Vimage1=Vimage1,
                                    Vimage2=Vimage2, Vimage3=Vimage3, Vimage4=Vimage4, Vimage5=Vimage5,
                                    AirConditioner=AirConditioner,
                                    PowerDoorLocks=PowerDoorLocks, AntiLockBrakingSystem=AntiLockBrakingSystem,
                                    BrakeAssist=BrakeAssist,
                                    PowerSteering=PowerSteering, DriverAirbag=DriverAirbag,
                                    PassengerAirbag=PassengerAirbag, PowerWindows=PowerWindows,
                                    CDPlayer=CDPlayer, CentralLocking=CentralLocking, CrashSensor=CrashSensor,
                                    LeatherSeats=LeatherSeats)
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/addVehicle.html', locals())


def manageVehicle(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicles.objects.all()
    return render(request, 'admin/manageVehicle.html', locals())


def editVehicle(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    brands = Brands.objects.all()
    vehicle = Vehicles.objects.get(id=pid)
    if request.method == "POST":
        brandid = request.POST['VehiclesBrand']
        brandsid = Brands.objects.get(id=brandid)

        VehiclesTitle = request.POST['VehiclesTitle']
        VehiclesOverview = request.POST['VehiclesOverview']
        PricePerDay = request.POST['PricePerDay']
        FuelType = request.POST['FuelType']
        ModelYear = request.POST['ModelYear']
        SeatingCapacity = request.POST['SeatingCapacity']

        if 'AirConditioner' in request.POST:
            AirConditioner = request.POST['AirConditioner']
        else:
            AirConditioner = "no"

        if 'PowerDoorLocks' in request.POST:
            PowerDoorLocks = request.POST['PowerDoorLocks']
        else:
            PowerDoorLocks = "no"

        if 'AntiLockBrakingSystem' in request.POST:
            AntiLockBrakingSystem = request.POST['AntiLockBrakingSystem']
        else:
            AntiLockBrakingSystem = "no"

        if 'BrakeAssist' in request.POST:
            BrakeAssist = request.POST['BrakeAssist']
        else:
            BrakeAssist = "no"

        if 'PowerSteering' in request.POST:
            PowerSteering = request.POST['PowerSteering']
        else:
            PowerSteering = "no"

        if 'DriverAirbag' in request.POST:
            DriverAirbag = request.POST['DriverAirbag']
        else:
            DriverAirbag = "no"

        if 'PassengerAirbag' in request.POST:
            PassengerAirbag = request.POST['PassengerAirbag']
        else:
            PassengerAirbag = "no"

        if 'PowerWindows' in request.POST:
            PowerWindows = request.POST['PowerWindows']
        else:
            PowerWindows = "no"

        if 'CDPlayer' in request.POST:
            CDPlayer = request.POST['CDPlayer']
        else:
            CDPlayer = "no"

        if 'CentralLocking' in request.POST:
            CentralLocking = request.POST['CentralLocking']
        else:
            CentralLocking = "no"

        if 'CrashSensor' in request.POST:
            CrashSensor = request.POST['CrashSensor']
        else:
            CrashSensor = "no"

        if 'LeatherSeats' in request.POST:
            LeatherSeats = request.POST['LeatherSeats']
        else:
            LeatherSeats = "no"

        vehicle.VehiclesBrand = brandsid
        vehicle.VehiclesTitle = VehiclesTitle
        vehicle.VehiclesOverview = VehiclesOverview
        vehicle.PricePerDay = PricePerDay
        vehicle.FuelType = FuelType
        vehicle.ModelYear = ModelYear
        vehicle.SeatingCapacity = SeatingCapacity

        vehicle.AirConditioner = AirConditioner
        vehicle.PowerDoorLocks = PowerDoorLocks
        vehicle.AntiLockBrakingSystem = AntiLockBrakingSystem
        vehicle.BrakeAssist = BrakeAssist
        vehicle.PowerSteering = PowerSteering
        vehicle.DriverAirbag = DriverAirbag
        vehicle.PassengerAirbag = PassengerAirbag
        vehicle.PowerWindows = PowerWindows
        vehicle.CDPlayer = CDPlayer
        vehicle.CentralLocking = CentralLocking
        vehicle.CrashSensor = CrashSensor
        vehicle.LeatherSeats = LeatherSeats

        try:
            vehicle.save()
            error = "no"
        except:
            error = "yes"

        try:
            Vimage1 = request.FILES['Vimage1']
            vehicle.Vimage1 = Vimage1
            vehicle.save()
        except:
            pass

        try:
            Vimage2 = request.FILES['Vimage2']
            vehicle.Vimage2 = Vimage2
            vehicle.save()
        except:
            pass

        try:
            Vimage3 = request.FILES['Vimage3']
            vehicle.Vimage3 = Vimage3
            vehicle.save()
        except:
            pass

        try:
            Vimage4 = request.FILES['Vimage4']
            vehicle.Vimage4 = Vimage4
            vehicle.save()
        except:
            pass

        try:
            Vimage5 = request.FILES['Vimage5']
            vehicle.Vimage5 = Vimage5
            vehicle.save()
        except:
            pass
    return render(request, 'admin/editVehicle.html', locals())


def deleteVehicle(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    vehicle = Vehicles.objects.get(id=pid)
    vehicle.delete()
    return redirect('vehicles')


def newBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    booking = Booking.objects.filter(Status__isnull=True)
    return render(request, 'admin/newBooking.html', locals())


def confirmBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    auto_complete_expired_bookings()
    booking = Booking.objects.filter(Status='Confirm').order_by('-id')
    return render(request, 'admin/confirmBooking.html', locals())


def completedBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    auto_complete_expired_bookings()
    booking = Booking.objects.filter(Status='Completed').order_by('-id')
    return render(request, 'admin/completedBooking.html', locals())


def releaseBooking(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    try:
        b = Booking.objects.get(id=pid)
        b.Status = 'Completed'
        b.LastUpdationDate = date.today()
        b.save()
    except Booking.DoesNotExist:
        pass
    next_page = request.GET.get('next', '')
    if next_page == 'allBooking':
        return redirect('allBooking')
    elif next_page == 'confirmBooking':
        return redirect('confirmBooking')
    return redirect('viewBooking', pid=pid)


def cancelBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    booking = Booking.objects.filter(Status='Cancel').order_by('-id')
    return render(request, 'admin/cancelBooking.html', locals())


def allBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    auto_complete_expired_bookings()
    booking = Booking.objects.all().order_by('-id')
    return render(request, 'admin/allBooking.html', locals())


def viewBooking(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    auto_complete_expired_bookings()
    bookingDtls = Booking.objects.get(id=pid)
    fd = bookingDtls.FromDate
    td = bookingDtls.ToDate
    totaldays = (td - fd).days if (td and fd) else 1
    if totaldays <= 0:
        totaldays = 1
    grandtotal = int(bookingDtls.VehicleId.PricePerDay) * int(totaldays)
    error = ""
    if request.method == "POST":
        Status = request.POST['Status']

        bookingDtls.Status = Status
        bookingDtls.LastUpdationDate = date.today()

        try:
            bookingDtls.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/viewBooking.html', locals())


def deleteBooking(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    booking = Booking.objects.get(id=pid)
    booking.delete()
    return redirect('allBooking')


def unreadQuery(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contact = Contactusquery.objects.filter(Status__isnull=True)
    return render(request, 'admin/unreadQuery.html', locals())


def readQuery(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contact = Contactusquery.objects.filter(Status='yes')
    return render(request, 'admin/readQuery.html', locals())


def viewQuery(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contacts = Contactusquery.objects.get(id=pid)
    contacts.Status = "yes"
    contacts.save()
    return render(request, 'admin/viewQuery.html', locals())


def deleteQuery(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    contacts = Contactusquery.objects.get(id=pid)
    contacts.delete()
    return redirect('readQuery')


def regUser(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    userDtls = UserDetails.objects.all()
    return render(request, 'admin/regUser.html', locals())

def search(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    if request.method=='POST':
        sd = request.POST['searchdata']
    try:
        booking = Booking.objects.filter(Q(BookingNumber=sd))
    except:
        booking = ""
    return render(request, 'admin/search.html', locals())

def betweendateReport(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    if request.method == 'POST':
        fd = request.POST['fromDate']
        td = request.POST['toDate']

        booking = Booking.objects.filter(Q(PostingDate__gte=fd) & Q(PostingDate__lte=td))
        return render(request, 'admin/betweendateReportDtls.html', locals())
    return render(request, 'admin/betweendateReport.html', locals())


def deleteUser(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    User.objects.get(id=pid).delete()
    return redirect('regUser')


def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'admin/changePassword.html', locals())


def Logout(request):
    logout(request)
    return redirect('index')


def userindex(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    vehicle = Vehicles.objects.all()
    return render(request, 'user/userindex.html', locals())


def vehicleDetails(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    vehicle = Vehicles.objects.get(id=pid)
    vehicleid = vehicle.id
    vehiclebrand = vehicle.VehiclesBrand
    similarvehicle = Vehicles.objects.exclude(id=vehicleid).order_by(
        Case(
            When(VehiclesBrand=vehiclebrand, then=0),
            default=1
        ),
        '-id'
    )
    if not similarvehicle.exists():
        similarvehicle = Vehicles.objects.all()

    users = User.objects.get(id=request.user.id)
    userdtls = UserDetails.objects.filter(user=users).first()
    if not userdtls:
        userdtls = UserDetails.objects.create(user=users, ContactNo="")

    auto_complete_expired_bookings()
    today = date.today().strftime('%Y-%m-%d')
    today_date = date.today()

    existing_bookings = Booking.objects.filter(
        VehicleId=vehicle,
        ToDate__gte=today_date
    ).exclude(Status__in=['Cancel', 'Completed']).order_by('FromDate')

    booked_ranges = []
    for b in existing_bookings:
        if b.FromDate and b.ToDate:
            booked_ranges.append({
                'from': b.FromDate.strftime('%Y-%m-%d'),
                'to': b.ToDate.strftime('%Y-%m-%d'),
                'from_display': b.FromDate.strftime('%d-%m-%Y'),
                'to_display': b.ToDate.strftime('%d-%m-%Y')
            })
    booked_ranges_json = json.dumps(booked_ranges)

    error = ""
    conflict_info = ""

    if request.method == "POST":
        FromDate_str = request.POST.get('FromDate')
        ToDate_str = request.POST.get('ToDate')
        message = request.POST.get('message', '')

        try:
            req_from = dt.strptime(FromDate_str, '%Y-%m-%d').date()
            req_to = dt.strptime(ToDate_str, '%Y-%m-%d').date()

            if req_to < req_from:
                error = "invalid_dates"
            elif req_from < today_date:
                error = "past_date"
            else:
                conflicts = Booking.objects.filter(
                    VehicleId=vehicle,
                    FromDate__lte=req_to,
                    ToDate__gte=req_from
                ).exclude(Status__in=['Cancel', 'Completed'])

                if conflicts.exists():
                    error = "already_booked"
                    c = conflicts.first()
                    conflict_info = f"{c.FromDate.strftime('%d-%m-%Y')} to {c.ToDate.strftime('%d-%m-%Y')}"
                else:
                    bookingNo = str(random.randint(10000000, 99999999))
                    diff_days = (req_to - req_from).days
                    totaldays = max(1, diff_days)
                    grandtotal = int(vehicle.PricePerDay) * int(totaldays)
                    new_booking = Booking.objects.create(
                        user=userdtls,
                        VehicleId=vehicle,
                        FromDate=req_from,
                        ToDate=req_to,
                        message=message,
                        BookingNumber=bookingNo,
                        TotalAmount=str(grandtotal),
                        PaymentStatus="Pending"
                    )
                    booking_id = new_booking.id
                    error = "no"
                    existing_bookings = Booking.objects.filter(
                        VehicleId=vehicle,
                        ToDate__gte=today_date
                    ).exclude(Status__in=['Cancel', 'Completed']).order_by('FromDate')
                    booked_ranges = []
                    for b in existing_bookings:
                        if b.FromDate and b.ToDate:
                            booked_ranges.append({
                                'from': b.FromDate.strftime('%Y-%m-%d'),
                                'to': b.ToDate.strftime('%Y-%m-%d'),
                                'from_display': b.FromDate.strftime('%d-%m-%Y'),
                                'to_display': b.ToDate.strftime('%d-%m-%Y')
                            })
                    booked_ranges_json = json.dumps(booked_ranges)
        except Exception:
            error = "yes"
    return render(request, 'user/vehicleDetails.html', locals())


def userabout(request):
    return render(request, 'user/userabout.html')


def usercarlist(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    vehicles = Vehicles.objects.all()
    brand = Brands.objects.all()
    if request.method == "POST":
        brandid = request.POST['brand']
        fuelType = request.POST['fuelType']

        brands = Brands.objects.get(id=brandid)
        vehicles = Vehicles.objects.filter(Q(FuelType=fuelType) & Q(VehiclesBrand=brands))
        vehiclescount = Vehicles.objects.filter(Q(FuelType=fuelType) & Q(VehiclesBrand=brands)).count()
        return render(request, 'user/searchCarList.html', locals())
    return render(request, 'user/usercarlist.html', locals())


def myProfile(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    user = User.objects.get(id=request.user.id)
    userDtls = UserDetails.objects.get(user=user)

    if request.method == "POST":
        fname = request.POST['firstName']
        lname = request.POST['lastName']
        ContactNo = request.POST['ContactNo']
        dob = request.POST['dob']
        Country = request.POST['Country']
        City = request.POST['City']
        Address = request.POST['Address']

        userDtls.user.first_name = fname
        userDtls.user.last_name = lname
        userDtls.ContactNo = ContactNo
        userDtls.dob = dob
        userDtls.Country = Country
        userDtls.City = City
        userDtls.Address = Address

        try:
            userDtls.save()
            userDtls.user.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'user/myProfile.html', locals())


def myBooking(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    auto_complete_expired_bookings()
    user = User.objects.get(id=request.user.id)
    userDtls = UserDetails.objects.get(user=user)
    booking = Booking.objects.filter(user=userDtls).order_by('-id')
    return render(request, 'user/myBooking.html', locals())


def mybookingDtls(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    booking = Booking.objects.get(id=pid)
    fd = booking.FromDate
    td = booking.ToDate
    totaldays = (td - fd).days if (td and fd) else 1
    if totaldays <= 0:
        totaldays = 1
    grandtotal = int(booking.VehicleId.PricePerDay) * int(totaldays)
    return render(request, 'user/mybookingDtls.html', locals())


def mychangePassword(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'user/mychangePassword.html', locals())


def bookingPayment(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    try:
        booking = Booking.objects.get(id=pid)
    except Booking.DoesNotExist:
        return redirect('myBooking')

    vehicle = booking.VehicleId
    fd = booking.FromDate
    td = booking.ToDate
    diff_days = (td - fd).days if (td and fd) else 1
    totaldays = max(1, diff_days)
    grandtotal = int(vehicle.PricePerDay) * int(totaldays)

    if not booking.TotalAmount:
        booking.TotalAmount = str(grandtotal)
        booking.save()

    error = ""
    if request.method == "POST":
        payment_mode = request.POST.get('payment_mode', 'UPI')
        if payment_mode == "Pay on Pickup":
            booking.PaymentStatus = "Pay on Pickup"
            booking.PaymentMode = "Pay on Pickup (Cash / Card)"
            booking.TransactionId = "POP" + str(random.randint(10000000, 99999999))
            booking.Status = "Confirm"
        else:
            prefix = "UPI" if "UPI" in payment_mode else ("CARD" if "Card" in payment_mode else "NB")
            booking.PaymentStatus = "Paid"
            booking.PaymentMode = payment_mode
            booking.TransactionId = prefix + str(random.randint(1000000000, 9999999999))
            booking.Status = "Confirm"

        booking.TotalAmount = str(grandtotal)
        booking.LastUpdationDate = date.today()
        booking.save()
        return redirect('bookingInvoice', pid=booking.id)

    return render(request, 'user/bookingPayment.html', locals())


def bookingInvoice(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    try:
        booking = Booking.objects.get(id=pid)
    except Booking.DoesNotExist:
        return redirect('myBooking')

    vehicle = booking.VehicleId
    fd = booking.FromDate
    td = booking.ToDate
    diff_days = (td - fd).days if (td and fd) else 1
    totaldays = max(1, diff_days)
    grandtotal = int(vehicle.PricePerDay) * int(totaldays)

    return render(request, 'user/bookingInvoice.html', locals())


def downloadInvoicePDF(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    try:
        booking = Booking.objects.get(id=pid)
    except Booking.DoesNotExist:
        return redirect('myBooking')

    # Security check: User must own the booking or be admin/staff
    if not request.user.is_staff and booking.user and booking.user.user != request.user:
        return redirect('myBooking')

    vehicle = booking.VehicleId
    user = booking.user.user if (booking.user and booking.user.user) else None
    userdtls = booking.user

    fd = booking.FromDate
    td = booking.ToDate
    diff_days = (td - fd).days if (td and fd) else 1
    totaldays = max(1, diff_days)
    daily_price = int(vehicle.PricePerDay) if (vehicle and vehicle.PricePerDay) else 0
    grandtotal = daily_price * totaldays

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm
    )

    elements = []
    styles = getSampleStyleSheet()

    c_orange = colors.HexColor('#f77d0a')
    c_dark = colors.HexColor('#2b2e4a')
    c_gray = colors.HexColor('#6c757d')
    c_border = colors.HexColor('#dee2e6')

    s_title = ParagraphStyle('LogoTitle', fontName='Helvetica-Bold', fontSize=22, leading=26)
    s_subtitle = ParagraphStyle('Sub', fontName='Helvetica', fontSize=8, leading=11, textColor=c_gray)
    s_inv_no = ParagraphStyle('InvNo', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=c_dark, alignment=2)
    s_date = ParagraphStyle('InvDate', fontName='Helvetica', fontSize=8, leading=11, textColor=c_gray, alignment=2)
    s_section_hdr = ParagraphStyle('SecHdr', fontName='Helvetica-Bold', fontSize=9, textColor=c_gray, spaceAfter=4)
    s_bold_dark = ParagraphStyle('BoldDark', fontName='Helvetica-Bold', fontSize=12, textColor=c_dark)
    s_body = ParagraphStyle('BodyText', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#333333'))
    s_body_right = ParagraphStyle('BodyRight', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#333333'), alignment=2)

    s_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=c_dark)
    s_th_center = ParagraphStyle('THC', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=c_dark, alignment=1)
    s_th_right = ParagraphStyle('THR', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=c_dark, alignment=2)
    s_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#333333'))
    s_td_bold = ParagraphStyle('TDBold', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_dark)
    s_td_center = ParagraphStyle('TDC', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#333333'), alignment=1)
    s_td_right = ParagraphStyle('TDR', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#333333'), alignment=2)
    s_td_right_bold = ParagraphStyle('TDRB', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_dark, alignment=2)
    s_td_grand = ParagraphStyle('TDRG', fontName='Helvetica-Bold', fontSize=13, leading=15, textColor=c_orange, alignment=2)

    # Header
    logo_p = Paragraph('<font color="#f77d0a"><b>Ride</b></font><font color="#2b2e4a"><b>OnRent</b></font>', s_title)
    sub_p = Paragraph('Car Rental Portal Management System<br/>Support: support@rideonrent.com | +91 98765 43210', s_subtitle)
    left_header = [logo_p, Spacer(1, 2 * mm), sub_p]

    posting_str = booking.PostingDate.strftime('%d %b %Y, %I:%M %p') if booking.PostingDate else ''
    badge_html = '<font color="#f77d0a"><b>TAX INVOICE</b></font>'
    inv_no_p = Paragraph(f'Invoice No: INV-{booking.BookingNumber}', s_inv_no)
    date_p = Paragraph(f'Date: {posting_str}', s_date)
    right_header = [Paragraph(badge_html, s_inv_no), Spacer(1, 1 * mm), inv_no_p, date_p]

    header_table = Table([[left_header, right_header]], colWidths=[100 * mm, 82 * mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width='100%', thickness=1, color=c_border, spaceAfter=8, spaceBefore=4))

    # Customer & Payment Summary
    cust_name = f'{user.first_name} {user.last_name}'.strip() if user else 'Registered Customer'
    cust_email = user.username if user else 'N/A'
    cust_phone = userdtls.ContactNo if userdtls and userdtls.ContactNo and userdtls.ContactNo != 'None' else 'Not Provided'
    addr_parts = []
    if userdtls:
        if userdtls.Address and userdtls.Address != 'None': addr_parts.append(userdtls.Address)
        if userdtls.City and userdtls.City != 'None': addr_parts.append(userdtls.City)
        if userdtls.Country and userdtls.Country != 'None': addr_parts.append(userdtls.Country)
    cust_address = ', '.join(addr_parts) if addr_parts else 'Registered Member'

    cust_info = [
        Paragraph('CUSTOMER DETAILS:', s_section_hdr),
        Paragraph(cust_name, s_bold_dark),
        Spacer(1, 1 * mm),
        Paragraph(f'Email: {cust_email}', s_body),
        Paragraph(f'Phone: {cust_phone}', s_body),
        Paragraph(f'Address: {cust_address}', s_body),
    ]

    pay_status = booking.PaymentStatus or 'Pending'
    status_color = '#198754' if pay_status == 'Paid' else ('#0d6efd' if pay_status == 'Pay on Pickup' else '#ffc107')
    pay_mode = booking.PaymentMode or 'Online'
    txn_id = booking.TransactionId or 'N/A'
    book_status = booking.Status or 'Confirmed'

    pay_info = [
        Paragraph('PAYMENT SUMMARY:', s_section_hdr),
        Paragraph(f'Payment Status: <font color="{status_color}"><b>{pay_status.upper()}</b></font>', s_body_right),
        Paragraph(f'Payment Mode: <b>{pay_mode}</b>', s_body_right),
        Paragraph(f'Transaction ID: <b>{txn_id}</b>', s_body_right),
        Paragraph(f'Booking Status: <b>{book_status}</b>', s_body_right),
    ]

    info_table = Table([[cust_info, pay_info]], colWidths=[96 * mm, 86 * mm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4 * mm))

    # Vehicle Table
    v_title = vehicle.VehiclesTitle if vehicle else 'Rental Vehicle'
    v_brand = vehicle.VehiclesBrand.BrandName if vehicle and vehicle.VehiclesBrand else ''
    v_year = vehicle.ModelYear if vehicle else ''
    v_fuel = vehicle.FuelType if vehicle else ''
    desc_html = f'<b>{v_title}</b><br/><font size="7.5" color="#6c757d">Brand: {v_brand} | Year: {v_year} | Fuel: {v_fuel}<br/>Booking No: #{booking.BookingNumber}</font>'

    from_str = fd.strftime('%d %b %Y') if fd else ''
    to_str = td.strftime('%d %b %Y') if td else ''
    period_html = f'{from_str} to<br/>{to_str}'

    table_data = [
        [
            Paragraph('#', s_th),
            Paragraph('Vehicle Description', s_th),
            Paragraph('Rental Period', s_th_center),
            Paragraph('Duration', s_th_center),
            Paragraph('Rate / Day', s_th_right),
            Paragraph('Total', s_th_right)
        ],
        [
            Paragraph('1', s_td),
            Paragraph(desc_html, s_td),
            Paragraph(period_html, s_td_center),
            Paragraph(f'<b>{totaldays} Day{"s" if totaldays > 1 else ""}</b>', s_td_center),
            Paragraph(f'Rs. {daily_price}', s_td_right),
            Paragraph(f'<b>Rs. {grandtotal}</b>', s_td_right_bold)
        ],
        [
            '', '', '', '',
            Paragraph('Subtotal:', s_td_right_bold),
            Paragraph(f'<b>Rs. {grandtotal}</b>', s_td_right_bold)
        ],
        [
            '', '', '', '',
            Paragraph('Taxes & GST:', s_td_right_bold),
            Paragraph('<font color="#198754"><b>Included</b></font>', s_td_right_bold)
        ],
        [
            '', '', '', '',
            Paragraph('<b>Grand Total:</b>', ParagraphStyle('GT', fontName='Helvetica-Bold', fontSize=10, textColor=c_dark, alignment=2)),
            Paragraph(f'<b>Rs. {grandtotal}</b>', s_td_grand)
        ]
    ]

    col_widths = [10 * mm, 68 * mm, 36 * mm, 22 * mm, 22 * mm, 24 * mm]
    booking_table = Table(table_data, colWidths=col_widths)
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f5')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 1), 0.5, c_border),
        ('GRID', (4, 2), (-1, -1), 0.5, c_border),
        ('BACKGROUND', (4, -1), (-1, -1), colors.HexColor('#fff8e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 6 * mm))

    # Terms
    terms_html = '<b>Rental Instructions & Terms:</b><br/>' \
                 '• Please carry your original valid Driving License and Govt ID during vehicle pick-up.<br/>' \
                 f'• Vehicle return scheduled on or before: <b>{to_str}</b>.<br/>' \
                 '• 24/7 Roadside Assistance: <b>1800-123-RENT</b> | support@rideonrent.com'
    terms_table = Table([[Paragraph(terms_html, s_body)]], colWidths=[182 * mm])
    terms_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(terms_table)
    elements.append(Spacer(1, 6 * mm))

    # Signatures
    sig_data = [
        [
            Paragraph('<font size="7.5" color="#6c757d">Computer-generated tax invoice. No signature required.</font>', styles['Normal']),
            Paragraph('<b>Authorized Signatory</b><br/><font size="7.5" color="#6c757d">RideOnRent Car Rental Portal</font>', ParagraphStyle('Sig', fontName='Helvetica', fontSize=8, alignment=2))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[110 * mm, 72 * mm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="RideOnRent_Invoice_{booking.BookingNumber}.pdf"'
    return response
