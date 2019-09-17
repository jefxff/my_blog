from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Post, Comment, PostColumn
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.contrib.postgres.search import TrigramSimilarity
from django.core.mail import send_mail
from taggit.models import Tag 
from django.db.models.aggregates import Count, Avg, Sum, Min, Max
import markdown
# 引入 Q 对象
from django.db.models import Q


def post_list(request, tag_slug=None):
    search = request.GET.get('search')
    # object_list = Post.published.all()
    object_list = Post.published.get_queryset().order_by('-id')
    tag = None 
    # Q搜索查询集
    if search:
        object_list = object_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 7) # 3 posts in each page
    page = request.GET.get('page')
    # 文章的分类
    post_column = PostColumn.objects.values_list('title').annotate(num_posts=Count('article'))
    # print(post_column)
    # 文章的归档

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page    
        posts = paginator.page(1)
    except EmptyPage:

        # If page is out of range deliver last page of results    
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag':tag,
                   'post_column':post_column,
                   'search': search
                   })
   
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month, publish__day=day)
    # post.body =markdown.markdown(post.body, extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.toc',], safe_mode=True,enable_attributes=False)
    comments = post.comments.filter(active=True)

    new_comment = None 

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                  .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:4]    
    md = markdown.Markdown(
        extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        # 目录扩展
        'markdown.extensions.toc',
        ])
    post.body = md.convert(post.body)


    return render(request, 'blog/post/detail.html', {'post':post, 'comments':comments, 'new_comment':new_comment, 'comment_form':comment_form, 'similar_posts':similar_posts, 'toc': md.toc})

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_share(request, post_id):
    # 通过id 获取 post 对象
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        # 表单被提交
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # 验证表单数据
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, '384024138@qq.com', [cd['to']])
            sent = True
            # 发送邮件......
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent':sent})

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.objects.annotate(search=SearchVector('title', 'slug', 'body'), ).filter(search=query)
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            search_vector = SearchVector('title', weight='B') + SearchVector('body', weight='A')
            # 搜索权重
            # results = Post.objects.annotate(search=search_vector,rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by('-rank')
            # 三元相似性搜索
            results = Post.objects.annotate(similarity=TrigramSimilarity('title',query),).filter(similarity__gte=0.2).order_by('-similarity')

    return render(request, 'blog/post/search.html', {'query': query, "form": form, 'results': results}) 
 

def post_articlelist(request, tag_slug=None):
    # object_list = Post.published.all()
    column_object_list = PostColumn.objects.values_list('title')
    print(type(column_object_list))
    for y in column_object_list:
        # print(y)
        pass
    object_list = Post.published.get_queryset()
    print(object_list)
    for x in object_list:
        # print(x)
        pass

    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 24) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page    
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results    
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/articlelist.html',
                  {'page': page,
                   'posts': posts,
                   'tag':tag})


def post_archives(request, year, month, tag_slug=None):
    # object_list = Post.published.all()
    object_list = Post.objects.filter(publish__year=year,
                                    publish__month=month
                                    ).order_by('-publish')

    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 8) # 3 posts in each page
    page = request.GET.get('page')
    # y = tag_slug.objects.values_list('title').annotate(num_posts=Count('article'))
    p_count = Post.objects.filter(publish__year=year,
                                    publish__month=month
                                    ).annotate(num_posts=Count('id'))
    # print("=====")
    # for count in p_count:
    #     print(count)
    # print(len(p_count))
    # e_count = len(p_count)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page    
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results    
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag':tag,
                   })  
# 网上的分类
def category(request, pk):
    cate = get_object_or_404(PostColumn, pk=pk)
    print(cate)
    # post_list = PostColumn.objects.filter(PostColumn=cate).order_by('-publish')
    post_list = PostColumn.objects.values_list('title').annotate(num_posts=Count('article'))
    print(post_list)
    return render(request, 'blog/post/list.html', context={'post_list': post_list})


"""
def column(request, pk, tag_slug=None):
    cate = get_object_or_404(PostColumn, pk=pk)
    # post_column = Post.objects.filter(PostColumn=cate).order_by('-publish')
    post_column = PostColumn.objects.values_list('title').annotate(num_posts=Count('article'))

    tag = None 
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_column = post_column.filter(tags__in=[tag])
    paginator = Paginator(post_column, 8) 
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag':tag,
                   'post_column': post_column,
                   })      
"""                