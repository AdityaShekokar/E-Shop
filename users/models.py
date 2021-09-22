# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

from e_shop.common import CreateUpdateDate, SafeDeleteModel, UniqueIds


class User(AbstractUser, SafeDeleteModel, UniqueIds):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = "user"


class Roles(CreateUpdateDate, UniqueIds, SafeDeleteModel):
    name = models.CharField(max_length=20, unique=True)
    user = models.ManyToManyField(User, db_table="user_and_roles", related_name="user_roles")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "roles"


class Scopes(CreateUpdateDate, UniqueIds, SafeDeleteModel):
    name = models.CharField(max_length=20, unique=True)
    roles = models.ManyToManyField(Roles, db_table="scopes_and_roles", related_name="role_scopes")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "scopes"
