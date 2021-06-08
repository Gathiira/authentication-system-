from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import get_user_model
from django.apps import apps as system_apps

from oauth2_provider.views.generic import ProtectedResourceView


from authentication import serializers as auth_serializers
from authentication import models as auth_models


application_label = 'authentication'


class UserViewSet(ProtectedResourceView, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_headers(self):
        headers = {
            'Authorization':
            self.request.headers.get('Authorization'),
            'JWTAUTH': self.request.headers.get('JWTAUTH'),
        }
        return headers

    def get_queryset(self):
        return []

    def get_serializer_context(self):
        context = self.get_headers()
        return context

    @action(methods=["GET"],
            detail=False,
            url_path="bulk-get-user-details",
            url_name="bulk-get-user-details")
    def bulk_get_user_details(self, request):
        payload = request.data
        serializer = auth_serializers.GetUserDetailSerializer(
            data=payload, many=True)
        if serializer.is_valid():
            user_account_details = []

            for user_record_details in payload:
                user_profile_details = {}
                userid = user_record_details['userid']
                print(userid)

                try:
                    user_details = get_user_model().objects.get(id=userid)
                except Exception:
                    pass
                try:
                    profile_info = {}
                    user_category_type = user_details.usertype
                    user_serializer = user_category_type.serializer
                    user_category_type_name = user_category_type.name
                    user_category = user_details.usertype.category.name
                    app_model = user_category_type.model_name
                    reference_serializer = getattr(
                        auth_serializers, user_serializer)
                    if app_model is None or not app_model:
                        pass

                    else:
                        try:
                            reference_model = system_apps.get_model(
                                application_label, app_model, require_ready=True)
                        except Exception:
                            pass
                        try:
                            userprofiledetails = reference_model.objects.get(
                                userid_id=user_details.id)
                        except Exception:
                            pass

                        profile_photo_details = auth_serializers. \
                            UserProfilePhotoSerializer(
                                user_details, many=False,
                                context=self.get_headers())
                        profile_info_photo = profile_photo_details.data
                        notification_info = {
                            "enable_phone_notification":
                            user_details.enable_phone_notification,
                            "enable_email_notification":
                            user_details.enable_email_notification,
                            "enable_system_notification":
                            user_details.enable_system_notification,
                        }
                        user_categorization = {
                            "usertype": user_category,
                            "usercategorytype": user_category_type_name
                        }
                        role_query_set = user_details.groups.all()
                        role_query_data = auth_serializers. \
                            GroupDetailSerializer(role_query_set,
                                                  many=True)
                        user_roles = {
                            "roles": role_query_data.data}
                        user_details = reference_serializer(
                            userprofiledetails, many=False).data
                        profile_info.update(user_details)
                        profile_info.update(user_categorization)
                        profile_info.update(user_roles)
                        profile_info.update(profile_info_photo)
                        profile_info.update(notification_info)
                        # user_profile_details = profile_info
                        user_profile_details.update({
                            userid: profile_info

                        })
                except Exception:
                    user_profile_details.update({
                        userid: profile_info
                    })
                user_account_details.append(user_profile_details)
                # user_account_details.append({
                #     userid: user_profile_details
                # })
            return Response(user_account_details, status=status.HTTP_200_OK)

        else:
            return Response(
                {'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"],
            detail=False,
            url_path="create-profile-photo",
            url_name="create-profile-photo")
    def create_profile_photo(self, request):
        payload = request.data
        account_user = request.user
        print(account_user)
        serializer = auth_serializers. \
            ProfilePhotoSerializer(data=request.data)
        if serializer.is_valid():
            profile_photo = payload['profile_photo']
            try:
                user_details = auth_models.User.objects.get(id=account_user.id)
            except Exception:
                return Response(
                    {"details": "Invalid User"},
                    status=status.HTTP_400_BAD_REQUEST)
            user_details.profile_photo = profile_photo
            user_details.save()
            return Response(
                {'details': 'Successfully Created'},
                status=status.HTTP_200_OK)
        else:
            return Response(
                {'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"],
            detail=False,
            url_path="update-profile-photo",
            url_name="update-profile-photo")
    def update_profile_photo(self, request):
        payload = request.data
        account_user = request.user
        serializer = auth_serializers. \
            ProfilePhotoSerializer(data=request.data)
        if serializer.is_valid():
            profile_photo = payload['profile_photo']
            try:
                user_details = auth_models.User.objects.get(id=account_user.id)
            except Exception:
                return Response(
                    {"details": "User does not exist"},
                    status=status.HTTP_400_BAD_REQUEST)
            user_details.profile_photo = profile_photo
            user_details.save()
            return Response(
                {'details': 'Successfully Updated'},
                status=status.HTTP_200_OK)
        else:
            return Response(
                {'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST)
