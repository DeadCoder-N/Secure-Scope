interface LogoProps {
  size?: number;
  className?: string;
}

export default function SecureScopeLogo({ size = 28, className = '' }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M16 2L4 7v9c0 6.5 5.1 12.6 12 14 6.9-1.4 12-7.5 12-14V7L16 2z"
        fill="rgba(6,182,212,0.15)"
        stroke="#06b6d4"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <line x1="10" y1="16" x2="14" y2="16" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="18" y1="16" x2="22" y2="16" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="16" y1="10" x2="16" y2="14" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="16" y1="18" x2="16" y2="22" stroke="#06b6d4" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="16" cy="16" r="1.5" fill="#06b6d4" />
      <circle cx="16" cy="16" r="3.5" stroke="#06b6d4" strokeWidth="1" fill="none" opacity="0.6" />
    </svg>
  );
}
