import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "./api";

const EMPTY = { title: "", notes: "", remindAt: "" };

function formatDate(iso) {
  return new Date(iso).toLocaleString("es", { dateStyle: "medium", timeStyle: "short" });
}

export default function TaskList({ onUnauthorized }) {
  const [tasks, setTasks] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const handleError = useCallback(
    (err) => {
      if (err instanceof ApiError && err.status === 401) onUnauthorized();
      else setError(err.message);
    },
    [onUnauthorized],
  );

  const load = useCallback(async () => {
    try {
      setTasks(await api("/tasks/"));
      setError("");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(request) {
    try {
      await request();
      await load();
      return true;
    } catch (err) {
      handleError(err);
      return false;
    }
  }

  async function addTask(e) {
    e.preventDefault();
    const body = {
      title: form.title.trim(),
      notes: form.notes.trim(),
      remind_at: form.remindAt ? new Date(form.remindAt).toISOString() : null,
    };
    if (await run(() => api("/tasks/", { method: "POST", body }))) setForm(EMPTY);
  }

  const toggle = (task) =>
    run(() => api(`/tasks/${task.id}/`, { method: "PATCH", body: { completed: !task.completed } }));
  const remove = (task) => run(() => api(`/tasks/${task.id}/`, { method: "DELETE" }));
  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const pending = tasks.filter((t) => !t.completed).length;

  return (
    <>
      <form className="card new-task" onSubmit={addTask}>
        <input
          className="title-input"
          placeholder="¿Qué hay que hacer?"
          value={form.title}
          onChange={update("title")}
          maxLength={200}
          required
        />
        <textarea placeholder="Notas (opcional)" rows={2} value={form.notes} onChange={update("notes")} />
        <div className="row">
          <label className="inline">
            Recordarme por email
            <input type="datetime-local" value={form.remindAt} onChange={update("remindAt")} />
          </label>
          <button type="submit">Agregar</button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="muted">Cargando…</p>
      ) : tasks.length === 0 ? (
        <p className="muted empty">No tienes tareas todavía.</p>
      ) : (
        <>
          <p className="muted count">
            {pending} pendiente{pending === 1 ? "" : "s"} de {tasks.length}
          </p>
          <ul className="tasks">
            {tasks.map((task) => (
              <li key={task.id} className={`card task${task.completed ? " done" : ""}`}>
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => toggle(task)}
                  aria-label={`Marcar "${task.title}" como ${task.completed ? "pendiente" : "hecha"}`}
                />
                <div className="body">
                  <span className="title">{task.title}</span>
                  {task.notes && <p className="notes">{task.notes}</p>}
                  {task.remind_at && (
                    <span className={`badge${task.reminder_sent_at ? " sent" : ""}`}>
                      {task.reminder_sent_at ? "Recordatorio enviado · " : "Recordatorio · "}
                      {formatDate(task.remind_at)}
                    </span>
                  )}
                </div>
                <button className="icon" onClick={() => remove(task)} aria-label={`Eliminar "${task.title}"`}>
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}
