from django.db import models
from django.contrib.auth.models import User
from Useradmin.models import ExtendedUser


class Article(models.Model):
    ARTICLE_CATEGORIES = [
        ('ECS', 'Electronics'),
        ('SUP', 'Supplements'),
        ('NUT', 'Nutrition'),
        ('BKS', 'Books')
    ]

    AGE_RESTRICTION = [
        ('0', 'FSK 0'),
        ('6', 'FSK 6'),
        ('12', 'FSK 12'),
        ('16', 'FSK 16'),
        ('18', 'FSK 18'),
    ]

    average_review = models.FloatField(blank=True, null=True, default=None)
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True)
    manufacturer = models.CharField(max_length=50)
    deliveryIn = models.CharField(max_length=50)
    category = models.CharField(max_length=3, choices=ARTICLE_CATEGORIES, )
    ageRestriction = models.CharField(max_length=2, choices=AGE_RESTRICTION, blank=True, null=True, default=None)
    price = models.CharField(max_length=10)
    quantity = models.IntegerField(default=1)
    extended_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='extended_users',
                                      related_query_name='extended_user', default=1)

    class Meta:
        ordering = ['name']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def get_full_title(self):
        return_string = self.name
        if self.subtitle:  # if subtitle is not empty
            return_string = self.name + ': ' + self.subtitle
        return return_string

    def __str__(self):
        return self.name + ' (' + self.manufacturer + ')'

    def __repr__(self):
        return self.get_full_title() + ' / ' + self.name + ' / ' + self.category

    def get_average_review(self):
        return self.average_review

    def set_average_review(self, review: str):
        prior_average = self.get_average_review()
        if prior_average is not None:
            new_review = (prior_average + int(review)) / 2
            self.average_review = new_review.__round__(2)
        else:
            self.average_review = int(review)
        self.save()

    def get_related_article_id(self):
        return self.id


# Specified Model for Articles that fit the Books Category
class Book(Article):
    GENRES = [
        ('PRO', 'Productivity'),
        ('PER', 'Personality Development'),
        ('HAP', 'Happiness'),
        ('HLT', 'Health')
    ]

    TYPES = [
        ('HAR', 'Hardcover'),
        ('PAP', 'Paperback'),
        ('EBK', 'E-Book')
    ]

    related_article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name="related_book")
    author = models.CharField(max_length=60)
    pages = models.IntegerField(default=100)
    isbn = models.IntegerField(unique=True)
    genre = models.CharField(choices=GENRES, max_length=3, default="No Genre specified.")
    type = models.CharField(choices=TYPES, max_length=3, default="Book")
    image = models.ImageField(upload_to='article-images/books', default=None, null=True, blank=True)

    def get_title_and_author_of_book(self):
        return f'{self.related_article.name} by {self.author}'

    def __str__(self):
        return f'Book: {self.get_title_and_author_of_book()} | {self.genre} | {self.type}'

    def __repr__(self):
        return f'{self.get_full_title()} / {self.related_article.category} / {self.genre} / {self.type}'


# Specified Model for Articles that fit the Electronics Category
class ElectronicDevice(Article):
    TYPES = [
        ('SFW', 'Software'),
        ('HAW', 'Hardware'),
        ('FIT', 'Fitness Tracker'),
        ('SLT', 'Sleep Tracker')
    ]

    related_article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name="related_e_device")
    type = models.CharField(choices=TYPES, max_length=3)
    material = models.CharField(max_length=100)
    color = models.CharField(max_length=20)
    battery_life = models.CharField(max_length=30, default="3 hours")
    # image field moved down here so the path can be specified based on the type of article child class
    image = models.ImageField(upload_to='article-images/electronic-devices', default=None, null=True, blank=True)

    def __str__(self):
        return f'ElectronicDevice: {self.related_article.category}: {self.related_article.name} | {self.type} | ' \
               f'{self.related_article.manufacturer} | {self.color}'

    def __repr__(self):
        return f'{self.related_article.name} / {self.related_article.category} / {self.type}'


# Specified Model for Articles that fit the Nutrition Category
class Superfood(Article):
    related_article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name="related_superfood")
    weight = models.CharField(max_length=20, default="100g")
    ingredients = models.CharField(max_length=500, default="No Ingredients given", blank=True)
    vegan = models.BooleanField(default=True)
    image = models.ImageField(upload_to='article-images/superfoods', default=None, null=True, blank=True)

    def __str__(self):
        return f'Superfood: {self.related_article.name} | {self.related_article.manufacturer} | {self.weight}'

    def __repr__(self):
        return f'{self.related_article.get_full_title()} / {self.related_article.name} / ' \
               f'{self.related_article.category}'


