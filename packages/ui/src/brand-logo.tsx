type BrandLogoProps = {
  href?: string;
  imageSrc?: string;
  alt?: string;
};

export function BrandLogo({
  href = "/",
  imageSrc = "/brand/logo-header.png",
  alt = "LateSight"
}: BrandLogoProps) {
  return (
    <a className="brand-logo" href={href} aria-label={alt}>
      <img src={imageSrc} alt={alt} />
    </a>
  );
}
