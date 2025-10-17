/**
 * Image optimization utilities
 */

interface ImageLoadOptions {
  loading?: 'lazy' | 'eager'
  decoding?: 'async' | 'sync' | 'auto'
  fetchPriority?: 'high' | 'low' | 'auto'
}

/**
 * Create optimized image attributes
 */
export function getOptimizedImageAttrs(
  src: string,
  alt: string,
  options: ImageLoadOptions = {}
): Record<string, string> {
  const {
    loading = 'lazy',
    decoding = 'async',
    fetchPriority = 'auto'
  } = options

  return {
    src,
    alt,
    loading,
    decoding,
    fetchpriority: fetchPriority
  }
}

/**
 * Preload critical images
 */
export function preloadImage(src: string, as: 'image' = 'image'): void {
  const link = document.createElement('link')
  link.rel = 'preload'
  link.as = as
  link.href = src
  document.head.appendChild(link)
}

/**
 * Lazy load image with intersection observer
 */
export function lazyLoadImage(img: HTMLImageElement, src: string): void {
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          img.src = src
          img.classList.add('loaded')
          observer.unobserve(img)
        }
      })
    })
    observer.observe(img)
  } else {
    // Fallback for browsers without IntersectionObserver
    img.src = src
  }
}

/**
 * Get responsive image srcset
 */
export function getResponsiveSrcSet(
  basePath: string,
  sizes: number[] = [320, 640, 960, 1280, 1920]
): string {
  return sizes
    .map((size) => {
      const ext = basePath.split('.').pop()
      const path = basePath.replace(`.${ext}`, `_${size}w.${ext}`)
      return `${path} ${size}w`
    })
    .join(', ')
}

/**
 * Convert image to WebP if supported
 */
export function supportsWebP(): Promise<boolean> {
  return new Promise((resolve) => {
    const webP = new Image()
    webP.onload = webP.onerror = () => {
      resolve(webP.height === 2)
    }
    webP.src =
      'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA'
  })
}

/**
 * Get optimized image format
 */
export async function getOptimizedImageSrc(
  src: string,
  preferWebP = true
): Promise<string> {
  if (!preferWebP) return src

  const isWebPSupported = await supportsWebP()
  if (isWebPSupported) {
    const ext = src.split('.').pop()
    return src.replace(`.${ext}`, '.webp')
  }

  return src
}
