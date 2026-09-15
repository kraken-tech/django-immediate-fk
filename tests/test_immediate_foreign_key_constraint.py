import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import connection
from django.db.models.constraints import Deferrable, UniqueConstraint
from django.db.utils import ProgrammingError
from django_subatomic import db
from django_integrity.constraints import set_deferred, set_immediate

from .books.models import Author, Book, Editor, Publisher
from django_immediate_fk import ForeignKeyConstraint


@pytest.mark.django_db(transaction=True)
def test_immediate_constraint_forwards_migration(migrator):
    """
    Test replacing a deferred constraint with an immediate constraint.

    After migration 0001 is applied, the constraint is deferred, so
    the `IntegrityError` happens in `transaction.__exit__`.
    After migration 0002 is applied, the constraint is immediate, so
    the `IntegrityError` happens within the `transaction` block.
    """
    initial_state = migrator.apply_initial_migration(("books", "0001_initial"))
    Book = initial_state.apps.get_model("books", "Book")
    Editor = initial_state.apps.get_model("books", "Editor")
    Publisher = initial_state.apps.get_model("books", "Publisher")

    editor = Editor.objects.create(name="Editor")
    publisher = Publisher.objects.create(name="Publisher")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=-1, editor_id=editor.pk, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)

    state = migrator.apply_tested_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Book = state.apps.get_model("books", "Book")

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1, editor_id=editor.pk, publisher_id=publisher.pk)


@pytest.mark.django_db(transaction=True)
def test_immediate_constraint_reverse_migration(migrator):
    """
    Test replacing an immediate constraint with a deferred constraint.

    After migration 0002 is applied, the constraint is immediate, so
    the `IntegrityError` happens within the `transaction` block.
    After rolling back to 0001 , the constraint is deferred, so the
    `IntegrityError` happens in `transaction.__exit__`.
    """
    initial_state = migrator.apply_initial_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Book = initial_state.apps.get_model("books", "Book")
    Editor = initial_state.apps.get_model("books", "Editor")
    Publisher = initial_state.apps.get_model("books", "Publisher")

    editor = Editor.objects.create(name="Editor")
    publisher = Publisher.objects.create(name="Publisher")

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=-1, editor_id=editor.pk, publisher_id=publisher.pk)

    state = migrator.apply_tested_migration(("books", "0001_initial"))
    Book = state.apps.get_model("books", "Book")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=-1, editor_id=editor.pk, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.django_db(transaction=True)
def test_not_deferrable_constraint_forwards_migration(migrator):
    """
    Test replacing a deferred constraint with a not deferable constraint.

    After migration 0001 is applied, the constraint is deferred, so
    the `IntegrityError` happens in `transaction.__exit__`.
    After migration 0002 is applied, the constraint is not deferrable,
    so the `IntegrityError` happens within the `transaction` block.
    """
    initial_state = migrator.apply_initial_migration(("books", "0001_initial"))
    Author = initial_state.apps.get_model("books", "Author")
    Book = initial_state.apps.get_model("books", "Book")
    Editor = initial_state.apps.get_model("books", "Editor")

    author = Author.objects.create(name="Author")
    editor = Editor.objects.create(name="Editor")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=editor.pk, publisher_id=-1)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)

    state = migrator.apply_tested_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Book = state.apps.get_model("books", "Book")

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=author.pk, editor_id=editor.pk, publisher_id=-1)


@pytest.mark.django_db(transaction=True)
def test_not_deferrable_constraint_reverse_migration(migrator):
    """
    Test replacing an immediate constraint with a deferred constraint.

    After migration 0002 is applied, the constraint is not deferrable,
    so the `IntegrityError` happens within the `transaction` block.
    After rolling back to 0001 , the constraint is deferred, so the
    `IntegrityError` happens in `transaction.__exit__`.
    """
    initial_state = migrator.apply_initial_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Author = initial_state.apps.get_model("books", "Author")
    Book = initial_state.apps.get_model("books", "Book")
    Editor = initial_state.apps.get_model("books", "Editor")

    author = Author.objects.create(name="Author")
    editor = Editor.objects.create(name="Editor")

    with db.transaction():
        with pytest.raises(IntegrityError):
            Book.objects.create(author_id=author.pk, editor_id=editor.pk, publisher_id=-1)

    state = migrator.apply_tested_migration(("books", "0001_initial"))
    Book = state.apps.get_model("books", "Book")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=editor.pk, publisher_id=-1)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.django_db(transaction=True)
def test_deferred_constraint_forwards_migration(migrator):
    """
    Test replacing Django's deferred constraint with an explicit deferred constraint.

    In both cases, the constraint is deferred, so the `IntegrityError`
    happens in `transaction.__exit__`.
    """
    initial_state = migrator.apply_initial_migration(("books", "0001_initial"))
    Author = initial_state.apps.get_model("books", "Author")
    Book = initial_state.apps.get_model("books", "Book")
    Publisher = initial_state.apps.get_model("books", "Publisher")

    author = Author.objects.create(name="Author")
    publisher = Publisher.objects.create(name="Publisher")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=-1, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)

    state = migrator.apply_tested_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Book = state.apps.get_model("books", "Book")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=-1, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.django_db(transaction=True)
