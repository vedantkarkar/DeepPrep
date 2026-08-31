import type { Metadata } from "next";
import "./globals.css";
import { AppProvider } from "@/lib/context/AppContext";
import { Header } from "@/components/layout/Header";

export const metadata: Metadata = {
  title: "DeepPrep — AI Role-Readiness Platform for Engineering Candidates",
  description: "Measure your engineering preparation against the actual requirements of the role you want using deterministic, evidence-backed readiness analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#080c14] text-slate-100 min-h-screen flex flex-col">
        <AppProvider>
          <Header />
          <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
            <p>DeepPrep · Deterministic Role-Readiness Intelligence · Engineering Career Assessment</p>
          </footer>
        </AppProvider>
      </body>
    </html>
  );
}
