"""Migración Multi-Tenant: Tabla tenants y tenant_id en todas las tablas

Revision ID: 004_multi_tenant
Revises: 12673429ef47
Create Date: 2025-11-25
"""
from alembic import op
import sqlalchemy as sa

revision = '004_multi_tenant'
down_revision = '12673429ef47'
branch_labels = None
depends_on = None


def _crear_tabla_tenants(op, tables):
    """Crea la tabla tenants si no existe."""
    if 'tenants' not in tables:
        op.create_table(
            'tenants',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('nombre', sa.String(255), nullable=False),
            sa.Column('codigo_tenant', sa.String(100), nullable=False, unique=True),
            sa.Column('estado', sa.Enum('activo', 'inactivo', name='estado_tenant'), 
                      nullable=False, server_default='activo'),
            sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.current_timestamp()),
            sa.Column('fecha_actualizacion', sa.DateTime, server_default=sa.func.current_timestamp(), 
                      onupdate=sa.func.current_timestamp())
        )

def _agregar_tenant_id_a_tablas(op, inspector, tables):
    """Agrega tenant_id a las tablas si no existe."""
    tablas_con_tenant = ['usuarios', 'personas', 'ganado', 'potrero', 'vacunacion', 'qr']
    for table_name in tablas_con_tenant:
        if table_name not in tables:
            continue
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        if 'tenant_id' in columns:
            continue
        ondelete_action = 'SET NULL' if table_name in ['usuarios', 'personas'] else 'CASCADE'
        op.add_column(table_name, sa.Column('tenant_id', sa.Integer, 
                                           sa.ForeignKey('tenants.id', ondelete=ondelete_action), 
                                           nullable=True))

def _asignar_tenant_por_defecto(op):
    """Crea y asigna tenant por defecto a registros existentes."""
    op.execute("""
        INSERT IGNORE INTO tenants (nombre, codigo_tenant, estado)
        VALUES ('Tenant Por Defecto', 'default', 'activo')
    """)
    
    op.execute("""
        UPDATE usuarios u
        SET u.tenant_id = (SELECT id FROM tenants WHERE codigo_tenant = 'default' LIMIT 1)
        WHERE u.tenant_id IS NULL
    """)

def _asignar_tenant_id_relaciones(op):
    """Asigna tenant_id basado en relaciones existentes."""
    op.execute("""
        UPDATE personas p
        INNER JOIN usuarios u ON p.id = u.id_persona
        SET p.tenant_id = u.tenant_id
        WHERE p.tenant_id IS NULL AND u.tenant_id IS NOT NULL
    """)
    
    op.execute("""
        UPDATE ganado g
        INNER JOIN personas p ON g.id_persona = p.id
        SET g.tenant_id = p.tenant_id
        WHERE g.tenant_id IS NULL AND p.tenant_id IS NOT NULL
    """)
    
    op.execute("""
        UPDATE potrero po
        INNER JOIN personas p ON po.responsable_persona_id = p.id
        SET po.tenant_id = p.tenant_id
        WHERE po.tenant_id IS NULL AND p.tenant_id IS NOT NULL
    """)
    
    op.execute("""
        UPDATE vacunacion v
        INNER JOIN ganado g ON v.id_animal = g.id
        SET v.tenant_id = g.tenant_id
        WHERE v.tenant_id IS NULL AND g.tenant_id IS NOT NULL
    """)
    
    op.execute("""
        UPDATE qr q
        INNER JOIN ganado g ON q.id_ganado = g.id
        SET q.tenant_id = g.tenant_id
        WHERE q.tenant_id IS NULL AND g.tenant_id IS NOT NULL
    """)

def _asignar_tenant_defecto_restantes(op):
    """Asigna tenant por defecto a registros sin tenant asignado."""
    tablas = ['ganado', 'potrero', 'vacunacion', 'qr']
    for tabla in tablas:
        op.execute(f"""
            UPDATE {tabla} SET tenant_id = (SELECT id FROM tenants WHERE codigo_tenant = 'default' LIMIT 1)
            WHERE tenant_id IS NULL
        """)

def _hacer_tenant_id_not_null(op, inspector, tables):
    """Hace tenant_id NOT NULL después de migrar datos."""
    tablas_not_null = ['ganado', 'potrero', 'vacunacion', 'qr']
    for table_name in tablas_not_null:
        if table_name not in tables:
            continue
        columns = inspector.get_columns(table_name)
        tenant_col = next((col for col in columns if col['name'] == 'tenant_id'), None)
        if tenant_col and tenant_col['nullable']:
            op.alter_column(table_name, 'tenant_id',
                            existing_type=sa.Integer(),
                            nullable=False)

def _actualizar_tabla_roles(op, inspector, tables):
    """Actualiza la tabla roles con nivel y permisos."""
    if 'roles' not in tables:
        return
    roles_columns = [col['name'] for col in inspector.get_columns('roles')]
    if 'nivel' not in roles_columns:
        op.add_column('roles', sa.Column('nivel', sa.Enum('global', 'tenant', name='nivel_rol'), 
                                         server_default='tenant'))
    if 'permisos' not in roles_columns:
        op.add_column('roles', sa.Column('permisos', sa.JSON, nullable=True))
    
    op.execute("""
        UPDATE roles SET nivel = 'tenant' WHERE rol IN ('admin', 'usuario')
    """)
    
    op.execute("""
        INSERT INTO roles (id, rol, descripcion, nivel, permisos)
        VALUES (3, 'super_admin', 'Administrador global del sistema', 'global', '{}')
        ON DUPLICATE KEY UPDATE nivel = 'global'
    """)

def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    _crear_tabla_tenants(op, tables)
    _agregar_tenant_id_a_tablas(op, inspector, tables)
    _asignar_tenant_por_defecto(op)
    _asignar_tenant_id_relaciones(op)
    _asignar_tenant_defecto_restantes(op)
    _hacer_tenant_id_not_null(op, inspector, tables)
    _actualizar_tabla_roles(op, inspector, tables)


def downgrade():
    # Eliminar columnas de tenant_id
    op.drop_column('qr', 'tenant_id')
    op.drop_column('vacunacion', 'tenant_id')
    op.drop_column('potrero', 'tenant_id')
    op.drop_column('ganado', 'tenant_id')
    op.drop_column('personas', 'tenant_id')
    op.drop_column('usuarios', 'tenant_id')
    
    # Eliminar columnas de roles
    op.drop_column('roles', 'permisos')
    op.drop_column('roles', 'nivel')
    
    # Eliminar tabla tenants
    op.drop_table('tenants')

