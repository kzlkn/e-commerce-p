from django.urls import path
from . import views

urlpatterns = [
    path('add-article/<str:category>', views.article_create, name="article-create"),
    path('delete/<int:pk>/', views.article_delete, name='article-delete'),
    path('show/<int:pk>/', views.article_detail, name='article-detail'),
    path('edit-article/<int:pk>/', views.article_edit, name='article-edit'),
    path('show/<str:category>', views.article_list, name='article-list'),
    path('show/', views.article_list, name='article-list'),
    path('article-pdf/<int:pk>/', views.article_pdf, name='article-pdf'),
    path('delete-comment/<int:pk>/', views.comment_delete, name='comment-delete'),
    path('comment-edit/<int:pk>/', views.comment_edit, name='comment-edit'),
    path('show/<int:pk>/report/<str:true_or_false>/', views.report, name='comment-report'),
    path('show/<int:pk>/vote/<str:up_or_down>/', views.vote, name='comment-vote'),
    path('contact/', views.customer_support_inquiry, name='customer-support'),
    path('customer-support-overview/', views.customer_support_overview, name='customer-support-overview'),
    path('search/', views.article_list, name='search'),
]
