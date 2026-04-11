type LogoMarkProps = {
  className?: string;
};

export function LogoMark({ className = "h-11 w-11" }: LogoMarkProps) {
  return (
    <svg viewBox="0 0 88 88" aria-hidden="true" className={className}>
      <rect x="4" y="4" width="80" height="80" rx="24" fill="#0F172A" />
      <circle cx="63" cy="24" r="9" fill="#60A5FA" />
      <path
        d="M24 48.5C24 36.6 33.4 27 45.2 27H55c9.8 0 17.8 7.7 17.8 17.1 0 10.5-8.5 19-20.3 19H42.1L29.4 72l3.2-11.2C27.1 58.9 24 54.6 24 48.5Z"
        fill="#F8FAFC"
      />
      <path
        d="M34 34h16.5c3.8 0 6.8 2.9 6.8 6.5s-3 6.5-6.8 6.5H42v4.8h14.4c3.8 0 6.8 2.9 6.8 6.5 0 3.5-3 6.4-6.8 6.4H34V34Zm8 12h8.2c1.5 0 2.7-1.1 2.7-2.5S51.7 41 50.2 41H42v5Z"
        fill="#2563EB"
      />
      <path
        d="M25.5 56.8c5.2-.6 9.8 1.4 13.8 5.8-5.8.5-10.5 3-14.3 7.7-.8-5-.6-9.5.5-13.5Z"
        fill="#93C5FD"
      />
    </svg>
  );
}
