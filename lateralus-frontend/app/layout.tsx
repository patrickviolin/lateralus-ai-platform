import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Lateralus",
  description: "Weather agent with streaming tool-call UI",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body suppressHydrationWarning className="min-h-full flex flex-col">
        {children}
        <Script id="remove-extension-hydration-noise" strategy="beforeInteractive">
          {`
            document.querySelectorAll('[bis_skin_checked]').forEach(function (node) {
              node.removeAttribute('bis_skin_checked');
            });
          `}
        </Script>
      </body>
    </html>
  );
}
