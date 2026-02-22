'use client';

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { useState } from "react";
import NotificationBell from "@/components/NotificationBell";
import NotificationCenter from "@/components/NotificationCenter";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

// Note: metadata must be exported from a Server Component
// We'll handle this differently

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  
  // Default user ID (in production, get from auth context)
  const userId = "e90cf88e-cb4b-4fe3-8098-6759d500b260";

  return (
    <html lang="en">
      <head>
        <title>PolicySentinel - AI Compliance Monitoring</title>
        <meta name="description" content="AI-powered policy compliance monitoring and violation detection" />
      </head>
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
                <a href="/reviews" className="hover:bg-blue-700 px-3 py-2 rounded-md">Reviews</a>
                <a href="/predictions" className="hover:bg-blue-700 px-3 py-2 rounded-md">Predictions</a>
                <a href="/feedback" className="hover:bg-blue-700 px-3 py-2 rounded-md">Feedback</a>
                <a href="/audit" className="hover:bg-blue-700 px-3 py-2 rounded-md">Audit</a>
                <a href="/data" className="hover:bg-blue-700 px-3 py-2 rounded-md">Data Explorer</a>
                
                {/* Notification Bell */}
                <div className="relative">
                  <NotificationBell
                    userId={userId}
                    onOpenNotifications={() => setNotificationsOpen(!notificationsOpen)}
                  />
                  <NotificationCenter
                    userId={userId}
                    isOpen={notificationsOpen}
                    onClose={() => setNotificationsOpen(false)}
                  />
                </div>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
