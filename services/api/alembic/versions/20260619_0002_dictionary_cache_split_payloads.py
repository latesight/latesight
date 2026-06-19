"""Split dictionary cache payloads into provider and DeepSeek data.

Revision ID: 20260619_0002
Revises: 20260619_0001
Create Date: 2026-06-19 22:15:00

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260619_0002"
down_revision = "20260619_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("dictionary_cache", "response", new_column_name="provider_response")
    op.add_column(
        "dictionary_cache",
        sa.Column(
            "deepseek_response",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("dictionary_cache", "deepseek_response")
    op.alter_column("dictionary_cache", "provider_response", new_column_name="response")
