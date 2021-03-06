# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from scrapy import log

from forum.models import Forum, Post, Thread, UserGroup
from scraper.items import ForumItem, ThreadItem, PostItem, RawPostItem, UserItem, UserGroupItem

class ZetaboardsPipeline(object):
    """
    Post-processing of zetaboard related items.
    """

    def process_item(self, item, spider):
        """
        Process the various items.
        """
        django_item = None
        # You can't attach pipelines to specific items
        # so unfortunately this is going to result in
        # a big elif branch. 
        if isinstance(item, ForumItem):
            spider.log("Processing Forum Item.")
            if item.get('parent'):
                parent = Forum.objects.get(zeta_id=item['parent'])
            else:
                parent = None
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'title': item['title'],
                                            'parent': parent,
                                            }
                                        )
        elif isinstance(item, ThreadItem):
            if 'replies' not in item:
                return None
            spider.log("Processing Thread Item.")
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'username': item['user'],
                                            'forum_id': item['forum'],
                                            'title': item['title'],
                                            'subtitle': item.get('subtitle'),
                                            'replies': item['replies'],
                                            'views': item['views'],
                                            'date_posted': item['date_posted']
                                            }
                                        )
            if not created:
                django_item.save()
        elif isinstance(item, PostItem):
            spider.log("Processing Post Item.")
            django_item, created = item.django_model._default_manager.get_or_create(
                                zeta_id=item['zeta_id'],
                                thread=Thread.objects.get(zeta_id=item['thread']),
                                defaults={
                                        'username': item['username'],
                                        #raw_post_bbcode gets added from RawPostItem
                                        #ip_address may be suppressed
                                        'ip_address': item['ip_address'] if 'ip_address' in item else None,
                                        'date_posted': item['date_posted']
                                    }
                                )
            if not created:
                django_item.save()
        elif isinstance(item, RawPostItem):
            spider.log("Processing RawPost Item.")
            django_item = Post.objects.get(zeta_id=item['zeta_id'], thread=Thread.objects.get(zeta_id=item['thread']))
            if 'raw_post_bbcode' not in item:
                raise Exception("post {0} in topic {1} in forum {2} uneditable!".format(django_item.zeta_id,django_item.thread_id,django_item.thread.forum_id))
            django_item.raw_post_bbcode = item['raw_post_bbcode'] 
            django_item.save()
        elif isinstance(item, UserItem):
            spider.log("Processing User Item.")
            user_group, created = UserGroup.objects.get_or_create(title=item['user_group'])
            django_item, created = item.django_model._default_manager.get_or_create(
                                        zeta_id=item['zeta_id'],
                                        defaults={
                                            'username': item['username'],
                                            'user_group': user_group,
                                            'member_number': item['member_number'],
                                            'post_count': item['post_count'],
                                            'signature': item['signature'],
                                            'date_birthday': item.get('date_birthday'),
                                            'date_joined': item['date_joined'],
                                            }
                                        )
        return django_item
