import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from django.db.models import JSONField


RECORD_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("REVOKED", "REVOKED")
]


class Agency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Agencies"

    def __str__(self):
        return str(self.name)


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(
        Agency,
        on_delete=models.CASCADE,
        related_name="agency_department",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Departments"

    def __str__(self):
        return str(self.name)


class UserCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user_mapping = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class UserGroup(models.Model):
    group = models.OneToOneField(
        "auth.Group", unique=True, on_delete=models.CASCADE,)
    user_category = models.ForeignKey(
        UserCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    user_department = models.ForeignKey(
        Department, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return "{}".format(self.group.name)


class UserCategoryType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        UserCategory,
        on_delete=models.CASCADE,
        related_name="user_category_type",
        blank=True,
        null=True,
    )
    model_name = models.CharField(max_length=100, null=True, blank=True)
    serializer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class User(AbstractBaseUser, PermissionsMixin):
    PUBLICUSER = "PUBLICUSER"
    PROFESSIONAL = "PROFESSIONAL"
    STAFF = "STAFF"
    USERTYPE = [
        (PUBLICUSER, "PUBLICUSER"),
        (STAFF, "STAFF"),
        (PROFESSIONAL, "PROFESSIONAL"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    usertype = models.ForeignKey(
        UserCategoryType, on_delete=models.CASCADE, blank=True, null=True
    )
    is_defaultpassword = models.BooleanField(default=False)
    profile_photo = models.CharField(max_length=255, null=True, blank=True)
    enable_phone_notification = models.BooleanField(null=True, blank=True)
    enable_email_notification = models.BooleanField(null=True, blank=True)
    enable_system_notification = models.BooleanField(default=True)
    primary_role = models.CharField(max_length=255, null=True, blank=True)
    date_registered = models.DateTimeField(auto_now=True)
    ACCOUNT_DEFAULT_STATUS = [
        ("ACTIVE", "ACTIVE"),
        ("IN_ACTIVE", "IN_ACTIVE"),
    ]
    account_status = models.CharField(
        max_length=255, choices=ACCOUNT_DEFAULT_STATUS, default='ACTIVE')

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = "systemusers"


VERIFICATION_LEVELS = [
    ("BUSINESS_REGISTRATION_SERVICE", "BUSINESS_REGISTRATION_SERVICE"),
    ("PHYSICAL_VERIFICATION", "PHYSICAL_VERIFICATION"),
    ("NRB_VERIFICATION", "NRB_VERIFICATION"),
]


class AccountVerificationLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="account_verification_level",
        blank=True,
        null=True,
    )
    verification_level = models.CharField(
        choices=VERIFICATION_LEVELS,
        max_length=1000, blank=True, null=True)
    verification_step = models.CharField(
        max_length=255, blank=True, null=True)
    date_verified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.verification_level)


class SecurityQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question)


SECURITY_ANSWER_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("REVOKED", "REVOKED"),
    ("RESET", "RESET"),
]


class AccountSecurityQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="account_user_questions"
    )
    security_question = models.ForeignKey(
        SecurityQuestions,
        on_delete=models.CASCADE,
        related_name="account_user_security_questions"
    )
    # hashed answer
    answer = models.TextField(blank=True, null=True)
    answer_status = models.CharField(
        choices=SECURITY_ANSWER_STATUS,
        max_length=1000, blank=True, null=True)

    def __str__(self):
        return str(self.answer)


class PublicUserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="public_user",
        blank=True,
        null=True,
    )
    email = models.EmailField(null=True, blank=True)
    phonenum = models.CharField(max_length=1000, blank=True, null=True)
    fullname = models.CharField(max_length=1000, blank=True, null=True)
    firstname = models.CharField(max_length=1000, blank=True, null=True)
    middlename = models.CharField(max_length=1000, blank=True, null=True)
    lastname = models.CharField(max_length=1000, blank=True, null=True)
    gender = models.CharField(max_length=1000, null=True, blank=True)
    mothermaiden = models.CharField(max_length=1000, blank=True, null=True)
    is_phoneverified = models.BooleanField(default=False)
    is_emailverified = models.BooleanField(default=False)
    is_passwordverified = models.BooleanField(default=False)
    date_registered = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.fullname)


class TeamCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


class TeamCategoryType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        TeamCategory,
        on_delete=models.CASCADE,
        related_name="user_category_type",
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.name)


class TeamAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    ACCOUNT_STATUS = [
        ("PENDING", "PENDING"),
        ("ACTIVE", "ACTIVE"),
        ("SUSPENDED", "SUSPENDED"),
        ("DEACTIVATED", "DEACTIVATED"),
    ]
    status = models.CharField(max_length=100, choices=ACCOUNT_STATUS)
    team_account_type = models.ForeignKey(
        TeamCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    date_created = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.name + "" + self.team_account_type.name)


class TeamAccountUsers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_account = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="team_user_account",
        null=True,
        blank=True,
    )
    team_account = models.ForeignKey(
        TeamAccount,
        on_delete=models.CASCADE,
        related_name="team_account",
        null=True,
        blank=True,
    )
    date_created = models.DateTimeField(null=True, blank=True)
    is_team_admin = models.BooleanField(default=False)
    REQUEST_STATUS = [
        ("PENDING", "PENDING"),
        ("ACTIVE", "ACTIVE"),
        ("SUSPENDED", "SUSPENDED"),
        ("REVOKED", "REVOKED"),
    ]
    status = models.CharField(max_length=100, choices=REQUEST_STATUS)
    team_account_user_type = models.ForeignKey(
        TeamCategoryType, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return str(self.team_account.name + "" + self.user_account.username)


class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    is_deleted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=255, choices=RECORD_STATUS, default="ACTIVE")
    date_deleted = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="designation_deleted_by",
        null=True, blank=True
    )

    def __str__(self):
        return "{}".format(self.name)


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    department_section = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="department_section",
        null=True,
        blank=True,
    )
    date_deleted = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=255, choices=RECORD_STATUS, default="ACTIVE")
    deleted_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="section_deleted_by",
        null=True, blank=True
    )

    def __str__(self):
        return "{}".format(self.name)


class Staff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="staff_user",
        null=True, blank=True
    )
    firstname = models.CharField(max_length=255, null=True, blank=True)
    middlename = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    # fullname = models.CharField(max_length=500,null=True, blank=True)
    user_designation = models.ForeignKey(
        Designation,
        on_delete=models.CASCADE,
        related_name="staff_designation",
        null=True,
        blank=True,
    )
    user_section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="staff_user_section",
        null=True,
        blank=True,
    )
    employeenum = models.CharField(
        max_length=255, unique=True, null=True, blank=True)
    phonenum = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    user_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="staff_department",
        null=True,
        blank=True,
    )
    identification_type = models.CharField(
        max_length=1000, blank=True, null=True)
    is_phoneverified = models.BooleanField(default=False)
    is_emailverified = models.BooleanField(default=False)
    is_passwordverified = models.BooleanField(default=False)
    date_registered = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Staff"

    def __str__(self):
        return str(self.userid)


class CodeVerification(models.Model):
    SMS = "SMS"
    EMAIL = "EMAIL"
    VERIFICATION_MODES = [
        (SMS, "SMS"),
        (EMAIL, "EMAIL"),
    ]
    LOGIN = "LOGIN"
    REGISTRATION = "REGISTRATION"
    MODULE_TYPES = [
        (LOGIN, "LOGIN"),
        (REGISTRATION, "REGISTRATION"),
    ]
    REVOKED = "REVOKED"
    PENDING = "PENDING"
    STATUS_TYPES = [
        (REVOKED, "REVOKED"),
        (PENDING, "PENDING"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phonenum = models.IntegerField(blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    generationtime = models.DateTimeField()
    exptime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_TYPES)
    vrftype = models.CharField(max_length=50, choices=VERIFICATION_MODES)
    module = models.CharField(max_length=50, choices=MODULE_TYPES)

    def __str__(self):
        return str(self.code)


class GroupProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    userid = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="group_user",
        blank=True,
        null=True,
    )
    teamid = models.ForeignKey(
        TeamAccount,
        on_delete=models.CASCADE,
        null=True,
        related_name="group_team",
        blank=True,
    )
    name = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(
        max_length=255, null=True, blank=True)
    phonenum = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    date_registered = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Groups"

    def __str__(self):
        return str(self.name)
