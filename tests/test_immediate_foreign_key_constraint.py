import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.constraints import UniqueConstraint
from django_subatomic import db

from .books.models import Author, Book
from django_immediate_fk import ImmediateDeferrableFKConstraint


@pytest.mark.django_db(transaction=True)
def test_forwards_migration(migrator):
    """
    Test replacing a deferred constraint with an immediate constraint.

    After migration 0001 is applied, the constraint is deferred, so
    the `IntegrityError` happens in `transaction.__exit__`.
    After migration 0002 is applied, the constraint is immediate, so
    the `IntegrityError` happens within the `transaction` block.
    """
    migrator.apply_initial_migration(("books", "0001_initial"))

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=-1)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)

    migrator.apply_tested_migration(("books", "0002_alter_book_author_book_books_book_author_immediate"))

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1)


@pytest.mark.django_db(transaction=True)
def test_reverse_migration(migrator):
    """
    Test replacing an immediate constraint with a deferred constraint.

    After migration 0002 is applied, the constraint is immediate, so
    the `IntegrityError` happens within the `transaction` block.
    After rolling back to 0001 , the constraint is deferred, so the
    `IntegrityError` happens in `transaction.__exit__`.
    """
    migrator.apply_initial_migration(("books", "0002_alter_book_author_book_books_book_author_immediate"))

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1)

    migrator.apply_tested_migration(("books", "0001_initial"))

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=-1)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.django_db
def test_immediate_foreign_key_full_clean():
    hobbit = Book(title="The Hobbit", author_id=-1)

    with db.transaction():
        with pytest.raises(ValidationError):
            hobbit.full_clean()


def test_eq():
    constraint = ImmediateDeferrableFKConstraint(name="name", field="author")
    assert constraint == ImmediateDeferrableFKConstraint(name="name", field="author")
    assert constraint != ImmediateDeferrableFKConstraint(name="other", field="author")
    assert constraint != ImmediateDeferrableFKConstraint(name="name", field="other")
    assert constraint != UniqueConstraint(name="name", fields=["author"])
