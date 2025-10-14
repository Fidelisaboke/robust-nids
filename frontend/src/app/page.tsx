"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Shield,
  Lock,
  Activity,
  AlertTriangle,
  Network,
  ArrowRight,
} from "lucide-react";

export default function HomePage() {
  const features = [
    {
      icon: Shield,
      title: "Advanced Threat Detection",
      description: "Real-time monitoring and analysis of network traffic",
    },
    {
      icon: Lock,
      title: "Multi-Factor Authentication",
      description: "Enterprise-grade security with TOTP-based 2FA",
    },
    {
      icon: Activity,
      title: "Live Metrics",
      description: "Comprehensive dashboards and analytics",
    },
    {
      icon: AlertTriangle,
      title: "Instant Alerts",
      description: "Immediate notification of security threats",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="fixed top-0 w-full z-50 bg-slate-900/50 backdrop-blur-lg border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Network className="w-8 h-8 text-blue-400" />
            <span className="text-xl font-bold text-white">NIDS</span>
          </div>
          <Link
            href="/login"
            className="px-6 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all"
          >
            Sign In
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Network Security
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                Simplified
              </span>
            </h1>
            <p className="text-xl text-gray-300 mb-10 max-w-3xl mx-auto">
              Advanced intrusion detection system with real-time monitoring,
              threat intelligence, and comprehensive security analytics.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/login"
                className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all group"
              >
                Get Started
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center justify-center px-8 py-4 bg-slate-800/50 border border-slate-700 text-white font-semibold rounded-lg hover:bg-slate-800 transition-all"
              >
                Learn More
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Powerful Features
            </h2>
            <p className="text-gray-400 text-lg">
              Everything you need to protect your network infrastructure
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 hover:border-blue-500/50 transition-all"
              >
                <feature.icon className="w-12 h-12 text-blue-400 mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl p-12 text-center"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Secure Your Network?
            </h2>
            <p className="text-blue-100 text-lg mb-8">
              Join thousands of organizations protecting their infrastructure
              with NIDS
            </p>
            <Link
              href="/login"
              className="inline-flex items-center justify-center px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-gray-100 transition-all"
            >
              Sign In Now
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-slate-800">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p>&copy; 2025 NIDS. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
