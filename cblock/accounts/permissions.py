from rest_framework.permissions import BasePermission


class IsContractAdmin(BasePermission):

    def has_permission(self, request, view):

        # call contract to check admin rights

        pass