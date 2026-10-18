from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Membership

Role = Membership.Role

# Roles allowed for each operation (see the access matrix).
EDIT_PROJECT_ROLES = {Role.OWNER, Role.ADMIN}
DELETE_PROJECT_ROLES = {Role.OWNER}
MANAGE_MEMBERS_ROLES = {Role.OWNER, Role.ADMIN}
# Roles an Admin is allowed to add or remove (an Owner may handle any role).
ADMIN_MANAGEABLE_ROLES = {Role.MEMBER}


def get_membership_or_404(project_id, user):
    """Return the user's membership (with its project) in a single query.

    Non-members get 404 so they cannot tell whether the project exists.
    """
    try:
        return Membership.objects.select_related("project").get(
            project_id=project_id, user=user
        )
    except Membership.DoesNotExist:
        raise NotFound("Project not found.")


def require_role(membership, allowed_roles):
    if membership.role not in allowed_roles:
        raise PermissionDenied("You do not have permission to perform this action.")


def require_target_role(target_role, allowed_roles):
    """Check the role being assigned or removed when the actor is an Admin."""
    if target_role not in allowed_roles:
        raise PermissionDenied("You do not have permission to perform this action.")
