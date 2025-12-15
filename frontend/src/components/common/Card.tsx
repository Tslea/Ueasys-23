import React from 'react'
import { cn } from '@/lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode
  className?: string
  variant?: 'default' | 'glass' | 'interactive'
  hover?: boolean
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ children, className, variant = 'default', hover, ...props }, ref) => {
    const variants = {
      default: 'bg-fantasy-dark/80 backdrop-blur-sm border-gray-700/50',
      glass: 'bg-white/5 backdrop-blur-md border-white/10',
      interactive: 'bg-fantasy-dark/80 backdrop-blur-sm border-gray-700/50 hover:border-fantasy-accent/50 hover:shadow-fantasy-accent/20 transition-all duration-300 cursor-pointer'
    }

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-xl border shadow-xl',
          variants[variant],
          hover && 'hover:border-fantasy-accent/50 hover:shadow-fantasy-accent/20 transition-all duration-300 cursor-pointer',
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = 'Card'

export { Card }
export default Card

interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('mb-4', className)}>
      {children}
    </div>
  )
}

interface CardTitleProps {
  children: React.ReactNode
  className?: string
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-xl font-fantasy text-fantasy-gold', className)}>
      {children}
    </h3>
  )
}

interface CardContentProps {
  children: React.ReactNode
  className?: string
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn('text-gray-300', className)}>
      {children}
    </div>
  )
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn('mt-4 pt-4 border-t border-gray-700/50', className)}>
      {children}
    </div>
  )
}
