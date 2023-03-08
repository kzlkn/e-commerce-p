from datetime import datetime, date
from django.contrib.auth.models import User
from django.db import models


# --- Helper functions ---
# Users should be able to create an Account when they are at least 16 years old
# Default-Date is the youngest acceptable age
def get_youngest_acceptable_age():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return date(year - 16, month, day)


def get_extended_user_from_user(user):
    """
    :param user: Instance from User class
    :return: Corresponding ExtendedUser instance, or None if the
    instance does not exist
    """
    extended_user = None
    extended_user_query_set = ExtendedUser.objects.filter(user=user)
    if len(extended_user_query_set) > 0:
        extended_user = extended_user_query_set.first()
    return extended_user


# Create your models here.
class ExtendedUser(models.Model):
    GENDERS = [
        ("M", "Male"),
        ("F", "Female"),
        ("NB", "Non-Binary")]

    # Default User Model is connected to this class via OneToOneField
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="extended_user")
    date_of_birth = models.DateField(default=get_youngest_acceptable_age())  # Default is 16 years old
    profile_picture = models.ImageField(upload_to='profile-pictures/', blank=True, null=True)
    gender = models.CharField(max_length=30, choices=GENDERS)
    street = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.IntegerField(blank=True, null=True)
    plz = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.IntegerField(blank=True, null=True)

    def get_address_of_user(self):
        return f'{self.street} {self.house_number}, {self.plz} {self.city}'

    def get_full_name_of_user(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def execute_after_login(self):
        self.save()

    def __str__(self):
        return f'{self.get_full_name_of_user()} | {self.user.email}'

    def __repr__(self):
        return repr(self)
