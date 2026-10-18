from django.db import IntegrityError, transaction

from rest_framework.exceptions import NotFound

from .exceptions import BusinessRuleViolation
from .models import Membership, Project
from .permissions import ADMIN_MANAGEABLE_ROLES, require_target_role


@transaction.atomic
def create_project(*, owner, name, description=""):
    """Create a project and its Owner membership in one transaction."""
    project = Project.objects.create(name=name, description=description)
    Membership.objects.create(project=project, user=owner, role=Membership.Role.OWNER)
    return project


def add_member(*, project, user, role):
    try:
        with transaction.atomic():
            return Membership.objects.create(project=project, user=user, role=role)
    except IntegrityError:
        # Backed by the (project, user) unique constraint, so it is race-safe.
        raise BusinessRuleViolation("This user is already a member of the project.")


@transaction.atomic
def remove_member(*, project_id, actor_role, target_user_id):
    try:
        target = Membership.objects.get(project_id=project_id, user_id=target_user_id)
    except Membership.DoesNotExist:
        raise NotFound("Member not found.")

    if actor_role == Membership.Role.ADMIN:
        require_target_role(target.role, ADMIN_MANAGEABLE_ROLES)

    if target.role == Membership.Role.OWNER:
        # Lock the project row so concurrent removals of Owners are serialized
        # and the "at least one Owner" rule cannot be bypassed by a race.
        Project.objects.select_for_update().get(pk=project_id)
        owner_count = Membership.objects.filter(
            project_id=project_id, role=Membership.Role.OWNER
        ).count()
        if owner_count <= 1:
            raise BusinessRuleViolation("A project must have at least one Owner.")

    target.delete()
