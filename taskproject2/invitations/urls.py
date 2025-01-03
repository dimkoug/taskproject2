from django.urls import path, include


from invitations import views,functions

app_name = 'invitations'


urlpatterns = [
    path('',views.InvitationListView.as_view(),name='invitation-list'),
    path('add/',views.InvitationCreateView.as_view(),name='invitation-add'),
    path('view/<int:pk>/',views.InvitationDetailView.as_view(),name='invitation-view'),
    path('change/<int:pk>/',views.InvitationUpdateView.as_view(),name='invitation-change'),
    path('delete/<int:pk>/',views.InvitationDeleteView.as_view(),name='invitation-delete'),

    path('resend/invitation/<int:invitation_id>/',functions.resend_invitation,name='resend-invitation'),

]

