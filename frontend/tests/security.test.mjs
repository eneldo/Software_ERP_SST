import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const src = (...parts) => readFileSync(resolve(root, "src", ...parts), "utf8");

const authService = src("services", "authService.js");
const requireAuth = src("components", "auth", "RequireAuth.jsx");
const app = src("App.jsx");
const axiosClient = src("api", "axios.js");

assert.match(authService, /api\.post\("\/auth\/login-json"/, "login debe usar /auth/login-json");
assert.match(authService, /api\.post\("\/auth\/logout"/, "logout debe limpiar cookie HttpOnly en backend");
assert.match(authService, /localStorage\.setItem\(ACCESS_TOKEN_KEY,\s*data\.access_token\)/, "login debe guardar access_token");
assert.match(authService, /localStorage\.setItem\(USER_KEY,\s*JSON\.stringify\(data\.usuario \|\| \{\}\)\)/, "login debe guardar usuario");

assert.match(requireAuth, /isAuthenticated\(\)/, "RequireAuth debe usar verificacion centralizada de autenticacion");
assert.match(authService, /localStorage\.getItem\(ACCESS_TOKEN_KEY\)/, "authService debe leer access_token");
assert.match(requireAuth, /<Navigate to="\/" replace state=\{\{ from: location \}\}/, "RequireAuth debe redirigir al login sin token");

for (const route of [
  "/admin/dashboard",
  "/organizacion/empresas",
  "/hacer/examenes-medicos",
  "/documental/firma-digital",
  "/admin/usuarios-sistema",
]) {
  const routePattern = new RegExp(`path="${route.replaceAll("/", "\\/")}"[^\\n]+<ProtectedPage`);
  assert.match(app, routePattern, `la ruta critica ${route} debe estar protegida`);
}

assert.match(axiosClient, /headers\.Authorization = `Bearer \$\{token\}`/, "axios debe enviar Authorization Bearer");
assert.match(axiosClient, /withCredentials:\s*true/, "axios debe enviar cookies HttpOnly");
assert.match(axiosClient, /\/auth\/refresh/, "axios debe intentar renovar access token con refresh token");

console.log("Frontend security tests OK");
