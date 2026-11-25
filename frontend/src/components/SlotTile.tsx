// One of the 8 slots around the center of a grid. An empty slot shows "+";
// clicking it turns the tile into a text box. A filled slot shows its title,
// with small "edit" and "clear" buttons.
"use client";

import Link from "next/link";
import { type KeyboardEvent, useState } from "react";

type SlotTileProps = {
  /** Tailwind background class, from src/lib/colors.ts. */
  color: string;
  /** Used for screen readers, e.g. "Supporting goal 3". */
  label: string;
  /** The saved title, or undefined for an empty slot. */
  title?: string;
  /** Save a title. Resolves true if it saved (false keeps the text box open). */
  onSave: (title: string) => Promise<boolean>;
  onClear: () => Promise<void>;
  /** If set, clicking a filled tile opens this page instead of editing. */
  href?: string;
};

export function SlotTile({ color, label, title, onSave, onClear, href }: SlotTileProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  function startEditing() {
    setDraft(title ?? "");
    setEditing(true);
  }

  async function save() {
    if (busy) return;
    // An empty slot clicked by accident: just close it again.
    if (title === undefined && draft.trim() === "") {
      setEditing(false);
      return;
    }
    if (draft === title) {
      setEditing(false);
      return;
    }
    setBusy(true);
    const saved = await onSave(draft);
    setBusy(false);
    if (saved) setEditing(false);
  }

  async function clear() {
    if (!window.confirm(`Clear "${title}"?`)) return;
    setBusy(true);
    await onClear();
    setBusy(false);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter") {
      event.preventDefault(); // Enter saves instead of adding a new line
      void save();
    } else if (event.key === "Escape") {
      setEditing(false);
    }
  }

  const tile = `relative flex h-full w-full items-center justify-center rounded-3xl ${color} p-4 text-center`;

  if (editing) {
    return (
      <div className={tile}>
        <textarea
          autoFocus
          value={draft}
          disabled={busy}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => void save()}
          maxLength={200}
          aria-label={label}
          placeholder="Type, then Enter"
          className="h-full w-full resize-none rounded-2xl bg-white/60 p-3 text-center text-lg font-semibold text-zinc-900 outline-none placeholder:text-zinc-500 focus:ring-2 focus:ring-zinc-900/30"
        />
      </div>
    );
  }

  if (title === undefined) {
    return (
      <button
        onClick={startEditing}
        aria-label={`Add ${label.toLowerCase()}`}
        className={`${tile} text-7xl font-light text-white hover:brightness-95`}
      >
        +
      </button>
    );
  }

  const text = <span className="text-lg font-semibold break-words text-zinc-900">{title}</span>;
  return (
    <div className={`${tile} group`}>
      {href ? (
        <Link href={href} className="flex h-full w-full items-center justify-center">
          {text}
        </Link>
      ) : (
        <button
          onClick={startEditing}
          aria-label={`Edit ${title}`}
          className="flex h-full w-full items-center justify-center"
        >
          {text}
        </button>
      )}
      {/* Small actions in the corner. Always reachable by keyboard (Tab). */}
      <div className="absolute top-2 right-2 flex gap-1 opacity-60 group-hover:opacity-100 focus-within:opacity-100">
        {href && (
          <button
            onClick={startEditing}
            aria-label={`Rename ${title}`}
            title="Rename"
            className="rounded-full bg-white/70 px-2 py-0.5 text-sm text-zinc-800 hover:bg-white"
          >
            ✎
          </button>
        )}
        <button
          onClick={() => void clear()}
          disabled={busy}
          aria-label={`Clear ${title}`}
          title="Clear"
          className="rounded-full bg-white/70 px-2 py-0.5 text-sm text-zinc-800 hover:bg-white"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
