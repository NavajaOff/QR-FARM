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
  edadTexto: string | null;
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

const calculateAgeDetailFromDate = (value: string | null): { years: number; months: number } | null => {
  if (!value) return null;
  const candidate = new Date(value);
  if (Number.isNaN(candidate.getTime())) return null;
  const today = new Date();
  let years = today.getFullYear() - candidate.getFullYear();
  let months = today.getMonth() - candidate.getMonth();
  if (today.getDate() < candidate.getDate()) {
    months -= 1;
  }
  if (months < 0) {
    years -= 1;
    months += 12;
  }
  if (years < 0) {
    years = 0;
    months = 0;
  }
  return { years, months };
};

const formatEdadTextoFromDetail = (detail: { years: number; months: number } | null): string | null => {
  if (!detail) return null;
  if (detail.years >= 1) {
    return detail.years === 1 ? '1 año' : `${detail.years} años`;
  }
  if (detail.months >= 1) {
    return detail.months === 1 ? '1 mes' : `${detail.months} meses`;
  }
  return 'Menos de un mes';
};

const formatEdadTextoFromPayload = (fechaNacimiento: string | null, edadValue: number | null): string => {
  const detail = calculateAgeDetailFromDate(fechaNacimiento);
  const detalleTexto = formatEdadTextoFromDetail(detail);
  if (detalleTexto) {
    return detalleTexto;
  }
  if (typeof edadValue === 'number' && Number.isFinite(edadValue)) {
    if (edadValue === 1) return '1 año';
    if (edadValue > 1) return `${edadValue} años`;
  }
  return 'Sin datos';
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
        if (typeof data.fecha === 'string' && data.fecha.trim() !== '') {
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

const prepareCandidateQueue = (alternatives: string[] | undefined, resourceId: string): string[] => {
  const allCandidates = [...(alternatives ?? []), resourceId]
    .map(normalizeCandidate)
    .filter((value): value is string => value.length > 0);

  return removeDuplicates(allCandidates);
};

const normalizeCandidate = (candidate: unknown): string => {
  if (typeof candidate === 'number') {
    return String(candidate);
  }
  if (typeof candidate === 'string') {
    return candidate.trim();
  }
  return '';
};

const removeDuplicates = (candidates: string[]): string[] => {
  const seen = new Set<string>();
  return candidates.filter(candidate => {
    const normalized = candidate.trim();
    if (seen.has(normalized)) return false;
    seen.add(normalized);
    return true;
  });
};

const handleParseError = (error: unknown): void => {
  if (error instanceof Error && error.name === 'QrInvalidResponseError') {
    throw error;
  }
};

const handleCancelError = (error: unknown): void => {
  if (axios.isCancel(error)) {
    throw createError('La consulta fue cancelada.', 'QrRequestCancelledError');
  }
};

const tryFetchByQrCode = async (
  qrUrl: string,
  candidate: string,
  signal?: AbortSignal
): Promise<GanadoResource> => {
  console.log('[QR-SERVICE] Intentando buscar por código QR:', qrUrl, 'candidate:', candidate);
  const response = await api.get(qrUrl, { signal });
  console.log('[QR-SERVICE] Respuesta exitosa por código QR:', response.data);
  return parseGanadoResponse(response.data);
};

const tryFetchById = async (
  idUrl: string,
  candidate: string,
  signal?: AbortSignal
): Promise<GanadoResource> => {
  console.log('[QR-SERVICE] Intentando buscar por ID:', idUrl);
  const response = await api.get(idUrl, { signal });
  console.log('[QR-SERVICE] Respuesta exitosa por ID:', response.data);
  return parseGanadoResponse(response.data);
};

interface ProcessCandidateResult {
  success: boolean;
  resource?: GanadoResource;
  error?: Error;
}

const processNumericCandidate = async (
  candidate: string,
  qrEndpoint: string,
  idEndpoint: string,
  signal?: AbortSignal
): Promise<ProcessCandidateResult> => {
  console.log('[QR-SERVICE] Candidato numérico detectado, intentando primero por ID:', candidate);
  const idUrl = buildUrl(idEndpoint, candidate);

  try {
    const resource = await tryFetchById(idUrl, candidate, signal);
    return { success: true, resource };
  } catch (idError) {
    handleCancelError(idError);
    handleParseError(idError);

    if (isAxiosError(idError) && idError.response?.status === 404) {
      return await tryQrFallback(candidate, qrEndpoint, idError, signal);
    }
    throw mapAxiosError(idError);
  }
};

const tryQrFallback = async (
  candidate: string,
  qrEndpoint: string,
  originalError: unknown,
  signal?: AbortSignal
): Promise<ProcessCandidateResult> => {
  console.log('[QR-SERVICE] No encontrado por ID, intentando por código QR:', candidate);
  const qrUrl = buildUrl(qrEndpoint, candidate);

  try {
    const resource = await tryFetchByQrCode(qrUrl, candidate, signal);
    return { success: true, resource };
  } catch (qrError) {
    handleCancelError(qrError);
    handleParseError(qrError);

    if (isAxiosError(qrError) && qrError.response?.status === 404) {
      console.log('[QR-SERVICE] No encontrado por código QR tampoco');
      return { success: false, error: mapAxiosError(originalError) };
    }
    throw mapAxiosError(qrError);
  }
};

const processNonNumericCandidate = async (
  candidate: string,
  qrEndpoint: string,
  signal?: AbortSignal
): Promise<ProcessCandidateResult> => {
  const qrUrl = buildUrl(qrEndpoint, candidate);

  try {
    const resource = await tryFetchByQrCode(qrUrl, candidate, signal);
    return { success: true, resource };
  } catch (error) {
    handleCancelError(error);
    handleParseError(error);

    if (isAxiosError(error) && error.response?.status === 404) {
      console.log('[QR-SERVICE] No encontrado por código QR, no es numérico, no se puede intentar por ID');
      return { success: false, error: mapAxiosError(error) };
    }
    throw mapAxiosError(error);
  }
};

const processCandidate = async (
  candidate: string,
  qrEndpoint: string,
  idEndpoint: string,
  signal?: AbortSignal
): Promise<ProcessCandidateResult> => {
  const isNumeric = /^\d+$/.test(candidate);

  if (isNumeric) {
    return processNumericCandidate(candidate, qrEndpoint, idEndpoint, signal);
  }

  return processNonNumericCandidate(candidate, qrEndpoint, signal);
};

const prioritizeCandidates = (alternatives: string[] | undefined, resourceId: string): string[] => {
  const allCandidates = [...(alternatives ?? []), resourceId];
  const numericIds = allCandidates.filter(c => /^\d+$/.test(String(c)));
  const nonNumericIds = allCandidates.filter(c => !/^\d+$/.test(String(c)));

  // Ordenar: primero IDs numéricos, luego códigos QR
  const queue = [...numericIds, ...nonNumericIds];
  return prepareCandidateQueue(queue, resourceId);
};

const buildEndpoints = (endpoint: string): { qrEndpoint: string; idEndpoint: string } => {
  const qrEndpoint = endpoint;
  const idEndpoint = endpoint.replace('/qr/{id}', '/{id}').replace('/qr/', '/');
  return { qrEndpoint, idEndpoint };
};

const tryCandidatesSequentially = async (
  candidates: string[],
  qrEndpoint: string,
  idEndpoint: string,
  signal?: AbortSignal
): Promise<GanadoResource> => {
  let lastNotFoundError: Error | null = null;

  for (const candidate of candidates) {
    const result = await processCandidate(candidate, qrEndpoint, idEndpoint, signal);
    if (result.success && result.resource) {
      console.log('[QR-SERVICE] Recurso encontrado con candidato:', candidate);
      return result.resource;
    }
    if (result.error) {
      lastNotFoundError = result.error;
    }
  }

  if (lastNotFoundError) {
    throw lastNotFoundError;
  }

  throw createError('No se pudo consultar el recurso asociado.', 'QrUnknownError');
};

export const fetchQrResource = async (params: QrResourceRequest): Promise<GanadoResource> => {
  console.log('[QR-SERVICE] fetchQrResource llamado con:', {
    endpoint: params.endpoint,
    resourceId: params.resourceId,
    alternatives: params.alternatives
  });

  const candidates = prioritizeCandidates(params.alternatives, params.resourceId);

  if (candidates.length === 0) {
    throw createError('El identificador del código QR es obligatorio.', 'QrResourceIdError');
  }

  console.log('[QR-SERVICE] Cola de búsqueda (priorizando IDs numéricos):', candidates);

  const { qrEndpoint, idEndpoint } = buildEndpoints(params.endpoint);

  return tryCandidatesSequentially(candidates, qrEndpoint, idEndpoint, params.signal);
};

export interface EmbeddedQrPayload {
  // Campos abreviados (optimizados para reducir tamaño del QR)
  s?: string;  // schema
  t?: string;  // type
  id?: string | number;
  c?: string;  // codigo
  n?: string;  // nombre
  e?: string;  // estado
  p?: string;  // propietario (nombre)
  ct?: string;  // contacto
  u?: string;  // url
  tid?: number;  // tenant_id
  
  // Campos legacy (compatibilidad hacia atrás)
  schema?: string;
  type?: string;
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

  // Soporte para campos abreviados (optimizados) y legacy (compatibilidad)
  const nombre = toNullableString(payload.n) ?? toNullableString(payload.nombre);
  const codigo = toNullableString(payload.c) ?? toNullableString(payload.codigo);
  const estado = toNullableString(payload.e) ?? toNullableString(payload.estado) ?? toNullableString(payload.estado_salud);
  const propietarioNombre = toNullableString(payload.p) ?? toNullableString(payload.propietario?.nombre);
  const contacto = toNullableString(payload.ct) ?? toNullableString(payload.propietario?.contacto);
  const potreroData = payload.potrero ?? null;
  const fechaNac = toIsoString(payload.fecha_nacimiento);
  
  // Calcular edad si hay fecha_nacimiento
  let edadCalculada: number | null = null;
  if (fechaNac) {
    try {
      const fecha = new Date(fechaNac);
      const hoy = new Date();
      let edad = hoy.getFullYear() - fecha.getFullYear();
      const mesDiff = hoy.getMonth() - fecha.getMonth();
      if (mesDiff < 0 || (mesDiff === 0 && hoy.getDate() < fecha.getDate())) {
        edad--;
      }
      edadCalculada = edad >= 0 ? edad : null;
    } catch {
      edadCalculada = null;
    }
  }
  const edadTextoCalculada = formatEdadTextoFromPayload(fechaNac, edadCalculada ?? toNullableNumber(payload.edad));
  
  return {
    id: identifier,
    nombre: nombre,
    raza: toNullableString(payload.raza),
    fecha_nacimiento: fechaNac,
    edad: edadCalculada ?? toNullableNumber(payload.edad),
    sexo: toNullableString(payload.sexo),
    estado: estado,
    estado_salud: toNullableString(payload.estado_salud),
    edadTexto: edadTextoCalculada,
    peso: toNullableNumber(payload.peso),
    codigo_qr: codigo,
    propietario: {
      nombre: propietarioNombre,
      telefono: contacto,
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

