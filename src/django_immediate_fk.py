from django.db.backends.ddl_references import Columns, Statement, Table
from django.db.models.constraints import BaseConstraint, Deferrable
from django.db.utils import DEFAULT_DB_ALIAS


class ForeignKeyConstraint(BaseConstraint):
    CONSTRAINT_SQL = "FOREIGN KEY (%(column)s) REFERENCES %(to_table)s (%(to_column)s)%(on_delete_db)s%(deferrable)s"
    CREATE_SQL = f"ALTER TABLE %(table)s ADD CONSTRAINT %(name)s {CONSTRAINT_SQL}"

    def __init__(self, *, field, name, deferrable):
        self.field = field
        self.deferrable = deferrable
        super().__init__(name=name)

    def __eq__(self, other):
        if not isinstance(other, ForeignKeyConstraint):
            return super().__eq__(other)
        return self.name == other.name and self.field == other.field and self.deferrable == other.deferrable

    def constraint_sql(self, model, schema_editor):
        field = model._meta.get_field(self.field)

        column = Columns(model._meta.db_table, [field.column], schema_editor.quote_name)
        to_table = Table(field.target_field.model._meta.db_table, schema_editor.quote_name)
        to_column = Columns(
            field.target_field.model._meta.db_table,
            [field.target_field.column],
            schema_editor.quote_name,
        )

        constraint = self.CONSTRAINT_SQL % {
            "column": column,
            "to_table": to_table,
            "to_column": to_column,
            "on_delete_db": schema_editor._create_on_delete_sql(model, field),
            "deferrable": schema_editor._deferrable_constraint_sql(self.deferrable),
        }
        return schema_editor.sql_constraint % {
            "name": schema_editor.quote_name(self.name),
            "constraint": constraint,
        }

    def create_sql(self, model, schema_editor):
        field = model._meta.get_field(self.field)
        table = Table(model._meta.db_table, schema_editor.quote_name)
        column = Columns(model._meta.db_table, [field.column], schema_editor.quote_name)
        to_table = Table(field.target_field.model._meta.db_table, schema_editor.quote_name)
        to_column = Columns(
            field.target_field.model._meta.db_table,
            [field.target_field.column],
            schema_editor.quote_name,
        )
        return Statement(
            self.CREATE_SQL,
            table=table,
            name=schema_editor.quote_name(self.name),
            column=column,
            to_table=to_table,
            to_column=to_column,
            on_delete_db=schema_editor._create_on_delete_sql(model, field),
            deferrable=schema_editor._deferrable_constraint_sql(self.deferrable),
        )

    def remove_sql(self, model, schema_editor):
        return schema_editor._delete_fk_sql(model, self.name)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs["field"] = self.field
        kwargs["deferrable"] = self.deferrable
        return path, args, kwargs

    def validate(self, model, instance, exclude=None, using=DEFAULT_DB_ALIAS):
        # Delegate all validation to the `ForeignKey` referred to by `self.field`
        return True
