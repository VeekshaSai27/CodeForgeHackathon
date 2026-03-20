interface ConfidenceBarProps {
  label: string;
  value: number; // 0-1
  colorClass?: string;
}

export function ConfidenceBar({ label, value, colorClass }: ConfidenceBarProps) {
  const percentage = Math.round(value * 100);
  const barColor = colorClass || (
    percentage >= 70 ? "bg-success" : percentage >= 40 ? "bg-warning" : "bg-destructive"
  );

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-foreground">{label}</span>
        <span className="tabular-nums text-muted-foreground">{percentage}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
