import {
  Eye,
  RotateCcw,
  FileText,
  ShieldCheck,
} from "lucide-react";

export default function VersionCard({
  version,
  onVer,
  onRestaurar,
}) {
  const obtenerEstado = () => {
    if (version.estado_documental === "OFICIAL")
      return "estado-oficial";

    if (version.estado_documental === "BORRADOR")
      return "estado-borrador";

    if (version.estado_documental === "ANULADA")
      return "estado-anulada";

    return "estado-historica";
  };

  return (
    <div className="version-card">
      <div className="version-header">
        <h4>{version.codigo_version}</h4>

        <span className={obtenerEstado()}>
          {version.estado_documental}
        </span>
      </div>

      <p>{version.observacion}</p>

      <small>{version.accion}</small>

      <div className="version-actions">
        <button onClick={() => onVer(version)}>
          <Eye size={16} />
          Ver
        </button>

        <button onClick={() => onRestaurar(version)}>
          <RotateCcw size={16} />
          Restaurar
        </button>

        <button>
          <FileText size={16} />
          PDF
        </button>

        <button>
          <ShieldCheck size={16} />
          Hash
        </button>
      </div>
    </div>
  );
}