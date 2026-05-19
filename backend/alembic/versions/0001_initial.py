"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


severity = sa.Enum("INFO", "WARNING", "ERROR", "CRITICAL", "EXISTENTIAL", name="severity")


def upgrade() -> None:
    op.create_table(
        "errors",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", severity, nullable=False),
        sa.Column("subsystem", sa.String(length=60), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "templates",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("pattern", sa.String(length=400), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False, server_default="title"),
        sa.Column("severity_hint", severity, nullable=True),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_table(
        "vocab",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("slot", sa.String(length=40), nullable=False, index=True),
        sa.Column("value", sa.String(length=120), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("vocab")
    op.drop_table("templates")
    op.drop_table("errors")
    severity.drop(op.get_bind(), checkfirst=True)
