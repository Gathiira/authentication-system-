import pytz
from django.db import transaction
from rest_framework.exceptions import APIException
from oauth2_provider.generators import \
    generate_client_id, generate_client_secret
from oauth2_provider.models import get_application_model
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.apps import apps as system_apps
from datetime import datetime, timedelta
import jwt
from django.conf import settings


application_label = 'authentication'


class ApplicationUser:

    def __init__(self) -> None:
        pass

    def create_application_user(self, user, email):
        try:
            with transaction.atomic():
                new_client_id = generate_client_id()
                new_client_secret = generate_client_secret()

                application_data = {
                    "user": user,
                    "client_id": new_client_id,
                    "client_secret": new_client_secret,
                    "name": email,
                    "skip_authorization": False,
                    "redirect_uris": "",
                    "client_type": 'confidential',
                    "authorization_grant_type": 'password'
                }

                new_application = get_application_model().objects.create(**application_data)
                new_application.save()

                if new_application:
                    return True
                return False
        except Exception as e:
            raise APIException({e})

    def fetch_user_details_info(self, userid):
        system_user_details = []

        try:
            user_details = get_user_model().objects.get(id=userid)
        except Exception as e:
            return system_user_details
        user_details_id = user_details.id
        user_category_type = user_details.usertype
        app_model = user_category_type.model_name
        if not bool(app_model):
            return system_user_details
        try:
            reference_model = system_apps.get_model(
                application_label, app_model, require_ready=True)
        except Exception:
            return system_user_details
        try:
            user_details = reference_model.objects.get(
                userid_id=user_details_id)
        except Exception:
            return system_user_details

        fullname = ''
        organization_bio_data = {}

        if hasattr(user_details, 'user_department'):
            user_assigned_department = user_details.user_department
            organization_details = user_assigned_department.ministry
            department_info = {
                "id": str(user_assigned_department.id),
                "name": user_assigned_department.name,
                "code": user_assigned_department.code
            }
            if hasattr(user_details, 'user_designation'):
                user_designation = user_details.user_designation
                try:
                    designation_detail = {
                        "name": user_designation.name,
                        "code": user_designation.code
                    }
                except Exception as e:
                    print(e)
                    designation_detail = None

            else:
                designation_detail = None

            organization_info = {
                "name": organization_details.name,
                "code": organization_details.code,
                "department_details": department_info,
                "designation": designation_detail

            }

            organization_bio_data.update({
                "organization": organization_info

            })
            # try:

            # except Exception:

        if hasattr(user_details, 'fullname'):
            fullname = user_details.fullname
        elif hasattr(user_details, 'name'):
            fullname = user_details.name

        system_user_details.append({
            "userid": str(user_details_id),
            "fullname": fullname,
            "organization": organization_bio_data
        })
        return system_user_details

    def fetch_user_groups(self, userid):
        userroles = []
        try:
            user_details = get_user_model().objects.get(id=userid)
        except Exception:
            return []
        primary_role = user_details.primary_role
        query_set = Group.objects.filter(user=userid)
        for groups in query_set:
            if str(groups.id) == str(primary_role):
                is_primary_role = True
            else:
                is_primary_role = False

            userroles.append(
                {"groupname": groups.name,
                    "is_primary_role": is_primary_role,
                 })
        return userroles

    def generate_jwt_token(self, userid):
        userprofile = self.fetch_user_details_info(userid)
        userroles = self.fetch_user_groups(userid)
        fullname = userprofile[0]['fullname']
        userprofileid = userprofile[0]['userid']
        organization = userprofile[0]['organization']
        current_timezone = pytz.timezone(settings.TIME_ZONE)
        access_token_expiry = datetime.now(current_timezone) + timedelta(
            seconds=settings.ACCESS_TOKEN_EXPIRY)
        access_token_issued_at = datetime.now(current_timezone)
        payload = {
            "user": str(userprofileid),
            "fullname": str(fullname),
            "organization": organization,
            "roles": userroles,
            'exp': access_token_expiry,
            'iat': access_token_issued_at
        }
        jwttoken = jwt.encode(payload, settings.TOKEN_SECRET_KEY)
        return jwttoken