def test_deferred_constraint_reverse_migration(migrator):
    """
    Test replacing an explicit deferred constraint with Django's implicit deferred constraint.

    In both cases, the constraint is deferred, so the `IntegrityError`
    happens in `transaction.__exit__`.
    """
    initial_state = migrator.apply_initial_migration(("books", "0002_alter_book_foreign_key_constraints"))
    Author = initial_state.apps.get_model("books", "Author")
    Book = initial_state.apps.get_model("books", "Book")
    Publisher = initial_state.apps.get_model("books", "Publisher")

    author = Author.objects.create(name="Author")
    publisher = Publisher.objects.create(name="Publisher")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=-1, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)

    state = migrator.apply_tested_migration(("books", "0001_initial"))
    Book = state.apps.get_model("books", "Book")

    transaction = db.transaction()
    transaction.__enter__()
    Book.objects.create(author_id=author.pk, editor_id=-1, publisher_id=publisher.pk)
    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SET DEFERRED is not supported by SQLite: https://www.sqlite.org/foreignkeys.html#fk_unsupported",
)
@pytest.mark.django_db(transaction=True)
def test_set_deferred_not_deferrable_foreign_key():
    with db.transaction():
        with pytest.raises(ProgrammingError):
            set_deferred(names=("books_book_publisher_not_deferrable",), using="default")


@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SET IMMEDIATE is not supported by SQLite: https://www.sqlite.org/foreignkeys.html#fk_unsupported",
)
@pytest.mark.django_db(transaction=True)
def test_set_immediate_not_deferrable_foreign_key():
    author = Author.objects.create(name="Author")
    editor = Editor.objects.create(name="Editor")

    with db.transaction():
        set_immediate(names=("books_book_publisher_not_deferrable",), using="default")

        with pytest.raises(IntegrityError):
            Book.objects.create(author=author, editor=editor, publisher_id=-1)


@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SET DEFERRED is not supported by SQLite: https://www.sqlite.org/foreignkeys.html#fk_unsupported",
)
@pytest.mark.django_db(transaction=True)
def test_set_deferred_immediate_foreign_key():
    editor = Editor.objects.create(name="Editor")
    publisher = Publisher.objects.create(name="Publisher")

    transaction = db.transaction()
    transaction.__enter__()

    set_deferred(names=("books_book_author_immediate",), using="default")
    Book.objects.create(author_id=-1, editor=editor, publisher=publisher)

    with pytest.raises(IntegrityError):
        transaction.__exit__(None, None, None)


@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SET IMMEDIATE is not supported by SQLite: https://www.sqlite.org/foreignkeys.html#fk_unsupported",
)
@pytest.mark.django_db(transaction=True)
def test_set_immediate_deferrable_foreign_key():
    author = Author.objects.create(name="Author")
    publisher = Publisher.objects.create(name="Publisher")

    with db.transaction():
        set_immediate(names=("books_book_editor_deferred",), using="default")
        with pytest.raises(IntegrityError):
            Book.objects.create(author=author, editor_id=-1, publisher=publisher)


@pytest.mark.django_db
def test_immediate_foreign_key_full_clean():
    editor = Editor.objects.create(name="Editor")
    publisher = Publisher.objects.create(name="Publisher")
    hobbit = Book(title="The Hobbit", author_id=-1, editor=editor, publisher=publisher)

    with db.transaction():
        with pytest.raises(ValidationError):
            hobbit.full_clean()


def test_eq():
    immediate = ForeignKeyConstraint(name="name", field="author", deferrable=Deferrable.IMMEDIATE)
    deferred = ForeignKeyConstraint(name="name", field="author", deferrable=Deferrable.DEFERRED)
    not_deferrable = ForeignKeyConstraint(name="name", field="author", deferrable=None)

    assert immediate == ForeignKeyConstraint(name="name", field="author", deferrable=Deferrable.IMMEDIATE)
    assert deferred == ForeignKeyConstraint(name="name", field="author", deferrable=Deferrable.DEFERRED)
    assert not_deferrable == ForeignKeyConstraint(name="name", field="author", deferrable=None)

    assert immediate != deferred
    assert immediate != not_deferrable
    assert deferred != not_deferrable

    assert immediate != ForeignKeyConstraint(name="other", field="author", deferrable=Deferrable.IMMEDIATE)
    assert immediate != ForeignKeyConstraint(name="name", field="other", deferrable=Deferrable.IMMEDIATE)
    assert immediate != UniqueConstraint(name="name", fields=["author"], deferrable=Deferrable.IMMEDIATE)


@pytest.mark.parametrize("deferrable", (None, Deferrable.IMMEDIATE, Deferrable.DEFERRED))
def test_deconstruct(deferrable):
    constraint = ForeignKeyConstraint(name="name", field="author", deferrable=deferrable)

    assert constraint.deconstruct() == (
        "django_immediate_fk.ForeignKeyConstraint",
        (),
        {"name": "name", "field": "author", "deferrable": deferrable},
    )
