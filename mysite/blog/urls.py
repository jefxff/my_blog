from django.urls import path
from . import views
from .feeds import LastestPostFeed

app_name = 'blog'
urlpatterns = [
    # post views
    path('', views.post_list, name='post_list'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('feed/', LastestPostFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('articlelist/', views.post_articlelist, name='post_articlelist'),
    # # path('archivelist/', views.post_archivelist, name='post_archivelist'),
    path('archives/<int:year>/<int:month>/', views.post_archives, name='post_archives'),
    # path('archives/',views.post_archives, name='post_archives'),
    # path('column/<int:columnID>/', views.column, name='column'),
]