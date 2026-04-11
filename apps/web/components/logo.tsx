import Image from "next/image";

type LogoMarkProps = {
  className?: string;
};

export function LogoMark({ className = "h-11 w-11" }: LogoMarkProps) {
  return (
    <span aria-hidden="true" className={`relative block overflow-hidden rounded-2xl ${className}`}>
      <Image src="/branding/zzge-logo.png" alt="" fill sizes="64px" className="object-contain" priority />
    </span>
  );
}
