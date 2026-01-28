"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, FileText, ChevronDown, ChevronUp, RefreshCw, Upload, Sparkles, User, Bot } from "lucide-react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface ChatInterfaceProps {
    filename: string
    onReset: () => void
}

interface Source {
    text: string
    source: string
    page: number
}

interface Message {
    role: "user" | "assistant"
    content: string
    sources?: Source[]
}

const suggestedQuestions = [
    "What is this document about?",
    "Summarize the key points",
    "What are the main conclusions?"
]

export function ChatInterface({ filename, onReset }: ChatInterfaceProps) {
    const [messages, setMessages] = React.useState<Message[]>([])
    const [input, setInput] = React.useState("")
    const [loading, setLoading] = React.useState(false)
    const scrollRef = React.useRef<HTMLDivElement>(null)

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1"

    React.useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: "smooth" })
        }
    }, [messages, loading])

    // Initial welcome message
    React.useEffect(() => {
        if (messages.length === 0) {
            // Optional: Could animate this in
        }
    }, [])

    const handleSubmit = async (e: React.FormEvent | null, questionOverride?: string) => {
        e?.preventDefault()
        const query = questionOverride || input
        if (!query.trim() || loading) return

        const userMsg: Message = { role: "user", content: query }
        setMessages((prev) => [...prev, userMsg])
        setInput("")
        setLoading(true)

        try {
            const res = await axios.post(`${API_URL}/chat`, { query: userMsg.content })

            const botMsg: Message = {
                role: "assistant",
                content: res.data.answer,
                sources: res.data.sources
            }
            setMessages((prev) => [...prev, botMsg])
        } catch (error) {
            setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex h-screen w-full bg-slate-50 overflow-hidden">

            {/* Sidebar (File details) */}
            <motion.div
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="w-80 bg-white border-r border-slate-200 p-6 flex flex-col hidden md:flex"
            >
                {/* File Icon Card */}
                <div className="w-full aspect-square bg-slate-50 rounded-3xl border border-slate-100 flex items-center justify-center mb-6 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-tr from-blue-50 to-indigo-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <div className="relative p-6 bg-white rounded-2xl shadow-sm border border-slate-100 text-blue-500">
                        <FileText size={48} strokeWidth={1.5} />
                    </div>
                </div>

                <h2 className="font-bold text-slate-800 text-lg leading-tight break-words mb-2">
                    {filename}
                </h2>

                <div className="flex gap-2 mb-8">
                    <span className="px-2 py-0.5 bg-red-50 text-red-500 text-xs font-bold rounded">PDF</span>
                    <span className="text-sm text-slate-400">4.6 KB</span>
                </div>

                <div className="space-y-4 text-sm">
                    <div className="flex justify-between py-3 border-b border-slate-50">
                        <span className="text-slate-400">Type</span>
                        <span className="font-medium text-slate-700">application/pdf</span>
                    </div>
                    <div className="flex justify-between py-3 border-b border-slate-50">
                        <span className="text-slate-400">Status</span>
                        <span className="font-medium text-green-500 flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-green-500" /> Ready
                        </span>
                    </div>
                </div>

                <div className="mt-auto">
                    <Button variant="outline" className="w-full gap-2 text-slate-600 h-11" onClick={onReset}>
                        <RefreshCw size={16} /> Upload New Document
                    </Button>
                </div>
            </motion.div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col h-full relative bg-white">
                {/* Header */}
                <header className="h-16 border-b border-slate-100 flex items-center px-8 bg-white/80 backdrop-blur-md sticky top-0 z-10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500 rounded-lg text-white shadow-lg shadow-blue-500/20">
                            <Sparkles size={18} />
                        </div>
                        <div>
                            <h1 className="font-semibold text-slate-800">Document Assistant</h1>
                            <p className="text-xs text-slate-500">Ask anything about your document</p>
                        </div>
                    </div>
                </header>

                {/* Chat Scroll Area */}
                <div className="flex-1 overflow-y-auto px-8 py-8 scroll-smooth">
                    <div className="max-w-3xl mx-auto space-y-8">

                        {/* Welcome / Empty State */}
                        {messages.length === 0 && (
                            <div className="mt-12 text-center">
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="text-slate-800 text-lg font-medium mb-8"
                                >
                                    I&apos;ve analyzed <span className="font-bold">{filename}</span>. Ask me anything about its contents!
                                </motion.div>

                                <div className="flex flex-wrap justify-center gap-3">
                                    {suggestedQuestions.map((q, i) => (
                                        <motion.button
                                            key={q}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.1 * i }}
                                            onClick={() => handleSubmit(null, q)}
                                            className="px-4 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 rounded-full text-sm font-medium transition-colors"
                                        >
                                            {q}
                                        </motion.button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={cn(
                                    "flex gap-4",
                                    msg.role === "assistant" ? "" : "flex-row-reverse"
                                )}
                            >
                                {/* Avatar */}
                                <div className={cn(
                                    "w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-sm",
                                    msg.role === "assistant" ? "bg-white border border-slate-100 text-blue-600" : "bg-blue-600 text-white"
                                )}>
                                    {msg.role === "assistant" ? <Bot size={20} /> : <User size={20} />}
                                </div>

                                {/* Bubble */}
                                <div className={cn(
                                    "max-w-[80%] rounded-2xl px-6 py-4 shadow-sm text-[15px] leading-relaxed",
                                    msg.role === "assistant"
                                        ? "bg-slate-50 text-slate-800 rounded-tl-none border border-slate-100"
                                        : "bg-blue-600 text-white rounded-tr-none shadow-blue-500/20"
                                )}>
                                    <div className="whitespace-pre-wrap font-medium">{msg.content}</div>

                                    {msg.sources && msg.sources.length > 0 && (
                                        <div className="mt-4 pt-4 border-t border-slate-200/60">
                                            <SourcesAccordion sources={msg.sources} />
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}

                        {loading && (
                            <div className="flex gap-4">
                                <div className="w-10 h-10 rounded-full bg-white border border-slate-100 flex items-center justify-center shrink-0">
                                    <Bot size={20} className="text-blue-600" />
                                </div>
                                <div className="bg-slate-50 rounded-2xl rounded-tl-none px-6 py-4 border border-slate-100 flex items-center gap-2">
                                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100" />
                                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200" />
                                </div>
                            </div>
                        )}
                        <div ref={scrollRef} />
                    </div>
                </div>

                {/* Input Footer */}
                <div className="p-6 bg-white shrink-0">
                    <div className="max-w-3xl mx-auto relative">
                        <form onSubmit={(e) => handleSubmit(e)} className="relative">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask a question about your document..."
                                className="w-full bg-white border border-slate-200 rounded-2xl pl-6 pr-14 py-4 text-[15px] focus:ring-2 focus:ring-blue-500/10 focus:border-blue-500 transition-all outline-none shadow-sm placeholder:text-slate-400 font-medium"
                            />
                            <button
                                type="submit"
                                disabled={!input.trim() || loading}
                                className="absolute right-2 top-2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-blue-500/20"
                            >
                                <Send size={18} />
                            </button>
                        </form>
                        <div className="text-center mt-3">
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-50 border border-slate-100 text-[10px] uppercase font-bold text-slate-400 tracking-wider hover:bg-slate-100 transition-colors cursor-default">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                                Powered by Groq Llama 3
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}

function SourcesAccordion({ sources }: { sources: Source[] }) {
    const [isOpen, setIsOpen] = React.useState(false)

    return (
        <div className="text-sm">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 w-full text-slate-500 hover:text-blue-600 transition-colors font-medium group"
            >
                <div className="p-1 rounded bg-white border border-slate-200 group-hover:border-blue-200 text-blue-500">
                    <FileText size={14} />
                </div>
                <span>View {sources.length} sources</span>
                {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden mt-3 space-y-2"
                    >
                        {sources.map((src, i) => (
                            <div key={i} className="bg-white p-3 rounded-xl border border-slate-200/60 shadow-sm text-xs text-slate-600 leading-relaxed">
                                <div className="flex justify-between font-semibold text-slate-800 mb-1">
                                    <span>Source Fragment {i + 1}</span>
                                    <span className="text-blue-500">Page {src.page}</span>
                                </div>
                                &quot;{src.text}&quot;
                            </div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
