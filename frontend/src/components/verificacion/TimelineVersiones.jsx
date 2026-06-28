import "./timeline-versiones.css";

export default function TimelineVersiones({ versiones = [] }) {
  return (
    <div className="timeline-versiones">
      {versiones.map((v, index) => (
        <div key={v.id} className="timeline-item">
          <div className="timeline-circle">
            V{v.version_numero}
          </div>

          <div className="timeline-info">
            <strong>{v.codigo_version}</strong>

            <span>{v.accion}</span>

            <small>
              {new Date(v.fecha_creacion).toLocaleString()}
            </small>
          </div>

          {index !== versiones.length - 1 && (
            <div className="timeline-line"></div>
          )}
        </div>
      ))}
    </div>
  );
}