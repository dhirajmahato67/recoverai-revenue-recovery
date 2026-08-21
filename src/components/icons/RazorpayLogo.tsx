import React from "react";

interface RazorpayIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string;
  size?: number;
}

/**
 * Official Razorpay Logomark SVG component.
 * Sourced from official brand assets & vector specification.
 */
export function RazorpayIcon({
  className = "w-4 h-4",
  size,
  ...props
}: RazorpayIconProps) {
  return (
    <svg
      role="img"
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      width={size}
      height={size}
      aria-label="Razorpay"
      {...props}
    >
      <title>Razorpay</title>
      <path d="M22.436 0l-11.91 7.773-1.174 4.276 6.625-4.297L11.65 24h4.391l6.395-24zM14.26 10.098L3.389 17.166 1.564 24h9.008l3.688-13.902Z" />
    </svg>
  );
}
