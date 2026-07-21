import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { obtenerAparienciaSistema } from "../../api/configuracionSistemaApi";

export const DEFAULT_BRANDING = {
  nombre_plataforma: "ERP SST PRO",
  logo_data_url: null,
  color_primario: "#2563EB",
  color_secundario: "#1E40AF",
  color_menu_inicio: "#0F172A",
  color_menu_fin: "#1E3A8A",
  tipografia: "Inter",
};

const FONT_STACKS = {
  Inter: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  Arial: 'Arial, Helvetica, sans-serif',
  Verdana: 'Verdana, Geneva, sans-serif',
  Tahoma: 'Tahoma, Geneva, sans-serif',
  "Trebuchet MS": '"Trebuchet MS", Arial, sans-serif',
  Georgia: 'Georgia, "Times New Roman", serif',
};

const BrandingContext = createContext({ branding: DEFAULT_BRANDING, refreshBranding: async () => {} });

function aplicarMarca(branding) {
  const root = document.documentElement;
  root.style.setProperty("--sst-primary", branding.color_primario);
  root.style.setProperty("--sst-primary-dark", branding.color_secundario);
  root.style.setProperty("--sst-sidebar-start", branding.color_menu_inicio);
  root.style.setProperty("--sst-sidebar-end", branding.color_menu_fin);
  root.style.setProperty("--sst-sidebar", `linear-gradient(180deg, ${branding.color_menu_inicio} 0%, ${branding.color_menu_fin} 100%)`);
  root.style.setProperty("--sst-font-family", FONT_STACKS[branding.tipografia] || FONT_STACKS.Inter);
  document.title = branding.nombre_plataforma || DEFAULT_BRANDING.nombre_plataforma;
}

export function BrandingProvider({ children }) {
  const [branding, setBranding] = useState(() => {
    try {
      return { ...DEFAULT_BRANDING, ...JSON.parse(localStorage.getItem("sst_branding") || "{}") };
    } catch {
      return DEFAULT_BRANDING;
    }
  });

  const refreshBranding = async () => {
    try {
      const data = await obtenerAparienciaSistema();
      const next = { ...DEFAULT_BRANDING, ...data };
      setBranding(next);
      localStorage.setItem("sst_branding", JSON.stringify(next));
      aplicarMarca(next);
      return next;
    } catch {
      aplicarMarca(branding);
      return branding;
    }
  };

  useEffect(() => {
    aplicarMarca(branding);
    refreshBranding();
  }, []);

  const value = useMemo(() => ({ branding, refreshBranding }), [branding]);
  return <BrandingContext.Provider value={value}>{children}</BrandingContext.Provider>;
}

export function useBranding() {
  return useContext(BrandingContext);
}
