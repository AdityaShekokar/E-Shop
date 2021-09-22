# reference https://djangosnippets.org/snippets/2513/

import uuid
import warnings
from http import HTTPStatus

from django.core.exceptions import ImproperlyConfigured
from django.db import models, router
from django_mysql.models import Bit1BooleanField
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from safedelete.config import HARD_DELETE, HARD_DELETE_NOCASCADE, NO_DELETE, SOFT_DELETE
from safedelete.managers import (
    SafeDeleteAllManager,
    SafeDeleteDeletedManager,
    SafeDeleteManager,
)
from safedelete.models import SOFT_DELETE_CASCADE
from safedelete.signals import post_softdelete, post_undelete, pre_softdelete
from safedelete.utils import can_hard_delete, related_objects

from e_shop.settings import HARD_DELETE_CASCADE


class CreateUpdateDate(models.Model):
    class Meta:
        abstract = True

    # Save date and time of add and update.
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)


class PublicId:
    @staticmethod
    def create_public_id():
        public_id = uuid.uuid4().int >> 75
        return public_id


class UniqueIds(models.Model):
    class Meta:
        abstract = True

    # primary key with big integer, auto incremented,
    # sequential number, used internally for logic and data management.
    id = models.BigAutoField(primary_key=True, unique=True)

    #  public id to share with the url,
    #  Used for REST routes and public displays
    public_id = models.BigIntegerField(editable=False, unique=True)


def is_safedelete_cls(cls):
    for base in cls.__bases__:

        # This used to check if it startswith 'safedelete', but that masks
        # the issue inside of a test. Other clients create models that are
        # outside of the safedelete package.
        if base.__module__.startswith("db.base_models"):
            return True
        if is_safedelete_cls(base):
            return True
    return False


def is_safedelete(related):
    warnings.warn(
        "is_safedelete is deprecated in favor of is_safedelete_cls", DeprecationWarning
    )
    return is_safedelete_cls(related.__class__)


