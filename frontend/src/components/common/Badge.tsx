import { cn } from '@/lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'secondary'
  size?: 'sm' | 'md'
  className?: string
}

export default function Badge({ 
  children, 
  variant = 'default', 
  size = 'md',
  className 
}: BadgeProps) {
  const variants = {
    default: 'bg-gray-700 text-gray-200',
    success: 'bg-green-900/50 text-green-400 border-green-700',
    warning: 'bg-yellow-900/50 text-yellow-400 border-yellow-700',
    danger: 'bg-red-900/50 text-red-400 border-red-700',
    info: 'bg-blue-900/50 text-blue-400 border-blue-700',
    secondary: 'bg-gray-800 text-gray-400 border-gray-600',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  )
}
