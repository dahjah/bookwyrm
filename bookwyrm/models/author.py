""" database schema for info about authors """
import re
from typing import Tuple, Any

from django.db import models
import pgtrigger

from bookwyrm import activitypub
from bookwyrm.settings import DOMAIN
from bookwyrm.utils.db import format_trigger

from .book import BookDataModel
from . import fields


class Author(BookDataModel):
    """basic biographic info"""

    wikipedia_link = fields.CharField(
        max_length=255, blank=True, null=True, deduplication_field=True
    )
    isni = fields.CharField(
        max_length=255, blank=True, null=True, deduplication_field=True
    )
    gutenberg_id = fields.CharField(
        max_length=255, blank=True, null=True, deduplication_field=True
    )
    isfdb = fields.CharField(
        max_length=255, blank=True, null=True, deduplication_field=True
    )

    website = fields.CharField(
        max_length=255, blank=True, null=True, deduplication_field=True
    )
    # idk probably other keys would be useful here?
    born = fields.DateTimeField(blank=True, null=True)
    died = fields.DateTimeField(blank=True, null=True)
    name = fields.CharField(max_length=255)
    aliases = fields.ArrayField(
        models.CharField(max_length=255), blank=True, default=list
    )
    bio = fields.HtmlField(null=True, blank=True)

    def save(self, *args: Tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """normalize isni format"""
        if self.isni:
            self.isni = re.sub(r"\s", "", self.isni)

        return super().save(*args, **kwargs)

    @property
    def isni_link(self):
        """generate the url from the isni id"""
        clean_isni = re.sub(r"\s", "", self.isni)
        return f"https://isni.org/isni/{clean_isni}"

    @property
    def openlibrary_link(self):
        """generate the url from the openlibrary id"""
        return f"https://openlibrary.org/authors/{self.openlibrary_key}"

    @property
    def isfdb_link(self):
        """generate the url from the isni id"""
        return f"https://www.isfdb.org/cgi-bin/ea.cgi?{self.isfdb}"

    def get_remote_id(self):
        """editions and works both use "book" instead of model_name"""
        return f"https://{DOMAIN}/author/{self.id}"

    class Meta:
        """sets up indexes and triggers"""

        triggers = [
            pgtrigger.Trigger(
                name="reset_search_vector_on_author_edit",
                when=pgtrigger.After,
                operation=pgtrigger.UpdateOf("name"),
                func=format_trigger(
                    """WITH updated_books AS (
                         SELECT book_id
                         FROM bookwyrm_book_authors
                         WHERE author_id = new.id
                    )
                    UPDATE bookwyrm_book
                    SET search_vector = ''
                    FROM updated_books
                    WHERE id = updated_books.book_id;
                    RETURN new;
                """
                ),
            )
        ]

    activity_serializer = activitypub.Author
