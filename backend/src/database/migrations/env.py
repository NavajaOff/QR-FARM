from __future__ import with_statement
import logging
import os
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    # Search for .env file in project root
    # env.py is at: backend/src/database/migrations/env.py
    # .env is at: project_root/.env
    env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not available, continue without it
    pass

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# Build database URL from environment variables
# This allows running migrations both from Docker (DB_HOST=mysql) and locally (DB_HOST=localhost)
def _build_database_url() -> str:
    """Build SQLAlchemy database URL from environment variables."""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'gestion_ganadera')
    db_port = os.getenv('DB_PORT', '3306')

    # Log for debugging
    logger.info(f"DB_HOST: {db_host}, DB_USER: {db_user}, DB_PASSWORD set: {bool(db_password)}, DB_NAME: {db_name}, DB_PORT: {db_port}")

    # Construct URL: mysql+mysqlconnector://user:password@host:port/database
    url = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    logger.info(f"Database URL constructed from environment variables (host: {db_host})")
    return url

# Override sqlalchemy.url with environment-based URL
database_url = _build_database_url()
config.set_main_option('sqlalchemy.url', database_url)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # handle non-ASCII characters in Python 2
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()