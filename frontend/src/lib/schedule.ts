// Turning a task's frequency into words, e.g. "Mon Wed Fri" or "2× / week".
import type { Task, TaskInput } from "@/lib/api";

export const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]; // index = weekday

export function dayNames(days: number[]): string {
  return days.map((day) => WEEKDAYS[day]).join(" ");
}

/** A short line for a task tile: "30 min · Every day". */
export function describeSchedule(task: TaskInput | Task): string {
  const often = {
    daily: "Every day",
    days: dayNames(task.weekdays),
    weekly: `${task.times_per_week}× / week`,
    per_day: `${task.times_per_day}× / day`,
  }[task.frequency];
  return `${task.duration_minutes} min · ${often}`;
}
