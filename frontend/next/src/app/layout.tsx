import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "3Brown1Blue",
  description:
    "An educational AI platform for visualizing and learning new concepts.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" style={{ width: "100%", height: "100%" }}>
      <body
        className={inter.className}
        style={{ width: "100%", height: "100%" }}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          forcedTheme="light"
          disableTransitionOnChange={false}
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
