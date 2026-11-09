import { useState } from "react";
import { api } from "./api";

export default function AuthForm({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const isRegister = mode === "register";

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = isRegister
        ? form
        : { username: form.username, password: form.password };
      onAuth(await api(`/auth/${mode}/`, { method: "POST", body }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card auth" onSubmit={submit}>
      <h2>{isRegister ? "Crear cuenta" : "Iniciar sesión"}</h2>

      <label>
        Usuario
        <input value={form.username} onChange={update("username")} autoComplete="username" required />
      </label>
      {isRegister && (
        <label>
          Email <span className="muted">(para los recordatorios)</span>
          <input type="email" value={form.email} onChange={update("email")} autoComplete="email" required />
        </label>
      )}
      <label>
        Contraseña
        <input
          type="password"
          value={form.password}
          onChange={update("password")}
          autoComplete={isRegister ? "new-password" : "current-password"}
          required
        />
      </label>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={busy}>
        {isRegister ? "Registrarme" : "Entrar"}
      </button>
      <button
        type="button"
        className="link"
        onClick={() => {
          setMode(isRegister ? "login" : "register");
          setError("");
        }}
      >
        {isRegister ? "Ya tengo cuenta" : "Crear una cuenta"}
      </button>
    </form>
  );
}
