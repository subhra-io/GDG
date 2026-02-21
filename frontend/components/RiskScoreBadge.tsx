"use client";

interface RiskScoreBadgeProps {
  score: number;
  level?: string;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

export default function RiskScoreBadge({ 
  score, 
  level,
  showLabel = true,
  size = "md" 
}: RiskScoreBadgeProps) {
  // Determine risk level from score if not provided
  const riskLevel = level || getRiskLevel(score);
  
  // Color mapping
  const colorClasses = {
    Low: "bg-green-100 text-green-800 border-green-300",
    Medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
    High: "bg-orange-100 text-orange-800 border-orange-300",
    Critical: "bg-red-100 text-red-800 border-red-300",
  };
  
  // Size mapping
  const sizeClasses = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
    lg: "text-base px-4 py-1.5",
  };
  
  const colorClass = colorClasses[riskLevel as keyof typeof colorClasses] || colorClasses.Low;
  const sizeClass = sizeClasses[size];
  
  return (
    <span 
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${colorClass} ${sizeClass}`}
      title={`Risk Score: ${score}/100`}
    >
      <span className="font-bold">{score}</span>
      {showLabel && <span>{riskLevel}</span>}
    </span>
  );
}

function getRiskLevel(score: number): string {
  if (score >= 76) return "Critical";
  if (score >= 51) return "High";
  if (score >= 26) return "Medium";
  return "Low";
}
