'use client'

import { forwardRef } from 'react'
import { cn } from '@/lib/utils'
import type { ButtonProps } from '@/lib/types'

/**
 * Reusable Button component with hockey theming
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, onClick, disabled = false, variant = 'primary', size = 'md', className, type = 'button', ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
    
    const variants = {
      primary: 'bg-hockey-blue hover:bg-hockey-blue-light text-white focus:ring-hockey-blue',
      secondary: 'bg-white hover:bg-neutral-50 text-hockey-blue border border-hockey-blue focus:ring-hockey-blue',
      ghost: 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 focus:ring-neutral-500'
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm rounded-md',
      md: 'px-4 py-2 text-sm rounded-lg',
      lg: 'px-6 py-3 text-base rounded-lg'
    }

    return (
      <button
        ref={ref}
        type={type}
        onClick={onClick}
        disabled={disabled}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export default Button
