"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { CheckCircle2, Mail, Clock } from "lucide-react";

export default function RegisterSuccessPage() {
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-500/20 mb-4">
          <CheckCircle2 className="h-8 w-8 text-green-400" />
        </div>
        <h2 className="text-3xl font-bold text-white">
          Registration Successful!
        </h2>
        <p className="text-gray-400 mt-2">
          Your account has been created and is pending admin approval
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="space-y-6"
      >
        {/* Information Cards */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-4">
          <div className="flex items-center space-x-3">
            <Mail className="h-5 w-5 text-blue-400" />
            <div>
              <h3 className="font-medium text-white">Check Your Email</h3>
              <p className="text-sm text-gray-400">
                We&apos;ve sent a confirmation email with your registration
                details
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Clock className="h-5 w-5 text-amber-400" />
            <div>
              <h3 className="font-medium text-white">Pending Approval</h3>
              <p className="text-sm text-gray-400">
                Your account requires admin approval before you can access the
                system
              </p>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-6">
          <h3 className="font-medium text-white mb-2">What happens next?</h3>
          <ul className="text-sm text-gray-400 space-y-1 list-disc list-inside">
            <li>Our admin team will review your registration</li>
            <li>You&apos;ll receive an email once your account is activated</li>
            <li>Typical approval time: 1-2 business days</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <Link
            href="/login"
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-lg hover:from-blue-600 hover:to-cyan-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all block text-center"
          >
            Return to Login
          </Link>

          <Link
            href="/contact"
            className="w-full py-3 px-4 bg-slate-700 text-white font-medium rounded-lg hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all block text-center text-sm"
          >
            Contact Support
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
