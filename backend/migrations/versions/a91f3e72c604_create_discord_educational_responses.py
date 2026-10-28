"""Create Discord educational responses table.

Revision ID: a91f3e72c604
Revises: c33e95978820
"""

from alembic import op
import sqlalchemy as sa


revision = "a91f3e72c604"
down_revision = "c33e95978820"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "discord_educational_responses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("clave_unica", sa.String(64), nullable=False),
        sa.Column("guild_id", sa.String(32), nullable=False),
        sa.Column("channel_id", sa.String(32), nullable=False),
        sa.Column("source_message_id", sa.String(32), nullable=False),
        sa.Column("pregunta_original", sa.Text(), nullable=False),
        sa.Column("respuesta", sa.Text(), nullable=True),
        sa.Column("tema", sa.String(100), nullable=True),
        sa.Column(
            "estado",
            sa.String(30),
            nullable=False,
            server_default="borrador",
        ),
        sa.Column("discord_message_id", sa.String(32), nullable=True),
        sa.Column("error_detalle", sa.Text(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("publicado_en", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "clave_unica",
            name="uq_discord_educational_clave",
        ),
        sa.UniqueConstraint(
            "guild_id",
            "channel_id",
            "source_message_id",
            name="uq_discord_educational_origen",
        ),
    )


def downgrade():
    op.drop_table("discord_educational_responses")
