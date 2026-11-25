// The 3x3 grid used at every level of the chart: one tile in the center (the
// goal one level up) and 8 slots around it.
import type { ReactNode } from "react";

// Slots are numbered clockwise from the top-left, but a CSS grid fills cells
// left to right, top to bottom. This is the slot shown in each cell, in that
// order ("center" is the middle cell):
//   0 1 2
//   7 C 3
//   6 5 4
const CELLS = [0, 1, 2, 7, "center", 3, 6, 5, 4] as const;

type GridProps = {
  center: ReactNode;
  /** Exactly 8 tiles, one per slot position 0-7. */
  slots: ReactNode[];
};

export function Grid({ center, slots }: GridProps) {
  return (
    <div className="grid w-full max-w-[min(42rem,75vh)] grid-cols-3 gap-4">
      {CELLS.map((cell) => (
        <div key={cell} className="aspect-square">
          {cell === "center" ? center : slots[cell]}
        </div>
      ))}
    </div>
  );
}
