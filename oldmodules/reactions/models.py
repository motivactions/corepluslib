from decimal import Decimal
from functools import cached_property
from logging import getLogger
from math import floor

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()

logger = getLogger("django")


class ReactionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.hide_blocked_user = kwargs.pop("hide_blocked_user", True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.hide_blocked_user:
            qs = super().get_queryset().filter(user__is_active=True)
        else:
            qs = super().get_queryset()
        return qs.select_related("user", "content_type")

    def get(self, *args, **kwargs):
        if self.hide_blocked_user:
            kwargs["user__is_active"] = True
        return super().get(*args, **kwargs)


class ReviewManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("user", "object_type")


class BookmarkManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related("user", "content_type")


class Reaction(models.Model):
    LIKE = "like"
    LOVE = "love"
    PRAY = "pray"
    FLAP = "flap"
    FUNNY = "funny"
    SAD = "sad"
    ANGRY = "angry"
    REACTION_TYPES = (
        (LIKE, _("like")),
        (LOVE, _("love")),
        (PRAY, _("pray")),
        (FLAP, _("flap")),
        (FUNNY, _("funny")),
        (SAD, _("sad")),
        (ANGRY, _("angry")),
    )

    user = models.ForeignKey(
        User,
        related_name="reactions",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    value = models.CharField(
        max_length=25,
        default=LIKE,
        choices=REACTION_TYPES,
        verbose_name=_("value"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    objects = ReactionManager()
    all_objects = ReactionManager(hide_blocked_user=False)

    class Meta:
        # TODO: FIX every user can reaction once for each object
        unique_together = ("user", "content_type", "id")
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")

    def __str__(self):
        return '%s %s "%s"' % (self.user, self.get_value_display(), self.content_object)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.uid,)


class ReactionableModel(models.Model):

    reaction = models.JSONField(
        editable=False,
        verbose_name=_("reaction"),
        help_text=_('JSON fields contains {"like": 1, "love":2, "flap":3}'),
    )

    reactions = GenericRelation(Reaction)

    class Meta:
        abstract = True

    def get_reactions(self, reaction=None):
        extra_filter = {}
        if reaction:
            extra_filter.update({"value": reaction})
            reactions = self.reactions.filter(**extra_filter)
        else:
            reactions = self.reactions.all()
        return reactions

    def calculate_reaction(self):
        reactions = (
            self.get_reactions().values("value").annotate(total=models.Count("id"))
        )
        self.reaction = {obj["value"]: obj["total"] for obj in reactions}

    def save(self, *args, **kwargs):
        self.calculate_reaction()
        return super().save(*args, **kwargs)

    def add_reaction(self, user, value):
        """add reaction to object"""
        content_type = ContentType.objects.get_for_model(self, for_concrete_model=True)
        try:
            reaction = Reaction.objects.get(
                content_type=content_type, object_id=self.id, user=user
            )
            reaction.value = value
            reaction.save()
        except Reaction.DoesNotExist:
            reaction = Reaction(
                content_type=content_type, object_id=self.id, user=user, value=value
            )
            # TODO: Add notification
            reaction.save()
        return reaction

    def user_reaction(self, user):
        reaction = self.get_user_reaction(user)
        if reaction:
            return reaction
        else:
            return None

    def get_user_reaction(self, user):
        return self.reactions.filter(user=user.id).first()


class Bookmark(models.Model):
    user = models.ForeignKey(
        User,
        related_name="bookmarks",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    objects = BookmarkManager()


class BookmarkableModel(models.Model):
    bookmarked = models.PositiveIntegerField(
        default=0,
        verbose_name=_("bookmarked"),
        help_text=_("Total bookmarked"),
    )

    bookmarks = GenericRelation(Bookmark)

    class Meta:
        abstract = True

    def add_bookmark(self, user):
        """add bookmark to object"""
        content_type = ContentType.objects.get_for_model(self, for_concrete_model=True)
        bookmark = self.bookmarks.filter(
            content_type=content_type, object_id=self.id, user=user
        ).first()
        if bookmark is None:
            bookmark = Bookmark(content_type=content_type, object_id=self.id, user=user)
            bookmark.save()
            self.save()

    def remove_bookmark(self, user):
        """remove bookmark to object"""
        content_type = ContentType.objects.get_for_model(self, for_concrete_model=True)
        bookmark = self.bookmarks.filter(
            content_type=content_type, object_id=self.id, user=user
        ).first()
        if bookmark is not None:
            bookmark.delete()
            self.save()

    def calculate_bookmark(self):
        self.bookmarked = (
            self.bookmarks.aggregate(total=models.Count("id"))["total"] or 0
        )

    def save(self, *args, **kwargs):
        self.calculate_bookmark()
        return super().save(*args, **kwargs)


class Review(models.Model):
    user = models.ForeignKey(
        User,
        related_name="ratings",
        on_delete=models.CASCADE,
        db_index=True,
    )
    object_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name=("review_objects"),
        help_text=_("reviewed object type"),
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=False,
        help_text=_("reviewed object ID"),
    )
    content_object = GenericForeignKey(
        ct_field="object_type",
        fk_field="object_id",
    )
    target_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name=("review_targets"),
        help_text=_("target object type"),
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("target object ID"),
    )
    target_object = GenericForeignKey(
        ct_field="target_type",
        fk_field="target_id",
    )

    rating = models.IntegerField(default=0, choices=[(x, f"{x}") for x in range(1, 6)])
    message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("message"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    objects = ReviewManager()

    class Meta:
        # TODO : FIX every user can give review once for each target object
        unique_together = ("user", "target_type", "id")
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")

    @cached_property
    def star_rating(self):
        rate = floor(self.rating)
        return rate

    @cached_property
    def star_rating_iterable(self):
        a = [0, 0, 0, 0, 0]
        for i, x in enumerate(range(self.star_rating)):
            a[i] = 1
        return a


class ReviewableModel(models.Model):
    RATING_STRING = {
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        "10": "ten",
    }
    rating = models.DecimalField(
        max_digits=4,
        default=Decimal("0.00"),
        decimal_places=2,
        editable=False,
        verbose_name=_("rating"),
    )
    review_count = models.IntegerField(
        default=0,
        verbose_name=_("review count"),
    )
    reviews = GenericRelation(
        Review,
        content_type_field="object_type",
        object_id_field="object_id",
    )
    review = models.JSONField(
        editable=False,
        verbose_name=_("review"),
        help_text=_('JSON fields contains {"one": 1, "two":1, "three":1}'),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    @cached_property
    def star_rating(self):
        rate = floor(self.rating)
        return rate

    @cached_property
    def star_rating_iterable(self):
        a = [0, 0, 0, 0, 0]
        for i, x in enumerate(range(self.star_rating)):
            a[i] = 1
        return a

    def get_reviews(self, rating=None):
        extra_filter = {}
        if rating:
            extra_filter.update({"rating": rating})
            reviews = self.reviews.filter(**extra_filter)
        else:
            reviews = self.reviews.all()
        return reviews

    def calculate_review(self):
        reviews = self.get_reviews().values("rating").annotate(total=models.Count("id"))
        self.review = {
            self.RATING_STRING.get(str(obj["rating"]), obj["rating"]): obj["total"]
            for obj in reviews
        }

    def count_rating(self):
        self.review_count = self.reviews.count()

    def calculate_rating(self):
        self.rating = self.reviews.aggregate(models.Avg("rating"))[
            "rating__avg"
        ] or Decimal("0.00")

    def add_review(self, user, rating, message=None, target_object=None):
        """add review to object"""
        object_type = ContentType.objects.get_for_model(self, for_concrete_model=True)
        target_type = None
        target_id = None
        if target_object:
            target_type = ContentType.objects.get_for_model(
                target_object, for_concrete_model=True
            )
            target_id = target_object.id
        review = Review(
            object_type=object_type,
            object_id=self.id,
            user=user,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            message=message,
        )
        review.save()
        return review

    def save(self, *args, **kwargs):
        self.calculate_review()
        self.calculate_rating()
        self.count_rating()
        return super().save(*args, **kwargs)


class Flag(models.Model):
    SPAM = "spam"
    SEXUAL = "sexual"
    HATE = "hate"
    VIOLENCE = "violence"
    BULLYING = "bullying"
    HOAX = "hoax"
    SCAM = "scam"
    ILLEGAL = "illegal"
    OTHERS = "others"

    FLAG_TYPES = (
        (SPAM, _("spam")),
        (SEXUAL, _("sexual")),
        (HATE, _("hate")),
        (VIOLENCE, _("violence")),
        (BULLYING, _("bullying")),
        (HOAX, _("hoax")),
        (SCAM, _("scam")),
        (ILLEGAL, _("illegal")),
        (OTHERS, _("others")),
    )
    user = models.ForeignKey(
        User,
        related_name="flags",
        on_delete=models.CASCADE,
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    value = models.CharField(
        max_length=25,
        default=SPAM,
        choices=FLAG_TYPES,
        verbose_name=_("value"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    objects = ReactionManager()
    message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("message"),
    )

    class Meta:
        unique_together = ("user", "content_type", "id")
        verbose_name = _("Flag")
        verbose_name_plural = _("Flags")

    def __str__(self):
        return '%s %s "%s"' % (self.user, self.get_value_display(), self.content_object)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.uid,)


class FlaggableModel(models.Model):

    flag = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("flag"),
        help_text=_('JSON fields contains {"spam": 1, "hoax":2, "bullying":3}'),
    )

    flags = GenericRelation(Flag)

    class Meta:
        abstract = True

    def get_flags(self, flag=None):
        extra_filter = {}
        if flag:
            extra_filter.update({"value": flag})
            flags = self.flags.filter(**extra_filter)
        else:
            flags = self.flags.all()
        return flags

    def calculate_flag(self):
        flags = self.get_flags().values("value").annotate(total=models.Count("id"))
        self.flag = {obj["value"]: obj["total"] for obj in flags}

    def save(self, *args, **kwargs):
        self.calculate_flag()
        return super().save(*args, **kwargs)

    def add_flag(self, user, value, message=None):
        """add flag to object"""
        content_type = ContentType.objects.get_for_model(self, for_concrete_model=True)
        try:
            flag = Flag.objects.get(
                content_type=content_type, object_id=self.id, user=user
            )
            flag.value = value
            flag.message = message
            flag.save()
        except Flag.DoesNotExist:
            flag = Flag(
                content_type=content_type,
                object_id=self.id,
                user=user,
                value=value,
                message=message,
            )
            flag.save()
        return flag


@receiver(post_save, sender=Flag)
def recalculate_object_flag(sender, instance, **kwargs):
    if instance.content_object is not None:
        instance.content_object.save()


@receiver(post_save, sender=Reaction)
def recalculate_object_reaction(sender, instance, **kwargs):
    if instance.content_object is not None:
        instance.content_object.save()
    # TODO send notification to user when reaction created


@receiver(post_delete, sender=Reaction)
def recalculate_object_reaction_remove(sender, instance, **kwargs):
    if instance.content_object is not None:
        instance.content_object.save()


@receiver(post_save, sender=Review)
def recalculate_object_rating(sender, instance, **kwargs):
    if instance.content_object is not None:
        instance.content_object.save()
    # TODO send notification to user when review created


@receiver(post_delete, sender=Review)
def recalculate_object_rating_remove(sender, instance, **kwargs):
    if instance.content_object is not None:
        instance.content_object.save()
    # TODO send notification to user when review created
