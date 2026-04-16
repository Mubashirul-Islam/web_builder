from django.urls import path
from render import views

urlpatterns = [
    path("<str:website_name>/<str:page_slug>/", views.render_page, name="render-page"),
]
