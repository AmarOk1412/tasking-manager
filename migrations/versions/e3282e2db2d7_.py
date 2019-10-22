"""empty message

Revision ID: e3282e2db2d7
Revises: 068674f06b0f
Create Date: 2019-06-17 18:34:11.058440

"""
from alembic import op
import sqlalchemy as sa
from server.models.postgis.statuses import TeamVisibility, OrganisationVisibility


# revision identifiers, used by Alembic.
revision = "e3282e2db2d7"
down_revision = "d2e18f0f34a9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organisations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("logo", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column(
            "visibility",
            sa.Integer(),
            nullable=False,
            server_default=str(OrganisationVisibility.SECRET.value),
        ),
        sa.PrimaryKeyConstraint("id")
        # ,
        # sa.UniqueConstraint("name"),
    )
    op.create_table(
        "organisation_admins",
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organisation_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("logo", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("invite_only", sa.Boolean(), nullable=False),
        sa.Column(
            "visibility",
            sa.Integer(),
            nullable=False,
            server_default=str(TeamVisibility.SECRET.value),
        ),
        sa.ForeignKeyConstraint(
            ["organisation_id"], ["organisations.id"], name="fk_organisations"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project_teams",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("team_id", "project_id"),
    )
    op.create_table(
        "team_members",
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("function", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], name="fk_teams"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_users"),
        sa.PrimaryKeyConstraint("team_id", "user_id"),
    )
    op.add_column("projects", sa.Column("organisation_id", sa.Integer(), nullable=True))
    op.alter_column(
        "projects", "task_creation_mode", existing_type=sa.INTEGER(), nullable=False
    )
    op.create_index(
        op.f("ix_projects_organisation_id"),
        "projects",
        ["organisation_id"],
        unique=False,
    )
    op.drop_index("ix_projects_organisation_tag", table_name="projects")
    op.create_foreign_key(
        "fk_organisations", "projects", "organisations", ["organisation_id"], ["id"]
    )
    op.drop_column("projects", "organisation_tag")
    op.drop_index(
        "idx_task_validation_mapper_status_composite",
        table_name="task_invalidation_history",
    )
    op.create_index(
        "idx_task_validation_mapper_status_composite",
        "task_invalidation_history",
        ["mapper_id", "is_closed"],
        unique=False,
    )

    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("logo", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "campaign_projects",
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
    )
    op.create_table(
        "campaign_organisations",
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.Column("organisation_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["organisation_id"], ["organisations.id"]),
    )
    op.drop_index(
        "idx_task_validation_mapper_status_composite",
        table_name="task_invalidation_history",
    )
    op.create_index(
        "idx_task_validation_mapper_status_composite",
        "task_invalidation_history",
        ["invalidator_id", "is_closed"],
        unique=False,
    )

    conn = op.get_bind()

    # Content migration: Migrate the campaigns tag in campaigns table
    campaigns = conn.execute(
        "select campaigns from tags where campaigns is not null"
    ).fetchall()

    # This will be used to consolidate the data in tags table
    dictionaries = {"HOTOSM": {"HOTOSM", "HOT-OSM"}, "ABC": {"abc", "ABc"}}

    for campaign in campaigns:
        result = campaign[0]
        for campaign_key, campaign_values in dictionaries.items():
            if campaign[0] in campaign_values:
                result = campaign_key

        query = "insert into campaigns(name) values('" + result + "')"
        op.execute(query)

    # Migrate the organisations tag in organisations table
    organisations = conn.execute(
        "select organisations from tags where organisations is not null"
    ).fetchall()

    # This will be used to consolidate the data in the tags table
    org_dictionaries = {"HOTOSM": {"HOTOSM", "HOT-OSM"}, "ABC": {"abc", "ABc"}}

    for org in organisations:
        result = org[0]
        if result.startswith("'") or result.startswith('"'):
            print(result)
            result = result[1 : len(result) - 1]
        for org_key, org_values in org_dictionaries.items():
            if result in org_values:
                result = org_key

        query = "insert into organisations(name) values ('" + result + "')"
        op.execute(query)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "idx_task_validation_mapper_status_composite",
        table_name="task_invalidation_history",
    )
    op.create_index(
        "idx_task_validation_mapper_status_composite",
        "task_invalidation_history",
        ["invalidator_id", "is_closed"],
        unique=False,
    )
    op.add_column(
        "projects",
        sa.Column("organisation_tag", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint("fk_organisations", "projects", type_="foreignkey")
    op.create_index(
        "ix_projects_organisation_tag", "projects", ["organisation_tag"], unique=False
    )
    op.drop_index(op.f("ix_projects_organisation_id"), table_name="projects")
    op.alter_column(
        "projects", "task_creation_mode", existing_type=sa.INTEGER(), nullable=True
    )
    op.drop_column("projects", "organisation_id")
    op.drop_table("team_members")
    op.drop_table("project_teams")
    op.drop_table("teams")
    op.drop_table("campaign_organisations")
    op.drop_table("campaign_projects")
    op.drop_table("campaigns")
    op.drop_table("organisation_admins")
    op.drop_table("organisations")

    # ### end Alembic commands ###
