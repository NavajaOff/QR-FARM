<%!
    import re

    # extract table name from CREATE TABLE statement
    def extract_table_name(sql):
        match = re.search(r'CREATE TABLE `([^`]+)`', sql, re.IGNORECASE)
        return match.group(1) if match else None

    # extract column definitions from CREATE TABLE statement
    def extract_columns(sql):
        # Find the part between parentheses
        start = sql.find('(')
        end = sql.rfind(')')
        if start == -1 or end == -1:
            return []

        columns_part = sql[start+1:end]
        columns = []

        # Split by comma, but be careful with commas inside parentheses
        parts = []
        current_part = ""
        paren_depth = 0

        for char in columns_part:
            if char == '(':
                paren_depth += 1
                current_part += char
            elif char == ')':
                paren_depth -= 1
                current_part += char
            elif char == ',' and paren_depth == 0:
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char

        if current_part.strip():
            parts.append(current_part.strip())

        return parts
%>
<%!
    def render_column(column_sql):
        # Remove trailing comma and clean up
        column_sql = column_sql.strip().rstrip(',')
        return column_sql
%>
<%!
    def render_table(table_name, columns):
        return f"""CREATE TABLE `{table_name}` (
{chr(10).join(f"  {render_column(col)}" for col in columns)}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;"""
%>
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: str = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    % if operations:
    ${operations}
    % endif


def downgrade() -> None:
    % if operations:
    ${operations}
    % endif