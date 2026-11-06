// App shell for every route: IBM Plex Sans, sidebar and page frame.
import type { Metadata } from "next";
import { IBM_Plex_Sans } from "next/font/google";

import { Sidebar } from "@/components/ui/layout/Sidebar";

import "./globals.css";

const plex = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-plex" });

export const metadata: Metadata = {
  title: "Roofing Lead Intel",
  description: "Roofing contractor prospects and saved leads for distributor sales representatives.",
};

/** Root layout: sidebar and main content area. */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={plex.variable}>
      <body className="font-sans">
        <div className="flex min-h-screen flex-col gap-4 p-3 md:flex-row md:p-4">
          <Sidebar />
          <main className="min-w-0 flex-1 rounded-md border border-line bg-surface/60 px-4 py-5 shadow-card md:px-6">
            <div className="mx-auto max-w-[1320px] space-y-4">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}
