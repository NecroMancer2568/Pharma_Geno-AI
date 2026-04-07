'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Dna, Pill, FileText, Zap, Shield, Clock } from 'lucide-react';

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-6 py-24 sm:py-32 lg:px-8">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1.5s' }} />
        </div>

        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex justify-center mb-6">
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass text-sm font-medium text-cyan-400">
                <Dna className="w-4 h-4" />
                Powered by AI & PharmGKB Science
              </span>
            </div>
            
            <h1 className="text-5xl sm:text-7xl font-bold tracking-tight mb-6">
              <span className="text-gradient">PharmGeno</span>{' '}
              <span className="text-white">AI</span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-slate-300 mb-4 max-w-2xl mx-auto">
              Upload your DNA. Enter your medications.
              <br />
              <span className="text-cyan-400 font-semibold">Get your personalized drug compatibility report in 60 seconds.</span>
            </p>
            
            <p className="text-slate-400 mb-10 max-w-xl mx-auto">
              2 out of 5 prescriptions fail because they're based on population averages. 
              Your genes are unique — your medicine should be too.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link
              href="/upload"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40"
            >
              <FileText className="w-5 h-5" />
              Upload Your DNA
            </Link>
            
            <Link
              href="/upload?demo=true"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold rounded-xl glass hover:bg-white/10 transition-all border border-white/20"
            >
              <Zap className="w-5 h-5 text-yellow-400" />
              Try Demo
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Three simple steps to personalized pharmacogenomics insights
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Dna,
                title: '1. Upload DNA',
                description: 'Upload your raw data file from 23andMe or AncestryDNA. We extract only pharmacogenomic variants.',
                color: 'cyan'
              },
              {
                icon: Pill,
                title: '2. Enter Medications',
                description: 'Add your current medications using our autocomplete search powered by RxNorm.',
                color: 'blue'
              },
              {
                icon: FileText,
                title: '3. Get Report',
                description: 'Receive a detailed compatibility report with risk scores, explanations, and alternatives.',
                color: 'purple'
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="gradient-border p-8 text-center"
              >
                <div className={`inline-flex p-4 rounded-xl bg-${feature.color}-500/10 mb-6`}>
                  <feature.icon className={`w-8 h-8 text-${feature.color}-400`} />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="px-6 py-24 lg:px-8 bg-slate-800/50">
        <div className="mx-auto max-w-6xl">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            {[
              {
                icon: Clock,
                stat: '60 sec',
                label: 'Report Generation'
              },
              {
                icon: Shield,
                stat: '100%',
                label: 'Privacy Protected'
              },
              {
                icon: Dna,
                stat: '50+',
                label: 'Genes Analyzed'
              }
            ].map((item, index) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="glass rounded-2xl p-8"
              >
                <item.icon className="w-8 h-8 text-cyan-400 mx-auto mb-4" />
                <div className="text-4xl font-bold text-gradient mb-2">{item.stat}</div>
                <div className="text-slate-400">{item.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-6">
              Ready to discover your drug compatibility?
            </h2>
            <p className="text-slate-400 mb-8 max-w-2xl mx-auto">
              Pharmacogenomics testing typically costs $500+ through labs. 
              We make it accessible, instant, and science-backed.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/25"
            >
              Get Started Free
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 border-t border-white/10">
        <div className="mx-auto max-w-6xl text-center text-slate-500 text-sm">
          <p className="mb-4">
            <strong className="text-slate-400">Medical Disclaimer:</strong> PharmGeno AI provides educational information only. 
            Always consult your healthcare provider before making medication decisions.
          </p>
          <p>© 2024 PharmGeno AI. Built for hackathon demonstration.</p>
        </div>
      </footer>
    </main>
  );
}
