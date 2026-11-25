// The task page ("/supporting-goals/7"): the same 3x3 grid one level down
// (Figma `CreationTask9Light`). The supporting goal is in the center, its 8
// task slots around it, and a side panel edits the selected task.
"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { type ReactNode, Suspense, useEffect, useState } from "react";

import { Grid } from "@/components/Grid";
import { TaskPanel } from "@/components/TaskPanel";
import {
  ApiError,
  clearTask,
  describeError,
  getSupportingGoal,
  setTask,
  type SupportingGoalDetail,
  type TaskInput,
} from "@/lib/api";
import { SLOT_COLORS, SLOT_SOFT_COLORS } from "@/lib/colors";
import { describeSchedule } from "@/lib/schedule";

const describe = (error: unknown) =>
  describeError(error, "Check the task's fields: a title, 1–480 minutes, and how often.");

// The id in the URL is only known when the page is visited, so the part that
// reads it sits inside <Suspense> (required with `cacheComponents` on).
export default function SupportingGoalPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <TaskGrid />
    </Suspense>
  );
}

function TaskGrid() {
  const { id } = useParams<{ id: string }>();
  const [sg, setSg] = useState<SupportingGoalDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [selected, setSelected] = useState<number | null>(null); // slot in the panel

  useEffect(() => {
    let ignore = false;
    getSupportingGoal(id) // GET /supporting-goals/{id}
      .then((loaded) => {
        if (!ignore) setSg(loaded);
      })
      .catch((error) => {
        if (ignore) return;
        if (error instanceof ApiError && (error.status === 404 || error.status === 422)) {
          setNotFound(true);
        } else {
          setLoadError(describe(error));
        }
      });
    return () => {
      ignore = true;
    };
  }, [id]);

  if (notFound) {
    return (
      <PageShell>
        <p className="text-xl">Supporting goal not found.</p>
      </PageShell>
    );
  }
  if (loadError) {
    return (
      <PageShell>
        <p role="alert" className="rounded-xl bg-red-50 p-4 text-red-700">
          {loadError}
        </p>
      </PageShell>
    );
  }
  if (!sg) return <PageShell>Loading…</PageShell>;

  // Weekly tasks are placed on the lightest days, so saving or clearing *any*
  // task can move the others. Reload the whole list to show the new days.
  async function reload() {
    setSg(await getSupportingGoal(id));
  }

  async function save(position: number, input: TaskInput): Promise<string | null> {
    try {
      await setTask(sg!.id, position, input); // PUT
      await reload();
      return null;
    } catch (error) {
      return describe(error);
    }
  }

  async function clear(position: number) {
    try {
      await clearTask(sg!.id, position); // DELETE
      setSelected(null);
      await reload();
    } catch (error) {
      setLoadError(describe(error));
    }
  }

  const soft = SLOT_SOFT_COLORS[sg.position];
  const slots = SLOT_SOFT_COLORS.map((_, position) => {
    const task = sg.tasks.find((t) => t.position === position);
    const isSelected = selected === position;
    return (
      <button
        key={position}
        onClick={() => setSelected(position)}
        aria-pressed={isSelected}
        aria-label={task ? `Edit task ${task.title}` : `Add task ${position + 1}`}
        className={`flex h-full w-full flex-col items-center justify-center gap-2 rounded-3xl ${soft} p-3 text-center hover:brightness-95 ${
          isSelected ? "ring-4 ring-zinc-900" : ""
        }`}
      >
        {task ? (
          <>
            <span className="text-base font-semibold break-words text-zinc-900">{task.title}</span>
            <span className="text-xs text-zinc-600">{describeSchedule(task)}</span>
          </>
        ) : (
          <span className="text-6xl font-light text-zinc-400">+</span>
        )}
      </button>
    );
  });

  const center = (
    <div
      className={`flex h-full w-full items-center justify-center rounded-3xl ${SLOT_COLORS[sg.position]} p-4 text-center text-xl font-bold break-words text-zinc-900`}
    >
      {sg.title}
    </div>
  );

  return (
    <PageShell back={{ href: `/goals/${sg.goal_id}`, label: sg.goal_title }}>
      <h2 className="text-xl font-semibold">+ add tasks</h2>
      <p className="-mt-6 text-zinc-500">
        The 8 things you&rsquo;ll do for &ldquo;{sg.title}&rdquo;. Click a slot to add or edit one.
      </p>
      <div className="flex items-start gap-8">
        <Grid center={center} slots={slots} />
        {selected === null ? (
          <p className="w-96 shrink-0 rounded-3xl border border-dashed border-zinc-300 p-6 text-zinc-500">
            Pick a slot to add a task.
          </p>
        ) : (
          <TaskPanel
            key={selected}
            task={sg.tasks.find((t) => t.position === selected)}
            slotNumber={selected + 1}
            onSave={(input) => save(selected, input)}
            onClear={() => clear(selected)}
            onClose={() => setSelected(null)}
          />
        )}
      </div>
    </PageShell>
  );
}

function PageShell({
  children,
  back,
}: {
  children: ReactNode;
  back?: { href: string; label: string };
}) {
  return (
    <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 px-10 py-12">
      <header className="flex items-end justify-between">
        <Link href="/" className="text-5xl font-black tracking-tight">
          GYST
        </Link>
        <Link href={back?.href ?? "/"} className="text-zinc-500 hover:text-zinc-900">
          ← {back?.label ?? "All goals"}
        </Link>
      </header>
      {children}
    </main>
  );
}
