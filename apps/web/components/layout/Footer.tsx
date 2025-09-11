'use client'

/**
 * App footer with links and attribution
 */
export function Footer() {
  return (
    <footer className="bg-neutral-100 border-t border-neutral-200 py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          {/* Brand and Description */}
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start space-x-2 mb-2">
              <span className="text-lg">🏒</span>
              <span className="font-semibold text-neutral-900">Hockey Coach AI</span>
            </div>
            <p className="text-sm text-neutral-600">
              Intelligent coaching assistant powered by AI
            </p>
          </div>

          {/* Links */}
          <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
            {/* TODO: Add proper links when pages are available */}
            <a 
              href="#" 
              className="text-sm text-neutral-600 hover:text-hockey-blue transition-colors"
            >
              About
            </a>
            <a 
              href="#" 
              className="text-sm text-neutral-600 hover:text-hockey-blue transition-colors"
            >
              Help
            </a>
            <a 
              href="#" 
              className="text-sm text-neutral-600 hover:text-hockey-blue transition-colors"
            >
              Privacy
            </a>
          </div>

          {/* Version and Status */}
          <div className="text-center md:text-right">
            <div className="text-xs text-neutral-500">
              Version 0.1.0 Beta
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              Built for hockey coaches with ❤️
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-6 pt-4 border-t border-neutral-200 text-center">
          <p className="text-xs text-neutral-500">
            © 2025 Hockey Coach AI. All rights reserved.
            {/* TODO: Add proper legal information */}
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
