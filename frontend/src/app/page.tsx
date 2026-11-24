// The home page ("/"). Layout loosely follows the Figma `CreationHome` screen,
// widened for a laptop (docs/product/designs.md, ADR 0004).
//
// "use client" makes this a Client Component: it runs in the browser, so it can
// keep state (useState), react to typing and clicks, and call the API directly.
"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";

import { ApiError, ApiUnreachableError, createGoal, type Goal, listGoals } from "@/lib/api";

// Turn any error from src/lib/api.ts into a sentence for the user.
function describeError(error: unknown): string {
  if (error instanceof ApiUnreachableError) {
    return "Can't reach the Gyst API. Is the backend running?";
  }
  if (error instanceof ApiError && error.status === 422) {
    return "Your goal needs a title (1–200 characters).";
  }
  return "Something went wrong. Please try again.";
}

export default function Home() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  // Bumping this number re-runs the effect below (used by "Try again").
  const [loadAttempt, setLoadAttempt] = useState(0);

  const [title, setTitle] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load the saved goals when the page first appears in the browser (and again
  // after "Try again"). `ignore` stops an old, slow response from overwriting
  // newer state if the effect re-runs before it arrives.
  useEffect(() => {
    let ignore = false;
    listGoals() // GET /goals
      .then((loaded) => {
        if (ignore) return;
        setGoals(loaded);
        setLoadError(null);
      })
      .catch((error) => {
        if (!ignore) setLoadError(describeError(error));
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [loadAttempt]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); // stop the browser's default full-page form submit
    setSaving(true);
    setSaveError(null);
    try {
      const goal = await createGoal(title); // POST /goals
      setGoals((current) => [goal, ...current]); // newest first, no reload needed
      setTitle("");
    } catch (error) {
      setSaveError(describeError(error));
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-10 px-10 py-12">
      <header>
        <h1 className="text-6xl font-black tracking-tight">GYST</h1>
        <p className="mt-1 text-lg text-zinc-500">get your stuff together</p>
      </header>

      <section aria-labelledby="add-goal-heading" className="flex flex-col gap-3">
        <h2 id="add-goal-heading" className="text-xl font-semibold">
          + add primary goal
        </h2>
        <form onSubmit={handleSubmit} className="flex max-w-2xl gap-3">
          <input
            ref={inputRef}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="e.g. Run a marathon"
            aria-label="Primary goal title"
            className="flex-1 rounded-xl border border-zinc-300 bg-white px-4 py-3 text-zinc-900 outline-none focus:border-yellow-500 focus:ring-2 focus:ring-yellow-300"
          />
          <button
            type="submit"
            disabled={saving}
            className="rounded-xl bg-zinc-900 px-6 py-3 font-semibold text-white hover:bg-zinc-700 disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save"}
          </button>
        </form>
        {saveError && (
          <p role="alert" className="text-sm text-red-600">
            {saveError}
          </p>
        )}
      </section>

      <section aria-label="Your goals">
        {loading ? (
          <p className="text-zinc-500">Loading your goals…</p>
        ) : loadError ? (
          <div role="alert" className="flex items-center gap-4 rounded-xl bg-red-50 p-4 text-red-700">
            <p>{loadError}</p>
            <button
              onClick={() => {
                setLoading(true);
                setLoadAttempt((n) => n + 1);
              }}
              className="rounded-lg border border-red-300 px-3 py-1 text-sm hover:bg-red-100"
            >
              Try again
            </button>
          </div>
        ) : goals.length === 0 ? (
          // Empty state: the big yellow "+" tile from CreationHome.
          <button
            onClick={() => inputRef.current?.focus()}
            aria-label="Add your first primary goal"
            className="flex aspect-square w-56 items-center justify-center rounded-3xl bg-yellow-300 text-8xl font-light text-white hover:bg-yellow-400"
          >
            +
          </button>
        ) : (
          <ul className="grid grid-cols-4 gap-6">
            {goals.map((goal) => (
              <li
                key={goal.id}
                className="flex aspect-square items-center justify-center rounded-3xl bg-yellow-300 p-5 text-center text-lg font-semibold break-words text-zinc-900"
              >
                {goal.title}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
