from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Brands(models.Model):
    BrandName = models.CharField(max_length=100, null=True)
    Creationdate = models.DateTimeField(auto_now_add=True)
    UpdationDate = models.DateField(null=True)

    def __str__(self):
        return self.BrandName

class Contactusinfo(models.Model):
    Address = models.CharField(max_length=250, null=True)
    EmailId = models.CharField(max_length=100, null=True)
    ContactNo = models.CharField(max_length=12, null=True)

    def __str__(self):
        return self.EmailId

class Contactusquery(models.Model):
    Name = models.CharField(max_length=250, null=True)
    EmailId = models.CharField(max_length=100, null=True)
    ContactNo = models.CharField(max_length=12, null=True)
    Message = models.CharField(max_length=250, null=True)
    PostingDate = models.DateTimeField(auto_now_add=True)
    Status = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.Name

class UserDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ContactNo = models.CharField(max_length=12, null=True)
    dob = models.DateField(null=True)
    Address = models.CharField(max_length=250, null=True)
    City = models.CharField(max_length=150, null=True)
    Country = models.CharField(max_length=100, null=True)
    RegDate = models.DateTimeField(auto_now_add=True)
    UpdationDate = models.DateField(null=True)

    def __str__(self):
        return self.user.first_name

class Vehicles(models.Model):
    VehiclesTitle = models.CharField(max_length=250, null=True)
    VehiclesBrand = models.ForeignKey(Brands, on_delete=models.CASCADE, null=True)
    VehiclesOverview = models.CharField(max_length=350, null=True)
    PricePerDay = models.CharField(max_length=200, null=True)
    FuelType = models.CharField(max_length=150, null=True)
    ModelYear = models.CharField(max_length=150, null=True)
    SeatingCapacity = models.CharField(max_length=150, null=True)
    Vimage1 = models.FileField(null=True,blank=True)
    Vimage2 = models.FileField(null=True,blank=True)
    Vimage3 = models.FileField(null=True,blank=True)
    Vimage4 = models.FileField(null=True,blank=True)
    Vimage5 = models.FileField(null=True,blank=True)
    AirConditioner = models.CharField(max_length=50, null=True)
    PowerDoorLocks = models.CharField(max_length=50, null=True)
    AntiLockBrakingSystem = models.CharField(max_length=50, null=True)
    BrakeAssist = models.CharField(max_length=50, null=True)
    PowerSteering = models.CharField(max_length=50, null=True)
    DriverAirbag = models.CharField(max_length=50, null=True)
    PassengerAirbag = models.CharField(max_length=50, null=True)
    PowerWindows = models.CharField(max_length=50, null=True)
    CDPlayer = models.CharField(max_length=50, null=True)
    CentralLocking = models.CharField(max_length=50, null=True)
    CrashSensor = models.CharField(max_length=50, null=True)
    LeatherSeats = models.CharField(max_length=50, null=True)
    RegDate = models.DateTimeField(auto_now_add=True)
    UpdationDate = models.DateField(null=True)

    def __str__(self):
        return self.VehiclesTitle

class Booking(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True)
    BookingNumber = models.CharField(max_length=150, null=True)
    VehicleId = models.ForeignKey(Vehicles, on_delete=models.CASCADE, null=True)
    FromDate = models.DateField(null=True)
    ToDate = models.DateField(null=True)
    message = models.CharField(max_length=350, null=True)
    Status = models.CharField(max_length=150, null=True)
    PostingDate = models.DateTimeField(auto_now_add=True)
    LastUpdationDate = models.DateField(null=True)

    def __str__(self):
        return self.BookingNumber