from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("clubs/", views.clubs, name="clubs"),
    path("clubs/<slug:slug>/", views.club_detail, name="club"),
    path("schedule/", views.schedule, name="schedule"),
    path("master-classes/", views.master_classes, name="master_classes"),
    path("teachers/", views.teachers, name="teachers"),
    path("pricing/", views.pricing, name="pricing"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("booking/", views.booking, name="booking"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("search/", views.search, name="search"),
    path("newsletter/", views.newsletter, name="newsletter"),
    path("api/clubs/", views.api_clubs, name="api_clubs"),
    path("api/suggest/", views.api_suggest, name="api_suggest"),
]
