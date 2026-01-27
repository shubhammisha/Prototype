import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn(
            "rounded-xl border border-white/20 bg-white/10 backdrop-blur-lg shadow-lg text-card-foreground",
            className
        )}
        {...props}
    />
))
Card.displayName = "Card"

export { Card }
