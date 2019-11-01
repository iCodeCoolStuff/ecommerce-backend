from rest_framework.exceptions import APIException

class PasswordMismatchException(APIException):
    status_code = 400
    default_detail = "Passwords do not match."

class PasswordConfirmationMismatchException(APIException):
    status_code = 400
    default_detail = "Password and confirmation do not match."