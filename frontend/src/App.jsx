import { useCallback, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";
import AuthForm from "./AuthForm.jsx";
import TaskList from "./TaskList.jsx";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  const clearSession = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (!getToken()) return;
    api("/auth/me/")
      .then(setUser)
      .catch(clearSession)
      .finally(() => setLoading(false));
  }, [clearSession]);

  function handleAuth({ token, user }) {
    setToken(token);
    setUser(user);
  }

  async function logout() {
    try {
      await api("/auth/logout/", { method: "POST" });
    } catch {
      // The token is dropped locally either way.
    }
    clearSession();
  }

  return (
    <main className="shell">
      <header className="topbar">
        <h1>Tareas</h1>
        {user && (
          <div className="user">
            <span>{user.username}</span>
            <button className="link" onClick={logout}>
              Salir
            </button>
          </div>
        )}
      </header>

      {loading ? (
        <p className="muted">Cargando…</p>
      ) : user ? (
        <TaskList onUnauthorized={clearSession} />
      ) : (
        <AuthForm onAuth={handleAuth} />
      )}
    </main>
  );
}
