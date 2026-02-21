import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "PolicySentinel - AI Compliance Monitoring",
  description: "AI-powered policy compliance monitoring and violation detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        <nav className="bg-blue-600 text-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <a href="/" className="text-xl font-bold">PolicySentinel</a>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="hover:bg-blue-700 px-3 py-2 rounded-md">Dashboard</a>
                <a href="/policies" className="hover:bg-blue-700 px-3 py-2 rounded-md">Policies</a>
                <a href="/violations" className="hover:bg-blue-700 px-3 py-2 rounded-md">Violations</a>
                <a href="/data" className="hover:bg-blue-700 px-3 py-2 rounded-md">Data Explorer</a>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
