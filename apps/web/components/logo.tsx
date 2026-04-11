import Image from "next/image";

type LogoMarkProps = {
  className?: string;
};

export function LogoMark({ className = "h-11 w-11" }: LogoMarkProps) {
  return (
    <span aria-hidden="true" className={`relative block overflow-hidden rounded-2xl ${className}`}>
      <Image src="/branding/zzge-logo-mark.png" alt="" fill sizes="64px" className="object-contain" priority />
    </span>
  );
}

type LogoFullProps = {
  className?: string;
  priority?: boolean;
};

export function LogoFull({ className = "h-12 w-auto", priority = false }: LogoFullProps) {
  return (
    <span aria-hidden="true" className={`relative block ${className}`}>
      <Image src="/branding/zzge-logo-full.png" alt="" fill sizes="320px" className="object-contain object-left" priority={priority} />
    </span>
  );
}