class SafeDeleteModel(models.Model):
    """Abstract safedelete-ready model.

    .. note::
        To create your safedelete-ready models, you have to make them inherit from this model.

    :attribute deleted:
        DateTimeField set to the moment the object was deleted. Is set to
        ``None`` if the object has not been deleted.

    :attribute _safedelete_policy: define what happens when you delete an object.
        It can be one of ``HARD_DELETE``, ``SOFT_DELETE``, ``SOFT_DELETE_CASCADE``, ``NO_DELETE`` and ``HARD_DELETE_NOCASCADE``.
        Defaults to ``SOFT_DELETE``.

        >>> class MyModel(SafeDeleteModel):
        ...     _safedelete_policy = SOFT_DELETE
        ...     my_field = models.TextField()
        ...
        >>> # Now you have your model (with its ``deleted`` field, and custom manager and delete method)

    :attribute objects:
        The :class:`safedelete.managers.SafeDeleteManager` that returns the non-deleted models.

    :attribute all_objects:
        The :class:`safedelete.managers.SafeDeleteAllManager` that returns the all models (non-deleted and soft-deleted).

    :attribute deleted_objects:
        The :class:`safedelete.managers.SafeDeleteDeletedManager` that returns the soft-deleted models.
    """

    _safedelete_policy = SOFT_DELETE

    deleted = Bit1BooleanField(default=0, null=True)

    objects = SafeDeleteManager()
    all_objects = SafeDeleteAllManager()
    deleted_objects = SafeDeleteDeletedManager()

    class Meta:
        abstract = True

    def save(self, keep_deleted=False, **kwargs):
        """Save an object, un-deleting it if it was deleted.

        Args:
            keep_deleted: Do not undelete the model if soft-deleted. (default: {False})
            kwargs: Passed onto :func:`save`.

        .. note::
            Undeletes soft-deleted models by default.
        """

        # undelete signal has to happen here (and not in undelete)
        # in service_order to catch the case where a deleted model becomes
        # implicitly undeleted on-save.  If someone manually nulls out
        # deleted, it'll bypass this logic, which I think is fine, because
        # otherwise we'd have to shadow field changes to handle that case.

        was_undeleted = False
        if not keep_deleted:
            if self.deleted and self.pk:
                was_undeleted = True
            self.deleted = None

        super(SafeDeleteModel, self).save(**kwargs)

        if was_undeleted:
            # send undelete signal
            using = kwargs.get("using") or router.db_for_write(
                self.__class__, instance=self
            )
            post_undelete.send(sender=self.__class__, instance=self, using=using)

    def undelete(self, force_policy=None, **kwargs):
        """Undelete a soft-deleted model.

        Args:
            force_policy: Force a specific undelete policy. (default: {None})
            kwargs: Passed onto :func:`save`.

        .. note::
            Will raise a :class:`AssertionError` if the model was not soft-deleted.
        """
        current_policy = force_policy or self._safedelete_policy

        assert self.deleted
        self.save(keep_deleted=False, **kwargs)

        if current_policy == SOFT_DELETE_CASCADE:

            for related in related_objects(self):
                if is_safedelete_cls(related.__class__) and related.deleted:
                    related.undelete()

    def delete(self, force_policy=None, **kwargs):
        """Overrides Django's delete behaviour based on the model's delete policy.

        Args:
            force_policy: Force a specific delete policy. (default: {None})
            kwargs: Passed onto :func:`save` if soft deleted.
        """

        current_policy = (
            self._safedelete_policy if (force_policy is None) else force_policy
        )
        if current_policy == SOFT_DELETE:

            # Only soft-delete the object, marking it as deleted.
            soft_delete_policy(self)
        elif current_policy == HARD_DELETE:

            # Normally hard-delete the object.
            super(SafeDeleteModel, self).delete()

        elif current_policy == HARD_DELETE_NOCASCADE:

            # Hard-delete the object only if nothing would be deleted with it
            hard_delete_no_cascade_policy(self)
        elif current_policy == SOFT_DELETE_CASCADE:

            # Soft-delete on related objects before

            for related in related_objects(self):
                if is_safedelete_cls(related.__class__) and not related.deleted:
                    related.delete(force_policy=SOFT_DELETE, **kwargs)
            # soft-delete the object
            self.delete(force_policy=SOFT_DELETE, **kwargs)
        elif current_policy == HARD_DELETE_CASCADE:

            # Hard-delete on related objects before
            hard_delete_cascade_policy(self)

    @classmethod
    def has_unique_fields(cls):
        """Checks if one of the fields of this model has a unique constraint set (unique=True)

        Args:
            model: Model instance to check
        """
        for field in cls._meta.fields:
            if field._unique:
                return True
        return False

    # We need to overwrite this check to ensure uniqueness is also checked
    # against "deleted" (but still in db) objects.
    # FIXME: Better/cleaner way ?
    def _perform_unique_checks(self, unique_checks):
        errors = {}

        for model_class, unique_check in unique_checks:
            lookup_kwargs = ensure_uniqueness(self, unique_check)
            if len(unique_check) != len(lookup_kwargs):
                continue

            # This is the changed line
            if hasattr(model_class, "all_objects"):
                qs = model_class.all_objects.filter(**lookup_kwargs)
            else:
                qs = model_class._default_manager.filter(**lookup_kwargs)

            model_class_pk = self._get_pk_val(model_class._meta)
            if not self._state.adding and model_class_pk is not None:
                qs = qs.exclude(pk=model_class_pk)
            if qs.exists():
                if len(unique_check) == 1:
                    key = unique_check[0]
                else:
                    key = models.base.NON_FIELD_ERRORS
                errors.setdefault(key, []).append(
                    self.unique_error_message(model_class, unique_check)
                )
        return errors


