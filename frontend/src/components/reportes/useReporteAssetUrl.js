import { useEffect, useState } from "react";
import api from "../../api/axios";

const protectedPath = (value) => {
  const raw = String(value || "").trim();
  const uploadsAt = raw.indexOf("/uploads/");
  if (uploadsAt >= 0) return `/archivos-protegidos/${raw.slice(uploadsAt + 9)}`;
  return raw;
};

export default function useReporteAssetUrl(value) {
  const [state, setState] = useState({ url: "", loading: Boolean(value), error: false });

  useEffect(() => {
    let active = true;
    let objectUrl = "";
    const raw = String(value || "").trim();
    if (!raw) {
      setState({ url: "", loading: false, error: false });
      return undefined;
    }
    if (/^(blob:|data:)/i.test(raw)) {
      setState({ url: raw, loading: false, error: false });
      return undefined;
    }

    const requestUrl = protectedPath(raw);
    if (!requestUrl.startsWith("/archivos-protegidos/") && /^https?:\/\//i.test(requestUrl)) {
      setState({ url: requestUrl, loading: false, error: false });
      return undefined;
    }

    setState({ url: "", loading: true, error: false });
    api.get(requestUrl, { responseType: "blob" })
      .then(({ data }) => {
        if (!active) return;
        objectUrl = URL.createObjectURL(data);
        setState({ url: objectUrl, loading: false, error: false });
      })
      .catch(() => active && setState({ url: "", loading: false, error: true }));

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [value]);

  return state;
}
