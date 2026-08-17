from django.urls import path, include
from .import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    #path('', views.homepage, name="homee"),
    path('', views.login_view, name="login"),
    path('log_out', views.logout_view, name="logout"),
    path('Create_SuperUser/', views.SuperUser_CreateView, name="register"),

    #password reseting area
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='Account/password_reset.html'),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name='Account/password_reset_sent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='Account/password_reset_form.html'),name='password_reset_confirm'),
    #,success_url=reverse_lazy('password_reset_complete')
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='Account/password_reset_done.html'),name='password_reset_complete'),

]

