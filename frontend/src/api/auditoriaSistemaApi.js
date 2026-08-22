
// ============================================================
// API AUDITORÍA SISTEMA PRO - FASE 35.4.1
// ============================================================
import api from './axios';
import { limpiarParams } from './apiHelpers';
const BASE_URL='/auditoria';
export async function obtenerAuditoriaSistema(params={}){const {data}=await api.get(`${BASE_URL}/sistema`,{params:limpiarParams(params)});return data;}
export async function obtenerDetalleAuditoria(id){const {data}=await api.get(`${BASE_URL}/${id}`);return data;}
export function getAuditoriaExcelUrl(params={}){const q=new URLSearchParams(limpiarParams(params)).toString();return `${api.defaults.baseURL}${BASE_URL}/export/excel${q?`?${q}`:''}`;}
export function getAuditoriaPdfUrl(params={}){const q=new URLSearchParams(limpiarParams(params)).toString();return `${api.defaults.baseURL}${BASE_URL}/export/pdf${q?`?${q}`:''}`;}
