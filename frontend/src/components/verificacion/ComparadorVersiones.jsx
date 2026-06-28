export default function ComparadorVersiones({
  diferencias,
}) {
  if (!diferencias)
    return (
      <div className="comparador-vacio">
        Seleccione dos versiones.
      </div>
    );

  const campos = Object.keys(diferencias);

  return (
    <table className="tabla-comparador">
      <thead>
        <tr>
          <th>Campo</th>
          <th>Antes</th>
          <th>Después</th>
        </tr>
      </thead>

      <tbody>
        {campos.map((campo) => (
          <tr key={campo}>
            <td>{campo}</td>

            <td>
              {String(
                diferencias[campo]?.antes || ""
              )}
            </td>

            <td>
              {String(
                diferencias[campo]?.despues || ""
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}