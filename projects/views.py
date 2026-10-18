from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Membership, Project
from .permissions import (
    ADMIN_MANAGEABLE_ROLES,
    DELETE_PROJECT_ROLES,
    EDIT_PROJECT_ROLES,
    MANAGE_MEMBERS_ROLES,
    Role,
    get_membership_or_404,
    require_role,
    require_target_role,
)
from .serializers import AddMemberSerializer, MembershipSerializer, ProjectSerializer


class ProjectListCreateView(APIView):
    def get(self, request):
        # Single query: the join on memberships filters to the user's projects.
        # (project, user) is unique, so no duplicate rows are possible.
        projects = Project.objects.filter(memberships__user=request.user).order_by("id")
        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = services.create_project(owner=request.user, **serializer.validated_data)
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    def get(self, request, project_id):
        membership = get_membership_or_404(project_id, request.user)
        project = membership.project
        members = Membership.objects.filter(project=project).select_related("user").order_by("id")
        data = ProjectSerializer(project).data
        data["members"] = MembershipSerializer(members, many=True).data
        return Response(data)

    def put(self, request, project_id):
        return self._update(request, project_id, partial=False)

    def patch(self, request, project_id):
        return self._update(request, project_id, partial=True)

    def delete(self, request, project_id):
        membership = get_membership_or_404(project_id, request.user)
        require_role(membership, DELETE_PROJECT_ROLES)
        membership.project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, project_id, partial):
        membership = get_membership_or_404(project_id, request.user)
        require_role(membership, EDIT_PROJECT_ROLES)
        serializer = ProjectSerializer(membership.project, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProjectMemberCreateView(APIView):
    def post(self, request, project_id):
        requester = get_membership_or_404(project_id, request.user)
        require_role(requester, MANAGE_MEMBERS_ROLES)

        serializer = AddMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data["role"]
        if requester.role == Role.ADMIN:
            require_target_role(role, ADMIN_MANAGEABLE_ROLES)

        membership = services.add_member(
            project=requester.project, user=serializer.validated_data["user"], role=role
        )
        return Response(MembershipSerializer(membership).data, status=status.HTTP_201_CREATED)


class ProjectMemberDetailView(APIView):
    def delete(self, request, project_id, user_id):
        requester = get_membership_or_404(project_id, request.user)
        require_role(requester, MANAGE_MEMBERS_ROLES)
        services.remove_member(
            project_id=project_id, actor_role=requester.role, target_user_id=user_id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
