from rest_framework import status
from rest_framework.exceptions import APIException


class BusinessRuleViolation(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The request violates a business rule."
    default_code = "business_rule_violation"
