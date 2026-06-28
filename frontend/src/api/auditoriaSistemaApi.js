
// ============================================================
// API AUDITORÍA SISTEMA PRO - FASE 35.4.1
// ============================================================
import api from './axios';
const BASE_URL='/auditoria';
function cleanParams(params={}){return Object.fromEntries(Object.entries(params).filter(([,v])=>v!==''&&v!==null&&v!==undefined));}
export async function obtenerAuditoriaSistema(params={}){const {data}=await api.get(`${BASE_URL}/sistema`,{params:cleanParams(params)});return data;}
export async function obtenerDetalleAuditoria(id){const {data}=await api.get(`${BASE_URL}/${id}`);return data;}
export function getAuditoriaExcelUrl(params={}){const q=new URLSearchParams(cleanParams(params)).toString();return `${api.defaults.baseURL}${BASE_URL}/export/excel${q?`?${q}`:''}`;}
export function getAuditoriaPdfUrl(params={}){const q=new URLSearchParams(cleanParams(params)).toString();return `${api.defaults.baseURL}${BASE_URL}/export/pdf${q?`?${q}`:''}`;}
