"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { FileUpload } from "@/components/file-upload"
import { ChatInterface } from "@/components/chat-interface"
import { ShieldCheck } from "lucide-react"

export default function Home() {
  const [view, setView] = React.useState<"upload" | "chat">("upload")
  const [filename, setFilename] = React.useState("")

  const handleUploadComplete = (name: string) => {
    setFilename(name)
    setView("chat")
  }

  const handleReset = () => {
    setView("upload")
    setFilename("")
  }

  return (
    <main className="min-h-screen bg-slate-50 selection:bg-blue-100 font-sans">

      <AnimatePresence mode="wait">
        {view === "upload" ? (
          <motion.div
            key="upload-view"
            exit={{ opacity: 0, x: -20 }}
            className="flex min-h-screen flex-col items-center justify-center relative overflow-hidden"
          >
            {/* Background Decoration */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-100/50 blur-[120px]" />
              <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-100/50 blur-[120px]" />
            </div>

            <div className="z-10 w-full max-w-5xl px-4 flex flex-col items-center">

              {/* Header */}
              <div className="text-center mb-16">
                <div className="flex items-center justify-center space-x-3 mb-6">
                  <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-600/20">
                    <FileTextIcon />
                  </div>
                  <div className="text-left">
                    <h1 className="text-2xl font-bold text-slate-900 leading-none">DocuChat AI</h1>
                    <p className="text-sm text-slate-500 font-medium">Intelligent Document Assistant</p>
                  </div>
                </div>

                <h2 className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight mb-4">
                  Upload your document
                </h2>
                <p className="text-lg text-slate-500 max-w-lg mx-auto">
                  Get instant answers from any document. Simply upload and start asking questions.
                </p>
              </div>

              <FileUpload onUploadComplete={handleUploadComplete} />

              <div className="mt-12">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-50 border border-green-100 text-green-700 text-sm font-medium">
                  <ShieldCheck size={16} />
                  <span>Your data stays private</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 ml-1 animate-pulse" />
                </div>
              </div>

            </div>
          </motion.div>
        ) : (
          <motion.div
            key="chat-view"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="h-screen w-full"
          >
            <ChatInterface filename={filename} onReset={handleReset} />
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  )
}

function FileTextIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
      <line x1="10" x2="8" y1="9" y2="9" />
    </svg>
  )
}