def soft_delete_policy(instance, **kwargs):
    instance.deleted = 1
    using = kwargs.get("using") or router.db_for_write(
        instance.__class__, instance=instance
    )
    # send pre_softdelete signal
    pre_softdelete.send(sender=instance.__class__, instance=instance, using=using)
    super(SafeDeleteModel, instance).save(**kwargs)
    # send softdelete signal
    post_softdelete.send(sender=instance.__class__, instance=instance, using=using)


def hard_delete_no_cascade_policy(instance, **kwargs):
    if not can_hard_delete(instance):
        instance.delete(force_policy=SOFT_DELETE, **kwargs)
    else:
        instance.delete(force_policy=HARD_DELETE, **kwargs)


def hard_delete_cascade_policy(instance, **kwargs):
    for related in related_objects(instance):
        if is_safedelete_cls(related.__class__) and not related.deleted:
            related.delete(force_policy=HARD_DELETE, **kwargs)
    # hard-delete the object
    instance.delete(force_policy=HARD_DELETE, **kwargs)


def ensure_uniqueness(instance, unique_check):
    lookup_kwargs = {}
    for field_name in unique_check:
        f = instance._meta.get_field(field_name)
        lookup_value = getattr(instance, f.attname)
        if lookup_value is None:
            continue
        if f.primary_key and not instance._state.adding:
            continue
        lookup_kwargs[str(field_name)] = lookup_value
    return lookup_kwargs


class SafeDeleteMixin(SafeDeleteModel):
    """``SafeDeleteModel`` was previously named ``SafeDeleteMixin``.

    .. deprecated:: 0.4.0
        Use :class:`SafeDeleteModel` instead.
    """

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The SafeDeleteMixin class was renamed SafeDeleteModel", DeprecationWarning
        )
        SafeDeleteModel.__init__(self, *args, **kwargs)


def validate_url_value(public_id, key_name):
    """
    This function is used to validate the public ids of URL.

    :param public_id:  This public id is related to the request URL.
    :type public_id: int
    :param key_name: This key name is related to quality control constant.
    :type key_name: str.
    :return: return the Json response.
    :raises ValueError: If the value is not valid.
    :rtype: dict
    """
    try:
        if public_id is not None:
            int(public_id)
            if public_id == "0":
                raise ValidationError(
                    {key_name: "PUBLIC ID CAN NOT BE ZERO"},
                    HTTPStatus.BAD_REQUEST
                )
            elif len(str(public_id)) > 17:
                raise ValidationError(
                    {key_name: "PUBLIC Id IS BEYOND THE ALLOW LIMIT"},
                    HTTPStatus.BAD_REQUEST,
                )
    except ValueError:
        raise ValidationError(
            {key_name: "VALID INT IS REQUIRED"},
            HTTPStatus.BAD_REQUEST,
        )


class CustomPermissions(BasePermission):
    """
    :attr:alternate_required_scopes: dict keyed by HTTP method name with value: iterable alternate scope lists

    This fulfills the [Open API Specification (OAS; formerly Swagger)](https://www.openapis.org/)
    list of alternative Security Requirements Objects for oauth2 or openIdConnect:
      When a list of Security Requirement Objects is defined on the Open API object or Operation Object,
      only one of Security Requirement Objects in the list needs to be satisfied to authorize the request.
    [1](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#securityRequirementObject)

    For each method, a list of lists of allowed scopes is tried in order and the first to match succeeds.

    @example
    required_alternate_scopes = {
       'GET': [['read']],
       'POST': [['create1','scope2'], ['alt-scope3'], ['alt-scope4','alt-scope5']],
    }

    TODO: DRY: subclass TokenHasScope and iterate over values of required_scope?
    """

    def has_permission(self, request, view):
        required_alternate_scopes = getattr(view, "required_alternate_scopes")
        m = request.method.upper()
        if m in required_alternate_scopes:
            for alt in required_alternate_scopes[m]:
                user_scopes = list(
                    {scope.name for role in request.user.user_roles.all() for scope in role.role_scopes.all()})
                for alt_scope in alt:
                    flag = False
                    if alt_scope in user_scopes:
                        flag = True
            return flag
        else:
            return False
