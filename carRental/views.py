import datetime
import random

from django.contrib.auth import authenticate, logout, login
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from datetime import date


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


def carDetails(request, pid):
    vehicle = Vehicles.objects.get(id=pid)
    vehicleid = vehicle.id
    vehiclebrand = vehicle.VehiclesBrand
    similarvehicle = Vehicles.objects.filter(~Q(id=vehicleid), VehiclesBrand=vehiclebrand)
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
    if request.method == "POST":
        fname = request.POST['firstName']
        lname = request.POST['lastName']
        ContactNo = request.POST['ContactNo']
        dob = request.POST['dob']
        email = request.POST['emailid']
        password = request.POST['password']
        Country = request.POST['Country']
        City = request.POST['City']
        Address = request.POST['Address']

        try:
            user = User.objects.create_user(username=email, password=password, first_name=fname, last_name=lname)
            UserDetails.objects.create(user=user, ContactNo=ContactNo, dob=dob, Country=Country, City=City,
                                       Address=Address)
            error = "no"
        except:
            error = "yes"
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
    booking = Booking.objects.filter(Status='Confirm')
    return render(request, 'admin/confirmBooking.html', locals())


def cancelBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    booking = Booking.objects.filter(Status='Cancel')
    return render(request, 'admin/cancelBooking.html', locals())


def allBooking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    booking = Booking.objects.all()
    return render(request, 'admin/allBooking.html', locals())


def viewBooking(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    bookingDtls = Booking.objects.get(id=pid)
    fd = bookingDtls.FromDate
    td = bookingDtls.ToDate
    totaldays = td - fd
    totaldays = str(totaldays)[0:1]
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
    similarvehicle = Vehicles.objects.filter(~Q(id=vehicleid), VehiclesBrand=vehiclebrand)

    users = User.objects.get(id=request.user.id)
    userdtls = UserDetails.objects.get(user=users)
    if request.method == "POST":
        FromDate = request.POST['FromDate']
        ToDate = request.POST['ToDate']
        message = request.POST['message']
        bookingNo = str(random.randint(10000000, 99999999))
        try:
            Booking.objects.create(user=userdtls, VehicleId=vehicle, FromDate=FromDate, ToDate=ToDate, message=message,
                                   BookingNumber=bookingNo)
            error = "no"
        except:
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
    user = User.objects.get(id=request.user.id)
    userDtls = UserDetails.objects.get(user=user)
    booking = Booking.objects.filter(user=userDtls)
    return render(request, 'user/myBooking.html', locals())


def mybookingDtls(request, pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    booking = Booking.objects.get(id=pid)
    fd = booking.FromDate
    td = booking.ToDate
    totaldays = td - fd
    totaldays = str(totaldays)[0:1]
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
