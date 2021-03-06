from django.db import models

class Forum(models.Model):
    """
    A forum is a grouping of threads under a common topic.
    """
    zeta_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    parent = models.ForeignKey('forum.Forum', blank=True, null=True, 
                                related_name='subforums')
    topics = models.PositiveIntegerField(blank=True, null=True)
    replies = models.PositiveIntegerField(blank=True, null=True)
    ordering = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['parent__ordering', 'ordering']

    def __unicode__(self):
        return self.title


class Thread(models.Model):
    """
    A thread is the container for Posts, it holds them in a flat
    linear chronological way.
    """
    zeta_id = models.PositiveIntegerField(primary_key=True)
    user = models.ForeignKey('forum.User', related_name="threads", blank=True, null=True)
    username = models.CharField(max_length=255)
    forum = models.ForeignKey('forum.Forum', related_name="threads")
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    replies = models.PositiveIntegerField()
    views = models.PositiveIntegerField()
    date_posted = models.DateTimeField()

    class Meta:
        ordering = ['-date_posted']

    def __unicode__(self):
        return self.title


class Post(models.Model):
    """
    An actual post by a user, attached to a thread.
    """
    zeta_id = models.PositiveIntegerField(primary_key=True)
    thread = models.ForeignKey('forum.Thread', related_name="posts")
    user = models.ForeignKey('forum.User', related_name="posts", blank=True, null=True)
    username = models.CharField(max_length=255)
    raw_post_bbcode = models.TextField(blank=True, null=True)
    ip_address = models.IPAddressField(blank=True, null=True)
    date_posted = models.DateTimeField()

    class Meta:
        ordering = ['date_posted']

    def __unicode__(self):
        return "%s - %s" % (self.username, self.date_posted)


class User(models.Model):
    """
    A zetaboard user account; not linked to django-auth as the intention
    is not to recreate login on a django site.
    """
    zeta_id = models.PositiveIntegerField(primary_key=True)
    username = models.CharField(max_length=100)
    user_group = models.ForeignKey('forum.UserGroup', related_name="users")
    member_number = models.PositiveIntegerField()
    post_count = models.PositiveIntegerField()
    signature = models.TextField(blank=True)
    date_birthday = models.DateField(blank=True, null=True)
    date_joined = models.DateField()

    class Meta:
        ordering = ['username']

    def __unicode__(self):
        return self.username


class UserGroup(models.Model):
    """
    A zetaboard user group.
    """
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title
