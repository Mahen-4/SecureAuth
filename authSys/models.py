from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class MemberManager(BaseUserManager):

    def create_user(self, email, password=None):

        if not email:
            raise ValueError("email address can't be empty")
        
        #email to lowercase 
        user = self.model(email=self.normalize_email(email))
        # Hash password
        user.set_password(password) 
        #save to database 
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True #set user to admin 
        user.save(using=self._db)
        return user
    
class Member(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=250)
    last_login = models.DateTimeField(null=True, blank=True)

    # use MemberManager instead of default manager 
    objects = MemberManager()

    USERNAME_FIELD = 'email' #use email as principal instead of username

    #set last login datetime 
    def update_last_login(self):
        self.last_login = now()
        self.save(update_fields=["last_login"]) 