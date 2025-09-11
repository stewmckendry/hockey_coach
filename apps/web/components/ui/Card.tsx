'use client'

import { cn } from '@/lib/utils'
import type { CardProps } from '@/lib/types'

/**
 * Reusable Card component with hockey theming
 */
export function Card({ children, className, onClick }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-xl shadow-sm border border-neutral-200 p-6 transition-shadow duration-200',
        onClick && 'cursor-pointer hover:shadow-md',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export default Card
