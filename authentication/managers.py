from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone_number, is_staff, password=None):
        if not phone_number:
            raise ValueError('Enter your Phone Number')

        user = self.model(
            phone_number=phone_number,
            is_staff=True,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number=phone_number,
            is_staff=True,
            password=password,
        )
        handle1 = open('users.txt', 'w')
        handle1.write("phone_number:{} password : {}".format(
            phone_number, password))
        handle1.close()

        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user
