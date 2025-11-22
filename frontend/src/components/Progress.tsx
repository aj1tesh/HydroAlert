interface ProgressProps {
  value: number
  color?: 'blue' | 'yellow' | 'orange' | 'red' | 'green'
  className?: string
}

const colorClasses = {
  blue: 'bg-blue-600',
  yellow: 'bg-yellow-500',
  orange: 'bg-orange-500',
  red: 'bg-red-600',
  green: 'bg-green-600',
}

export function Progress({ value, color = 'blue', className = '' }: ProgressProps) {
  const clampedValue = Math.min(Math.max(value, 0), 100)

  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div
        className={`h-2.5 rounded-full transition-all duration-300 ${colorClasses[color]}`}
        style={{ width: `${clampedValue}%` }}
      />
    </div>
  )
}

