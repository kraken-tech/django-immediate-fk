from django.db import models
from django.db.models.constraints import Deferrable

from django_immediate_fk import ForeignKeyConstraint


class Author(models.Model):
    name = models.CharField()


class Editor(models.Model):
    name = models.CharField()


class Publisher(models.Model):
    name = models.CharField()


class Book(models.Model):
    title = models.CharField()
    author = models.ForeignKey(Author, on_delete=models.DB_CASCADE, db_constraint=False)
    editor = models.ForeignKey(Editor, on_delete=models.DB_CASCADE, db_constraint=False)
    publisher = models.ForeignKey(Publisher, on_delete=models.DB_CASCADE, db_constraint=False)

    class Meta:
        constraints = [
            ForeignKeyConstraint(name="books_book_author_immediate", field="author", deferrable=Deferrable.IMMEDIATE),
            ForeignKeyConstraint(name="books_book_editor_deferred", field="editor", deferrable=Deferrable.DEFERRED),
            ForeignKeyConstraint(name="books_book_publisher_not_deferrable", field="publisher", deferrable=None),
        ]