# Specified Model for Articles that fit the Supplement Category
class Supplement(Article):
    FIELDS_OF_USE = [
        ('RLX', 'Relaxation & Sleep'),
        ('VIT', 'Vitamins'),
        ('EGY', 'Energy'),
        ('STR', 'Strength'),
    ]

    related_article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name="related_supplement")
    weight = models.CharField(max_length=20, default="100g")
    field_of_use = models.CharField(choices=FIELDS_OF_USE, max_length=3)
    recommended_frequency_of_use = models.CharField(max_length=20, default="One daily unit")
    ingredients = models.CharField(max_length=300, default="No Ingredients given")
    image = models.ImageField(upload_to='article-images/supplements', default=None, null=True, blank=True)

    def __str__(self):
        return f'Supplement: {self.related_article.name} | {self.related_article.manufacturer} | {self.weight} | ' \
               f'{self.field_of_use}'

    def __repr__(self):
        return f'{self.related_article.get_full_title()} / {self.related_article.name} / ' \
               f'{self.related_article.category}'


class Comment(models.Model):
    REVIEW_STARS = [
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ]

    title = models.CharField(max_length=100, default="")
    text = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    # User now references Extended User Model instead of default Django-User
    extended_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, default=None)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, default=None)
    article_review = models.CharField(max_length=1, choices=REVIEW_STARS, default="")
    report = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def set_report(self, true_or_false):
        if true_or_false == 'true':
            self.report = True
        else:
            self.report = False
        self.save()

    def get_report(self):
        return self.report

    def get_comment_prefix(self):
        if len(self.text) > 50:
            return self.text[:50] + '...'
        else:
            return self.text

    def get_user_has_upvoted(self, user):
        upvotes_found = self.get_upvotes().filter(extended_user=user).exists()
        return upvotes_found

    def get_user_has_downvoted(self, user):
        downvotes_found = self.get_downvotes().filter(extended_user=user).exists()
        return downvotes_found

    def remove_upvote(self, user):
        self.get_upvotes().filter(extended_user=user).delete()

    def remove_downvote(self, user):
        self.get_downvotes().filter(extended_user=user).delete()

    def get_upvotes(self):
        upvotes = Vote.objects.filter(up_or_down='U', comment=self)
        return upvotes

    def get_upvotes_count(self):
        return len(self.get_upvotes())

    def get_downvotes(self):
        downvotes = Vote.objects.filter(up_or_down='D', comment=self)
        return downvotes

    def get_downvotes_count(self):
        return len(self.get_downvotes())

    def vote(self, up_or_down, user):
        U_or_D = 'U'
        if up_or_down == 'down':
            U_or_D = 'D'
        vote = Vote.objects.create(up_or_down=U_or_D, comment=self, extended_user=user)
        return vote

    def get_related_article_id(self):
        return self.article.id

    def __str__(self):
        return self.get_comment_prefix() + ' (' + self.extended_user.user.username + ')'

    def __repr__(self):
        return self.get_comment_prefix() + ' (' + self.extended_user.user.username + ' / ' + str(self.timestamp) + ')'


class CustomerSupportRequest(models.Model):
    subject = models.CharField(max_length=100, default="")
    text = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    extended_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, default=None)
    user_contact = models.CharField(max_length=100, default="")

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return self.subject + ' (' + self.extended_user.user.username + ')'

    def __repr__(self):
        return self.subject + ' (' + self.extended_user.user.username + ' / ' + str(self.timestamp) + ')'


class Vote(models.Model):
    VOTE_TYPES = [
        ('U', 'up'),
        ('D', 'down'),
    ]

    up_or_down = models.CharField(max_length=1, choices=VOTE_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, default="")
    extended_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, default="1")

    def __str__(self):
        return self.up_or_down + ' on ' + self.comment.title


# --- Helper Functions ---
def get_related_article_from_article(article):
    related_article = None
    query_set = None
    if article.category == 'BKS':
        query_set = Book.objects.filter(related_article=article)
    elif article.category == 'ECS':
        query_set = ElectronicDevice.objects.filter(related_article=article)
    elif article.category == 'NUT':
        query_set = Superfood.objects.filter(related_article=article)
    elif article.category == 'SUP':
        query_set = Supplement.objects.filter(related_article=article)
    if len(query_set) > 0:
        related_article = query_set.first()
    return related_article
