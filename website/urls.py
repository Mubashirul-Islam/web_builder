from django.urls import path
from website import views


urlpatterns = [
    path("websites/", views.websiteList.as_view(), name="website-list"),
    path("websites/<int:pk>/", views.websiteDetail.as_view(), name="website-detail"),
    path("pages/", views.PageList.as_view(), name="page-list"),
    path("pages/<int:pk>/", views.PageDetail.as_view(), name="page-detail"),
    path(
        "websites/<int:pk>/build/", views.WebsiteBuild.as_view(), name="website-build"
    ),
    path(
        "websites/<int:pk>/upload/",
        views.AssetUpload.as_view(),
        name="website-asset-upload",
    ),

    path("websites/<int:pk>/edit/", views.WebsiteEdit.as_view(), name="website-edit"),
    path("websites/<int:pk>/edit/refresh/", views.WebsiteEditRefresh.as_view(), name="website-edit-refresh"),
    path("websites/<int:pk>/edit/save/", views.WebsiteEditSave.as_view(), name="website-edit-save"),
    #path("websites/<int:pk>/edit/exit/", views.WebsiteEditExit.as_view(), name="website-edit-exit"),
]
