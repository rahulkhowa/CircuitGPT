"""add_subject_id_and_resource_type_to_uploads

Revision ID: fb64d07d4bb2
Revises: 23cc71bfb0da
Create Date: 2026-08-20 11:40:28.156709+00:00

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fb64d07d4bb2'
down_revision: str | None = '23cc71bfb0da'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Define the new enum
resourcetype_enum = sa.Enum(
    'notes', 'videos', 'lab_manuals', 'books', 'pyqs',
    name='resourcetype',
)


def upgrade() -> None:
    # 1. Drop old uploadtype enum column
    op.drop_column('uploads', 'is_indexed')
    op.drop_column('uploads', 'transcript')
    op.drop_column('uploads', 'file_type')

    # 2. Drop old enum type if it exists
    op.execute("DROP TYPE IF EXISTS uploadtype")

    # 3. Create new enum type
    resourcetype_enum.create(op.get_bind(), checkfirst=True)

    # 4. Add new columns — nullable first, then set default + make non-null
    op.add_column('uploads', sa.Column('subject_id', sa.String(length=100), nullable=True))
    op.add_column('uploads', sa.Column(
        'resource_type',
        sa.Enum('notes', 'videos', 'lab_manuals', 'books', 'pyqs', name='resourcetype'),
        nullable=True,
    ))
    op.add_column('uploads', sa.Column('mime_type', sa.String(length=128), nullable=True))

    # 5. Backfill defaults for any existing rows
    op.execute("UPDATE uploads SET subject_id = 'unknown' WHERE subject_id IS NULL")
    op.execute("UPDATE uploads SET resource_type = 'notes' WHERE resource_type IS NULL")
    op.execute("UPDATE uploads SET mime_type = 'application/octet-stream' WHERE mime_type IS NULL")

    # 6. Now enforce NOT NULL
    op.alter_column('uploads', 'subject_id', nullable=False)
    op.alter_column('uploads', 'resource_type', nullable=False)
    op.alter_column('uploads', 'mime_type', nullable=False)

    # 7. Add indexes
    op.create_index(op.f('ix_uploads_resource_type'), 'uploads', ['resource_type'], unique=False)
    op.create_index(op.f('ix_uploads_subject_id'), 'uploads', ['subject_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_uploads_subject_id'), table_name='uploads')
    op.drop_index(op.f('ix_uploads_resource_type'), table_name='uploads')
    op.drop_column('uploads', 'mime_type')
    op.drop_column('uploads', 'resource_type')
    op.drop_column('uploads', 'subject_id')

    # Restore old enum and column
    old_enum = postgresql.ENUM('PDF', 'VIDEO', 'AUDIO', 'IMAGE', 'OTHER', name='uploadtype', create_type=False)
    op.execute("CREATE TYPE uploadtype AS ENUM ('PDF', 'VIDEO', 'AUDIO', 'IMAGE', 'OTHER')")
    op.add_column('uploads', sa.Column('file_type', old_enum, autoincrement=False, nullable=True))
    op.execute("UPDATE uploads SET file_type = 'OTHER'")
    op.alter_column('uploads', 'file_type', nullable=False)
    op.add_column('uploads', sa.Column('transcript', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('uploads', sa.Column('is_indexed', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.execute("UPDATE uploads SET is_indexed = FALSE")
    op.alter_column('uploads', 'is_indexed', nullable=False)
