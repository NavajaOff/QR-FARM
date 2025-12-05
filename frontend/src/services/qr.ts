import api from './api.js';
import axios, { isAxiosError } from 'axios';

export interface QrResourceRequest {
  endpoint: string;
  resourceId: string;
  alternatives?: string[];
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

export interface GanadoHistorial {
  id: string | null;
  fecha: string | null;
  observaciones: string | null;
  resultado: string | null;
  diagnostico: string | null;
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
  historial: GanadoHistorial[];
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
    ? sanitizedEndpoint.slice(0, -1)
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
      return createError('Este QR no está registrado en la base de datos.', 'QrNotFoundError');
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
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  // Para tipos desconocidos, retornar null en lugar de usar String() que podría dar '[object Object]'
  return null;
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

const parseHistorial = (value: unknown): GanadoHistorial[] => {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const data = item as Record<string, unknown>;
      
      // Manejar fecha - si es string vacío, retornar null
      let fechaValue: string | null = null;
      if (data.fecha !== null && data.fecha !== undefined) {
        if (typeof data.fecha === 'string' && data.fecha.trim() === '') {
          fechaValue = null;
        } else {
          fechaValue = toIsoString(data.fecha);
        }
      }
      
      // Manejar resultado y diagnostico - diagnostico como fallback de resultado
      const diagnosticoValue = toNullableString(data.diagnostico);
      const resultadoValue = toNullableString(data.resultado) ?? diagnosticoValue;
      
      return {
        id: toNullableString(data.id),
        fecha: fechaValue,
        observaciones: toNullableString(data.observaciones),
        resultado: resultadoValue,
        diagnostico: diagnosticoValue
      };
    })
    .filter((historial): historial is GanadoHistorial => historial !== null);
};

const parseGanadoResponse = (input: unknown): GanadoResource => {
  if (!input || typeof input !== 'object') {
    throw createError('La respuesta del servidor no es válida.', 'QrInvalidResponseError');
  }
  const payload = input as Record<string, unknown>;
  const raw = 'data' in payload ? payload.data : payload;

  if (!raw || typeof raw !== 'object') {
    throw createError('La respuesta del servidor no es válida.', 'QrInvalidResponseError');
  }

  const data = raw as Record<string, unknown>;
  const identifier = toNullableString(data.id);
  if (!identifier) {
    throw createError('La respuesta del servidor no incluye un identificador válido.', 'QrInvalidResponseError');
  }

  const primaryState = toNullableString(data.estado) ?? toNullableString(data.estado_salud);

  return {
    id: identifier,
    nombre: toNullableString(data.nombre),
    raza: toNullableString(data.raza),
    fecha_nacimiento: toIsoString(data.fecha_nacimiento),
    edad: toNullableNumber(data.edad),
    sexo: toNullableString(data.sexo),
    estado: primaryState,
    estado_salud: toNullableString(data.estado_salud),
    peso: toNullableNumber(data.peso),
    codigo_qr: toNullableString(data.codigo_qr),
    propietario: parseOwner(data.propietario),
    potrero: parsePotrero(data.potrero),
    vacunas: parseVacunas(data.vacunas),
    historial: parseHistorial(data.historial)
  };
};

export const fetchQrResource = async (params: QrResourceRequest): Promise<GanadoResource> => {
  const candidates = [params.resourceId, ...(params.alternatives ?? [])]
    .map((candidate) => {
      if (typeof candidate === 'number') {
        return String(candidate);
      }
      if (typeof candidate === 'string') {
        return candidate.trim();
      }
      return '';
    })
    .filter((value): value is string => value.length > 0);

  const seen = new Set<string>();
  const queue = candidates.filter(candidate => {
    const normalized = candidate.trim();
    if (seen.has(normalized)) return false;
    seen.add(normalized);
    return true;
  });

  if (queue.length === 0) {
    throw createError('El identificador del código QR es obligatorio.', 'QrResourceIdError');
  }

  let lastNotFoundError: Error | null = null;

  for (const candidate of queue) {
    const url = buildUrl(params.endpoint, candidate);
    try {
      const response = await api.get(url, { signal: params.signal });
      return parseGanadoResponse(response.data);
    } catch (error) {
      if (axios.isCancel(error)) {
        throw createError('La consulta fue cancelada.', 'QrRequestCancelledError');
      }

      if (isAxiosError(error) && error.response?.status === 404) {
        lastNotFoundError = mapAxiosError(error);
        continue;
      }

      throw mapAxiosError(error);
    }
  }

  if (lastNotFoundError) {
    throw lastNotFoundError;
  }

  throw createError('No se pudo consultar el recurso asociado.', 'QrUnknownError');
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

