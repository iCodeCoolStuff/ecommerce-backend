from rest_framework.exceptions import APIException

class PasswordMismatchException(APIException):
    status_code = 400
    default_detail = "Passwords do not match."

class PasswordValidationException(APIException):
    status_code = 400
    default_detail = "Passwords must be at least 8 characters long, and contain one capital letter and one number"


class PasswordConfirmationMismatchException(APIException):
    status_code = 400
    default_detail = "Password and confirmation do not match."


class EmptyCartException(APIException):
    status_code = 400
    default_detail = "Cart cannot be empty."


class ItemDoesntExist(APIException):
    status_code = 400
    default_detail = "Entered in an item id that doesn\'t correspond with a product"


class ItemAlreadyExists(APIException):
    status_code = 400
    default_detail = "Entered in an item for a product multiple times"


class NoItemsException(APIException):
    status_code = 400
    default_detail = "No items provided"