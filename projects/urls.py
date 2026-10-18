from django.urls import path

from .views import (
    ProjectDetailView,
    ProjectListCreateView,
    ProjectMemberCreateView,
    ProjectMemberDetailView,
)

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-list"),
    path("<int:project_id>/", ProjectDetailView.as_view(), name="project-detail"),
    path("<int:project_id>/members/", ProjectMemberCreateView.as_view(), name="project-member-add"),
    path(
        "<int:project_id>/members/<int:user_id>/",
        ProjectMemberDetailView.as_view(),
        name="project-member-remove",
    ),
]
