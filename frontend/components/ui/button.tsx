import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

// Since I didn't install cva/radix, I'll use a simpler implementation for now to avoid installing more deps if possible, 
// OR I should just install them. Standard shadcn uses them. 
// Let's stick to simple props for speed, or install cva if needed. 
// Actually, I can write a simple component without CVA for now.

const Button = React.forwardRef<
    HTMLButtonElement,
    React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "outline" | "ghost" }
>(({ className, variant = "default", ...props }, ref) => {
    const variants = {
        default: "bg-blue-600 text-white hover:bg-blue-700 shadow-md",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
    }

    return (
        <button
            ref={ref}
            className={cn(
                "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2",
                variants[variant],
                className
            )}
            {...props}
        />
    )
})
Button.displayName = "Button"

export { Button }
