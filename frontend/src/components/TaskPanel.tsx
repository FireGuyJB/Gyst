// The side panel for creating or editing one task. It sits next to the 3x3
// grid (not a pop-up) so you can see the other tasks while you work.
//
// Only a title is required. Everything else starts with a sensible default
// (15 minutes, every day), so a task can be added in a few seconds.
"use client";

import { type FormEvent, useState } from "react";

import type { Frequency, Task, TaskInput } from "@/lib/api";
import { dayNames, WEEKDAYS } from "@/lib/schedule";

const DURATION_PRESETS = [5, 15, 30, 60];

const FREQUENCIES: { value: Frequency; label: string }[] = [
  { value: "daily", label: "Every day" },
  { value: "days", label: "Specific days" },
  { value: "weekly", label: "× per week" },
  { value: "per_day", label: "× per day" },
];

type TaskPanelProps = {
  /** The saved task, or undefined when filling an empty slot. */
  task?: Task;
  slotNumber: number; // 1-8, for the heading
  /** Save the task. Resolves to an error message, or null if it saved. */
  onSave: (input: TaskInput) => Promise<string | null>;
  onClear: () => Promise<void>;
  onClose: () => void;
};

export function TaskPanel({ task, slotNumber, onSave, onClear, onClose }: TaskPanelProps) {
  // The form starts from the saved task, or from the defaults for a new one.
  // (The page gives each slot its own panel via `key`, so switching slots
  // starts a fresh form.)
  const [title, setTitle] = useState(task?.title ?? "");
  const [description, setDescription] = useState(task?.description ?? "");
  const [duration, setDuration] = useState(task?.duration_minutes ?? 15);
  const [frequency, setFrequency] = useState<Frequency>(task?.frequency ?? "daily");
  const [weekdays, setWeekdays] = useState<number[]>(task?.weekdays ?? []);
  const [timesPerWeek, setTimesPerWeek] = useState(task?.times_per_week ?? 2);
  const [timesPerDay, setTimesPerDay] = useState(task?.times_per_day ?? 2);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const missingDays = frequency === "days" && weekdays.length === 0;
  const canSave = title.trim() !== "" && !missingDays && !saving;

  function toggleDay(day: number) {
    setWeekdays((current) =>
      current.includes(day) ? current.filter((d) => d !== day) : [...current, day].sort(),
    );
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError(null);
    // Send every field; the API ignores the ones this frequency doesn't use.
    const message = await onSave({
      title,
      description,
      duration_minutes: duration,
      frequency,
      weekdays,
      times_per_week: timesPerWeek,
      times_per_day: timesPerDay,
    });
    setSaving(false);
    setError(message);
  }

  async function handleClear() {
    if (!task || !window.confirm(`Clear "${task.title}"?`)) return;
    await onClear();
  }

  const chip = (selected: boolean) =>
    `rounded-full border px-3 py-1 text-sm ${
      selected
        ? "border-zinc-900 bg-zinc-900 text-white"
        : "border-zinc-300 bg-white text-zinc-800 hover:border-zinc-500"
    }`;

  return (
    <form
      onSubmit={handleSubmit}
      aria-label={`Task ${slotNumber}`}
      className="flex w-96 shrink-0 flex-col gap-5 rounded-3xl border border-zinc-200 bg-white p-6 text-zinc-900 shadow-sm"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{task ? "Edit task" : `New task (slot ${slotNumber})`}</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close panel"
          className="text-zinc-500 hover:text-zinc-900"
        >
          ✕
        </button>
      </div>

      <label className="flex flex-col gap-1 text-sm font-medium">
        Title
        <input
          autoFocus
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={200}
          placeholder="e.g. Run 5k"
          className="rounded-xl border border-zinc-300 px-3 py-2 text-base font-normal outline-none focus:border-zinc-900"
        />
      </label>

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-medium">Time it takes</legend>
        <div className="flex flex-wrap items-center gap-2">
          {DURATION_PRESETS.map((minutes) => (
            <button
              key={minutes}
              type="button"
              aria-pressed={duration === minutes}
              onClick={() => setDuration(minutes)}
              className={chip(duration === minutes)}
            >
              {minutes} min
            </button>
          ))}
          <label className="flex items-center gap-1 text-sm">
            <input
              type="number"
              min={1}
              max={480}
              value={duration}
              onChange={(event) => setDuration(Number(event.target.value))}
              aria-label="Minutes"
              className="w-16 rounded-lg border border-zinc-300 px-2 py-1"
            />
            min
          </label>
        </div>
      </fieldset>

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-medium">How often</legend>
        <div className="flex flex-wrap gap-2">
          {FREQUENCIES.map(({ value, label }) => (
            <button
              key={value}
              type="button"
              aria-pressed={frequency === value}
              onClick={() => setFrequency(value)}
              className={chip(frequency === value)}
            >
              {label}
            </button>
          ))}
        </div>

        {frequency === "days" && (
          <div className="flex gap-1" role="group" aria-label="Days">
            {WEEKDAYS.map((name, day) => (
              <button
                key={name}
                type="button"
                aria-pressed={weekdays.includes(day)}
                aria-label={name}
                onClick={() => toggleDay(day)}
                className={`h-9 w-9 rounded-full text-sm ${
                  weekdays.includes(day) ? "bg-zinc-900 text-white" : "bg-zinc-100 hover:bg-zinc-200"
                }`}
              >
                {name[0]}
              </button>
            ))}
          </div>
        )}
        {frequency === "weekly" && (
          <label className="flex items-center gap-2 text-sm">
            <input
              type="number"
              min={1}
              max={6}
              value={timesPerWeek}
              onChange={(event) => setTimesPerWeek(Number(event.target.value))}
              className="w-16 rounded-lg border border-zinc-300 px-2 py-1"
            />
            times a week. Gyst puts it on your lightest days.
          </label>
        )}
        {frequency === "per_day" && (
          <label className="flex items-center gap-2 text-sm">
            <input
              type="number"
              min={2}
              max={20}
              value={timesPerDay}
              onChange={(event) => setTimesPerDay(Number(event.target.value))}
              className="w-16 rounded-lg border border-zinc-300 px-2 py-1"
            />
            times a day
          </label>
        )}
        {task?.frequency === "weekly" && frequency === "weekly" && (
          <p className="text-sm text-zinc-600">This week: {dayNames(task.scheduled_days)}</p>
        )}
      </fieldset>

      <label className="flex flex-col gap-1 text-sm font-medium">
        Notes <span className="font-normal text-zinc-500">(optional)</span>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={2000}
          rows={3}
          placeholder="What exactly to do"
          className="resize-none rounded-xl border border-zinc-300 px-3 py-2 text-base font-normal outline-none focus:border-zinc-900"
        />
      </label>

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={!canSave}
          className="rounded-xl bg-zinc-900 px-5 py-2 font-semibold text-white hover:bg-zinc-700 disabled:opacity-40"
        >
          {saving ? "Saving…" : "Save task"}
        </button>
        {missingDays && <span className="text-sm text-zinc-500">Pick at least one day</span>}
        {task && (
          <button
            type="button"
            onClick={() => void handleClear()}
            className="ml-auto text-sm text-red-600 hover:underline"
          >
            Clear task
          </button>
        )}
      </div>
    </form>
  );
}
