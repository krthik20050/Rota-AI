import * as React from "react"
import { cn } from "@/lib/utils"

export const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" }>(
  ({ className, variant = "primary", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-md h-12 px-6 text-sm font-medium transition-all duration-200 ease-in-out disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-accent text-background hover:brightness-110": variant === "primary",
            "bg-surface-200 text-text-primary border border-border hover:bg-surface-200/80": variant === "secondary",
            "text-text-secondary hover:text-text-primary hover:bg-surface-100": variant === "ghost",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
