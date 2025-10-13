import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import React from "react";
import { QueryProvider } from '@/providers/QueryProvider';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from "@/components/ui/sonner";


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: 'NIDS - Network Intrusion Detection System',
  description: 'Advanced AI-powered network security monitoring and threat detection platform',
  keywords: ['network security', 'intrusion detection', 'NIDS', 'threat detection', 'cybersecurity'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={geistSans.className}>
        <QueryProvider>
          <AuthProvider>
            {children}
            <Toaster richColors position="top-right"/>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
