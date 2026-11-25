// The goal page ("/goals/3"): the primary goal in the center of a 3x3 grid,
// with its 8 supporting-goal slots around it (Figma `CreationMid9Light`).
//
// [id] in the folder name makes this a dynamic route: one page file serves
// every goal, and useParams() reads the id from the URL.
"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { Grid } from "@/components/Grid";
import { SlotTile } from "@/components/SlotTile";
import {
  ApiError,
  clearSupportingGoal,
  describeError,
  getGoal,
  type GoalDetail,
  setSupportingGoal,
} from "@/lib/api";
import { PRIMARY_COLOR, SLOT_COLORS } from "@/lib/colors";

const describe = (error: unknown) =>
  describeError(error, "A supporting goal needs a title (1–200 characters).");

// The id in the URL is only known when the page is visited, so the part that
// reads it sits inside <Suspense> (required with `cacheComponents` on).
export default function GoalPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <GoalGrid />
    </Suspense>
  );
}

function GoalGrid() {
  const { id } = useParams<{ id: string }>();
  const [goal, setGoal] = useState<GoalDetail | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    getGoal(id) // GET /goals/{id}
      .then((loaded) => {
        if (!ignore) setGoal(loaded);
      })
      .catch((error) => {
        if (ignore) return;
        // 404: no such goal. 422: the id isn't even a number (e.g. /goals/abc).
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
        <p className="text-xl">Goal not found.</p>
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
  if (!goal) return <PageShell>Loading…</PageShell>;

  async function save(position: number, title: string): Promise<boolean> {
    setSaveError(null);
    try {
      const saved = await setSupportingGoal(goal!.id, position, title); // PUT
      setGoal((current) =>
        current && {
          ...current,
          supporting_goals: [
            ...current.supporting_goals.filter((s) => s.position !== position),
            saved,
          ],
        },
      );
      return true;
    } catch (error) {
      setSaveError(describe(error));
      return false;
    }
  }

  async function clear(position: number) {
    setSaveError(null);
    try {
      await clearSupportingGoal(goal!.id, position); // DELETE
      setGoal(
        (current) =>
          current && {
            ...current,
            supporting_goals: current.supporting_goals.filter((s) => s.position !== position),
          },
      );
    } catch (error) {
      setSaveError(describe(error));
    }
  }

  const slots = SLOT_COLORS.map((color, position) => {
    const slot = goal.supporting_goals.find((s) => s.position === position);
    return (
      <SlotTile
        key={position}
        color={color}
        label={`Supporting goal ${position + 1}`}
        title={slot?.title}
        onSave={(title) => save(position, title)}
        onClear={() => clear(position)}
        // A filled supporting goal opens its own grid of tasks.
        href={slot && `/supporting-goals/${slot.id}`}
      />
    );
  });

  const center = (
    <div
      className={`flex h-full w-full items-center justify-center rounded-3xl ${PRIMARY_COLOR} p-4 text-center text-xl font-bold break-words text-zinc-900 ring-4 ring-yellow-500/40`}
    >
      {goal.title}
    </div>
  );

  return (
    <PageShell>
      <h2 className="text-xl font-semibold">+ add supporting goals</h2>
      <p className="-mt-6 text-zinc-500">
        The 8 pillars that make &ldquo;{goal.title}&rdquo; happen. Fill them in any order, then click one to add its tasks.
      </p>
      {saveError && (
        <p role="alert" className="text-sm text-red-600">
          {saveError}
        </p>
      )}
      <Grid center={center} slots={slots} />
    </PageShell>
  );
}

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-10 py-12">
      <header className="flex items-end justify-between">
        <Link href="/" className="text-5xl font-black tracking-tight">
          GYST
        </Link>
        <Link href="/" className="text-zinc-500 hover:text-zinc-900">
          ← All goals
        </Link>
      </header>
      {children}
    </main>
  );
}
