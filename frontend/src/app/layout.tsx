import type { Metadata, Viewport } from "next";
import { Inter, Cinzel } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const cinzel = Cinzel({
  subsets: ["latin"],
  variable: "--font-cinzel",
  display: "swap",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "AstroMind AI — Deterministic Vedic Astrology & Grounded AI Intelligence",
  description:
    "Production-ready Vedic astrology platform powered by high-precision ephemeris calculations, Lahiri ayanamsa, Whole-Sign houses, and source-grounded ethical AI analysis.",
  keywords: [
    "Vedic Astrology",
    "Jyotish",
    "Kundli",
    "Rashi Chart",
    "Navamsa",
    "Vimshottari Dasha",
    "AstroMind AI",
  ],
  authors: [{ name: "AstroMind Engineering Team" }],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${cinzel.variable} dark`}>
      <body className="bg-background text-foreground min-h-screen flex flex-col selection:bg-gold-500/30 selection:text-gold-300">
        {children}
      </body>
    </html>
  );
}
