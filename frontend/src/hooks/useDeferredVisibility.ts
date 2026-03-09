import { useCallback, useEffect, useState } from 'react'

interface UseDeferredVisibilityOptions {
  rootMargin?: string
}

export function useDeferredVisibility<T extends HTMLElement>({
  rootMargin = '160px 0px',
}: UseDeferredVisibilityOptions = {}) {
  const [targetNode, setTargetNode] = useState<T | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const targetRef = useCallback((node: T | null) => {
    setTargetNode(node)
  }, [])

  useEffect(() => {
    if (isVisible) return

    if (!targetNode) return

    if (typeof IntersectionObserver === 'undefined') {
      setIsVisible(true)
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { rootMargin },
    )

    observer.observe(targetNode)
    return () => observer.disconnect()
  }, [isVisible, rootMargin, targetNode])

  return {
    isVisible,
    targetRef,
  }
}
