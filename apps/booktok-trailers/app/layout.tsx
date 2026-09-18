import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BookTok Trailer Factory",
  description: "8 cinematic BookTok trailers per week from any Amazon URL.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
