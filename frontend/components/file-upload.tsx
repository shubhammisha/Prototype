"use client"

import * as React from "react"
import { useDropzone } from "react-dropzone"
import { motion, AnimatePresence } from "framer-motion"
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface FileUploadProps {
    onUploadComplete: (filename: string) => void
}

const steps = [
    { id: 1, label: "Extracting text" },
    { id: 2, label: "Analyzing content" },
    { id: 3, label: "Building index" },
]

export function FileUpload({ onUploadComplete }: FileUploadProps) {
    const [uploadStatus, setUploadStatus] = React.useState<"idle" | "uploading" | "success" | "error">("idle")
    const [errorMessage, setErrorMessage] = React.useState("")
    const [progress, setProgress] = React.useState(0)
    const [activeStep, setActiveStep] = React.useState(1)
    const [filename, setFilename] = React.useState("")

    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1"

    const onDrop = React.useCallback(async (acceptedFiles: File[]) => {
        const file = acceptedFiles[0]
        if (!file) return

        setUploadStatus("uploading")
        setProgress(0)
        setActiveStep(1)
        setFilename(file.name)

        // Simulate multi-step progress visibility
        const stepTimer = setInterval(() => {
            setActiveStep((prev) => {
                if (prev < 3) return prev + 1
                return prev
            })
        }, 1500)

        const progressTimer = setInterval(() => {
            setProgress((old) => {
                if (old >= 95) return 95
                return old + 2
            })
        }, 100)

        try {
            const formData = new FormData()
            formData.append("file", file)

            // Real upload
            await axios.post(`${API_URL}/documents/ingest`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            })

            clearInterval(stepTimer)
            clearInterval(progressTimer)
            setProgress(100)
            setActiveStep(3)
            setUploadStatus("success")

            // Delay before switching to chat
            setTimeout(() => {
                onUploadComplete(file.name)
            }, 1000)

        } catch (error: any) {
            clearInterval(stepTimer)
            clearInterval(progressTimer)
            setUploadStatus("error")
            setErrorMessage(error.message || "Upload failed")
        }
    }, [API_URL, onUploadComplete])

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { "application/pdf": [".pdf"], "text/plain": [".txt"] },
        maxFiles: 1,
    })

    return (
        <div className="w-full max-w-xl mx-auto">
            <AnimatePresence mode="wait">
                {uploadStatus === "idle" ? (
                    <motion.div
                        key="dropzone"
                        {...getRootProps()}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className={cn(
                            "relative group cursor-pointer flex flex-col items-center justify-center w-full h-80 rounded-3xl border border-dashed transition-all duration-300 bg-white/50 backdrop-blur-sm overflow-hidden",
                            isDragActive ? "border-blue-500 bg-blue-50/50 scale-[1.02]" : "border-slate-300 hover:border-blue-400 hover:bg-slate-50/50",
                        )}
                    >
                        <input {...getInputProps()} />
                        <div className={cn(
                            "p-5 rounded-2xl bg-slate-50 text-slate-400 mb-6 transition-transform duration-300 shadow-sm",
                            isDragActive && "scale-110 text-blue-500 bg-blue-50"
                        )}>
                            <UploadCloud size={40} />
                        </div>

                        <h3 className="text-lg font-semibold text-slate-800 mb-1">
                            Drag & drop your document
                        </h3>
                        <p className="text-sm text-blue-500 font-medium mb-6 hover:underline">
                            or browse files
                        </p>

                        {/* Format Badges */}
                        <div className="flex gap-2">
                            {["PDF", "DOCX", "TXT", "Images"].map((fmt) => (
                                <span key={fmt} className={cn(
                                    "px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider",
                                    fmt === "PDF" && "bg-red-50 text-red-500",
                                    fmt === "DOCX" && "bg-blue-50 text-blue-500",
                                    fmt === "TXT" && "bg-slate-100 text-slate-500",
                                    fmt === "Images" && "bg-green-50 text-green-500",
                                )}>
                                    {fmt}
                                </span>
                            ))}
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="processing"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full bg-white rounded-3xl shadow-xl p-8 border border-slate-100"
                    >
                        {/* Header */}
                        <div className="flex items-start gap-4 mb-6">
                            <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                                <FileText size={24} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-slate-900 truncate pr-4">{filename}</h3>
                                <p className="text-sm text-slate-500 mt-0.5">Processing document...</p>
                            </div>
                            {(uploadStatus === "uploading" || uploadStatus === "success") && (
                                <div className="w-5 h-5">
                                    {uploadStatus === "success" ? (
                                        <CheckCircle2 className="text-green-500 w-full h-full" />
                                    ) : (
                                        <Loader2 className="text-blue-500 w-full h-full animate-spin" />
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Progress Bar */}
                        <div className="mb-2 flex justify-between text-xs font-medium text-slate-500">
                            <span>Processing</span>
                            <span>{Math.round(progress)}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden mb-8">
                            <motion.div
                                className="h-full bg-blue-600 rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                transition={{ ease: "easeInOut" }}
                            />
                        </div>

                        {/* Steps Checklist */}
                        <div className="space-y-3">
                            {steps.map((step) => {
                                const isCompleted = activeStep > step.id || uploadStatus === "success";
                                const isCurrent = activeStep === step.id && uploadStatus !== "success";
                                const isPending = activeStep < step.id;

                                return (
                                    <div key={step.id} className="flex items-center gap-3 text-sm">
                                        <div className={cn(
                                            "w-5 h-5 rounded-full flex items-center justify-center transition-colors duration-300",
                                            isCompleted ? "bg-green-500 text-white" : isCurrent ? "bg-blue-500 text-white" : "bg-slate-100 text-slate-300"
                                        )}>
                                            {isCompleted ? <CheckCircle2 size={12} strokeWidth={3} /> : (
                                                isCurrent ? <Loader2 size={12} className="animate-spin" /> : <div className="w-1.5 h-1.5 rounded-full bg-current" />
                                            )}
                                        </div>
                                        <span className={cn(
                                            "font-medium transition-colors duration-300",
                                            isCompleted || isCurrent ? "text-slate-700" : "text-slate-400"
                                        )}>
                                            {step.label}
                                        </span>
                                    </div>
                                )
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
