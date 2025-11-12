import api from './api.js';
import axios, { isAxiosError } from 'axios';

export interface QrResourceRequest {
  endpoint: string;
  resourceId: string;
  signal?: AbortSignal;
}

export interface GanadoOwner {
  nombre: string | null;
  telefono: string | null;
  rol: string | null;
}

export interface GanadoPotrero {
  nombre: string | null;
  tipo_pasto: string | null;
  ultima_limpieza: string | null;
  fecha_ultimo_uso: string | null;
  proxima_limpieza: string | null;
  capacidad: number | null;
  estado: string | null;
}

export interface GanadoVacuna {
  id: string | null;
  nombre: string | null;
  fecha_aplicacion: string | null;
  proxima_dosis: string | null;
  estado: string | null;
  responsable: string | null;
}

export interface GanadoRevision {
  id: string | null;
  fecha: string | null;
  observaciones: string | null;
  resultado: string | null;
  veterinario: string | null;
}

export interface GanadoResource {
  id: string;
  nombre: string | null;
  raza: string | null;
  fecha_nacimiento: string | null;
  edad: number | null;
  sexo: string | null;
  estado: string | null;
  estado_salud: string | null;
  peso: number | null;
  codigo_qr: string | null;
  propietario: GanadoOwner;
  potrero: GanadoPotrero;
  vacunas: GanadoVacuna[];
  historial: GanadoRevision[];
}

const sanitizeEndpoint = (endpoint: string): string => {
  const trimmed = endpoint.trim();
  if (!trimmed) {
    throw createError('El endpoint para consultar el código QR es obligatorio.', 'QrEndpointError');
  }
  return trimmed;
};

const buildUrl = (endpoint: string, resourceId: string): string => {
  if (!resourceId) {
    throw createError('El identificador del código QR es obligatorio.', 'QrResourceIdError');
  }

  const sanitizedEndpoint = sanitizeEndpoint(endpoint);
  if (sanitizedEndpoint.includes('{id}')) {
    return sanitizedEndpoint.replace('{id}', encodeURIComponent(resourceId));
  }

  const normalizedEndpoint = sanitizedEndpoint.endsWith('/')
    ? sanitizedEndpoint.slice(0, sanitizedEndpoint.length - 1)
    : sanitizedEndpoint;

  return `${normalizedEndpoint}/${encodeURIComponent(resourceId)}`;
};

const createError = (message: string, name: string): Error => {
  const error = new Error(message);
  error.name = name;
  return error;
};

const mapAxiosError = (error: unknown): Error => {
  if (!isAxiosError(error)) return createError('No se pudo consultar el recurso asociado.', 'QrUnknownError');

  if (error.response) {
    const status = error.response.status;
    if (status === 404) {
      return createError('QR no reconocido. Verifica que el código exista.', 'QrNotFoundError');
    }
    if (status === 403) {
      return createError('No autorizado para consultar este recurso.', 'QrForbiddenError');
    }
    if (status >= 500) {
      return createError('Error del servidor al consultar el recurso.', 'QrServerError');
    }
  }

  if (error.request) {
    return createError('No fue posible contactar al servidor. Verifica la conexión.', 'QrNetworkError');
  }

  if (error.message) {
    return createError(error.message, 'QrAxiosError');
  }

  return createError('Ocurrió un error desconocido.', 'QrUnknownAxiosError');
};

const toNullableString = (value: unknown): string | null => {
  if (value === null || value === undefined) return null;
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }
  return String(value);
};

const toIsoString = (value: unknown): string | null => {
  if (value === null || value === undefined) return null;
  if (value instanceof Date) return value.toISOString();
  if (typeof value === 'number') {
    const candidate = new Date(value);
    return Number.isNaN(candidate.getTime()) ? null : candidate.toISOString();
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (trimmed.length === 0) return null;
    const candidate = new Date(trimmed);
    return Number.isNaN(candidate.getTime()) ? trimmed : candidate.toISOString();
  }
  return null;
};

const toNullableNumber = (value: unknown): number | null => {
  if (value === null || value === undefined) return null;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
};

const parseOwner = (value: unknown): GanadoOwner => {
  if (!value || typeof value !== 'object') {
    return { nombre: null, telefono: null, rol: null };
  }
  const data = value as Record<string, unknown>;
  const contactValue = data.telefono ?? data.contacto;
  return {
    nombre: toNullableString(data.nombre),
    telefono: toNullableString(contactValue),
    rol: toNullableString(data.rol)
  };
};

const parsePotrero = (value: unknown): GanadoPotrero => {
  if (!value || typeof value !== 'object') {
    return {
      nombre: null,
      tipo_pasto: null,
      ultima_limpieza: null,
      fecha_ultimo_uso: null,
      proxima_limpieza: null,
      capacidad: null,
      estado: null
    };
  }
  const data = value as Record<string, unknown>;
  return {
    nombre: toNullableString(data.nombre),
    tipo_pasto: toNullableString(data.tipo_pasto),
    ultima_limpieza: toIsoString(data.ultima_limpieza),
    fecha_ultimo_uso: toIsoString(data.fecha_ultimo_uso),
    proxima_limpieza: toIsoString(data.proxima_limpieza),
    capacidad: toNullableNumber(data.capacidad),
    estado: toNullableString(data.estado)
  };
};

