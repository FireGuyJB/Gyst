// Gyst's color identity (docs/product/designs.md): the primary goal is yellow,
// and each supporting goal's color comes from its slot, so it never changes.
//
// Full class names are written out because Tailwind only generates classes it
// can find as complete strings in the code.
// shortcut: Tailwind shades close to the Figma names, swap in exact Figma values in the styling pass.

export const PRIMARY_COLOR = "bg-yellow-300";

/** Slot colors, indexed by position (0-7, clockwise from the top-left). */
export const SLOT_COLORS = [
  "bg-rose-300", // 0 rose
  "bg-teal-200", // 1 mint
  "bg-sky-300", // 2 blue
  "bg-orange-200", // 3 peach
  "bg-stone-300", // 4 taupe
  "bg-indigo-300", // 5 indigo
  "bg-pink-300", // 6 pink
  "bg-lime-200", // 7 sage
];
