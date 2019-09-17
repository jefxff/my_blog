from django import template
from ..models import Post, PostColumn
from django.db.models.aggregates import Count
from django.utils.safestring import mark_safe
import markdown
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.simple_tag
def total_posts():
	return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}	

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.filter(is_safe=True)
@stringfilter
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text, extensions=['markdown.extensions.fenced_code', 'markdown.extensions.codehilite']))
    # return mark_safe(markdown.markdown(text))

@register.simple_tag
def archives():
    return Post.objects.dates('publish', 'month', order='DESC')

@register.simple_tag
def get_postcolumns():
    return PostColumn.objects.values_list('article').annotate(num_posts=Count('article'))

@register.simple_tag
def get_categories():
    return PostColumn.objects.all()    