const parseVacunas = (value: unknown): GanadoVacuna[] => {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const data = item as Record<string, unknown>;
      const nombreVacuna = toNullableString(data.nombre) ?? toNullableString(data.nombre_vacuna);
      return {
        id: toNullableString(data.id),
        nombre: nombreVacuna,
        fecha_aplicacion: toIsoString(data.fecha_aplicacion),
        proxima_dosis: toIsoString(data.proxima_dosis),
        estado: toNullableString(data.estado),
        responsable: toNullableString(data.responsable)
      };
    })
    .filter((vacuna): vacuna is GanadoVacuna => vacuna !== null);
};

const parseHistorial = (value: unknown): GanadoRevision[] => {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const data = item as Record<string, unknown>;
      return {
        id: toNullableString(data.id),
        fecha: toIsoString(data.fecha),
        observaciones: toNullableString(data.observaciones),
        resultado: toNullableString(data.resultado) ?? toNullableString(data.diagnostico),
        veterinario: toNullableString(data.veterinario)
      };
    })
    .filter((registro): registro is GanadoRevision => registro !== null);
};

export const fetchQrResource = async (params: QrResourceRequest): Promise<GanadoResource> => {
  const url = buildUrl(params.endpoint, params.resourceId);
  try {
    const response = await api.get(url, { signal: params.signal });
    const payload = response.data as Record<string, unknown>;
    const raw = typeof payload === 'object' && payload !== null && 'data' in payload
      ? (payload as Record<string, unknown>).data
      : payload;

    if (!raw || typeof raw !== 'object') {
      throw createError('La respuesta del servidor no es válida.', 'QrInvalidResponseError');
    }

    const data = raw as Record<string, unknown>;
    const identifier = toNullableString(data.id);
    if (!identifier) {
      throw createError('La respuesta del servidor no incluye un identificador válido.', 'QrInvalidResponseError');
    }

    const estadoPrincipal = toNullableString(data.estado) ?? toNullableString(data.estado_salud);

    return {
      id: identifier,
      nombre: toNullableString(data.nombre),
      raza: toNullableString(data.raza),
      fecha_nacimiento: toIsoString(data.fecha_nacimiento),
      edad: toNullableNumber(data.edad),
      sexo: toNullableString(data.sexo),
      estado: estadoPrincipal,
      estado_salud: toNullableString(data.estado_salud),
      peso: toNullableNumber(data.peso),
      codigo_qr: toNullableString(data.codigo_qr),
      propietario: parseOwner(data.propietario),
      potrero: parsePotrero(data.potrero),
      vacunas: parseVacunas(data.vacunas),
      historial: parseHistorial(data.historial)
    };
  } catch (error) {
    if (axios.isCancel(error)) {
      throw createError('La consulta fue cancelada.', 'QrRequestCancelledError');
    }
    throw mapAxiosError(error);
  }
};

export interface EmbeddedQrPayload {
  schema?: string;
  type?: string;
  id?: string | number;
  codigo?: string;
  nombre?: string;
  estado?: string;
  estado_salud?: string;
  propietario?: {
    nombre?: string;
    contacto?: string;
    rol?: string;
  };
  potrero?: {
    nombre?: string;
    tipo_pasto?: string;
    ultima_limpieza?: string;
    fecha_ultimo_uso?: string;
    proxima_limpieza?: string;
    capacidad?: number;
    estado?: string;
  } | null;
  url?: string;
  generado_en?: string;
  peso?: number;
  sexo?: string;
  fecha_nacimiento?: string;
  [key: string]: unknown;
}

export const transformEmbeddedPayload = (payload: EmbeddedQrPayload): GanadoResource => {
  const identifier = toNullableString(payload.id);
  if (!identifier) {
    throw createError('El QR embebido no incluye un identificador válido.', 'QrEmbeddedWithoutIdError');
  }

  const potreroData = payload.potrero ?? null;
  return {
    id: identifier,
    nombre: toNullableString(payload.nombre),
    raza: null,
    fecha_nacimiento: toIsoString(payload.fecha_nacimiento),
    edad: null,
    sexo: toNullableString(payload.sexo),
    estado: toNullableString(payload.estado) ?? toNullableString(payload.estado_salud),
    estado_salud: toNullableString(payload.estado_salud),
    peso: toNullableNumber(payload.peso),
    codigo_qr: toNullableString(payload.codigo),
    propietario: {
      nombre: toNullableString(payload.propietario?.nombre),
      telefono: toNullableString(payload.propietario?.contacto),
      rol: toNullableString(payload.propietario?.rol)
    },
    potrero: potreroData
      ? {
          nombre: toNullableString(potreroData.nombre),
          tipo_pasto: toNullableString(potreroData.tipo_pasto),
          ultima_limpieza: toIsoString(potreroData.ultima_limpieza),
          fecha_ultimo_uso: toIsoString(potreroData.fecha_ultimo_uso),
          proxima_limpieza: toIsoString(potreroData.proxima_limpieza),
          capacidad: toNullableNumber(potreroData.capacidad),
          estado: toNullableString(potreroData.estado)
        }
      : {
          nombre: null,
          tipo_pasto: null,
          ultima_limpieza: null,
          fecha_ultimo_uso: null,
          proxima_limpieza: null,
          capacidad: null,
          estado: null
        },
    vacunas: [],
    historial: []
  };
};

