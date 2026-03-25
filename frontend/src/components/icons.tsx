import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

function baseProps(props: IconProps) {
  return {
    fill: "none",
    stroke: "currentColor",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    strokeWidth: 1.8,
    viewBox: "0 0 24 24",
    ...props
  };
}

export function BrandIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M4 16l4.5-6 4.5 4 7-10" />
      <circle cx="4" cy="16" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="8.5" cy="10" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="13" cy="14" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="20" cy="4" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function SunIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2.5M12 19.5V22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M2 12h2.5M19.5 12H22M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" />
    </svg>
  );
}

export function MoonIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M20 14.5A7.5 7.5 0 119.5 4 6 6 0 0020 14.5z" />
    </svg>
  );
}

export function SearchIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <circle cx="11" cy="11" r="6.5" />
      <path d="M20 20l-4-4" />
    </svg>
  );
}

export function ArrowRightIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M5 12h14" />
      <path d="M13 6l6 6-6 6" />
    </svg>
  );
}

export function TrophyIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M8 4h8v3a4 4 0 01-8 0V4z" />
      <path d="M8 6H5a2 2 0 000 4h2M16 6h3a2 2 0 010 4h-2M12 11v4M9 19h6" />
    </svg>
  );
}

export function TagsIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M11 4H5v6l8 8a2 2 0 002.8 0l3.2-3.2a2 2 0 000-2.8L11 4z" />
      <circle cx="8.5" cy="8.5" r="1" />
    </svg>
  );
}

export function BarChartIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M4 20V10" />
      <path d="M10 20V4" />
      <path d="M16 20v-7" />
      <path d="M22 20v-12" />
    </svg>
  );
}

export function SparklesIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3z" />
      <path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9L19 15z" />
      <path d="M5 14l.7 1.7L7.5 16l-1.8.7L5 18.5l-.7-1.8L2.5 16l1.8-.3L5 14z" />
    </svg>
  );
}

export function ActivityIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M3 12h4l2-5 4 10 2-5h6" />
    </svg>
  );
}

export function UserIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20a7 7 0 0114 0" />
    </svg>
  );
}

export function RefreshIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <path d="M20 5v5h-5" />
      <path d="M4 19v-5h5" />
      <path d="M19 10a7 7 0 00-12-3L4 10" />
      <path d="M5 14a7 7 0 0012 3l3-3" />
    </svg>
  );
}

export function TableIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="M3 10h18M8 5v14M16 5v14" />
    </svg>
  );
}

export function TargetIcon(props: IconProps) {
  return (
    <svg {...baseProps(props)}>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </svg>
  );
}
