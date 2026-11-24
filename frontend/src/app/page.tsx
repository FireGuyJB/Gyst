// The home page. In Next.js's App Router, each folder under src/app is a URL
// route, and its page.tsx is what renders there ("/" here).
export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-4xl font-bold tracking-tight">Gyst</h1>
      <p className="text-lg text-zinc-600 dark:text-zinc-400">Get your stuff together.</p>
    </main>
  );
}
