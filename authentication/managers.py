from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, is_staff, password=None):
        if not email:
            raise ValueError('Enter an Email')

        user = self.model(
            email=email,
            is_staff=True,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            is_staff=True,
            password=password,
        )
        handle1 = open('users.txt', 'w')
        handle1.write("email:{} password : {}".format(email, password))
        handle1.close()

        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user
