'use client'

import { useState } from 'react'
import { Menu, X, Home } from 'lucide-react'
import Button from '@/components/ui/Button'

/**
 * App header with hockey branding and navigation
 */
export function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="header-gradient border-b border-hockey-blue-dark sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🏒</div>
            <div className="text-white">
              <h1 className="text-lg font-bold">Hockey Coach AI</h1>
              <p className="text-xs text-hockey-ice opacity-90 hidden sm:block">
                Your intelligent coaching assistant
              </p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <a 
              href="/" 
              className="text-white hover:text-hockey-ice transition-colors duration-200 flex items-center space-x-2"
            >
              <Home size={18} />
              <span>Chat</span>
            </a>
            {/* TODO: Add more navigation links */}
            {/* <a href="/plans" className="text-white hover:text-hockey-ice transition-colors">Practice Plans</a> */}
            {/* <a href="/development" className="text-white hover:text-hockey-ice transition-colors">Player Development</a> */}
            {/* <a href="/library" className="text-white hover:text-hockey-ice transition-colors">Knowledge Library</a> */}
          </nav>

          {/* Desktop Action Buttons */}
          <div className="hidden md:flex items-center space-x-3">
            {/* TODO: Add authentication buttons when auth is implemented */}
            {/* <Button variant="ghost" className="text-white border-white hover:bg-white hover:text-hockey-blue">
              Sign In
            </Button>
            <Button variant="secondary">
              Get Started
            </Button> */}
            <div className="text-xs text-hockey-ice opacity-75">
              v0.1.0 Beta
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-white hover:text-hockey-ice transition-colors p-2"
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-hockey-blue-light">
            <nav className="flex flex-col space-y-3">
              <a 
                href="/" 
                className="text-white hover:text-hockey-ice transition-colors flex items-center space-x-2 py-2"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Home size={18} />
                <span>Chat Assistant</span>
              </a>
              {/* TODO: Add more mobile navigation links */}
              <div className="pt-3 border-t border-hockey-blue-light">
                <div className="text-xs text-hockey-ice opacity-75">
                  Hockey Coach AI v0.1.0 Beta
                </div>
                {/* TODO: Add mobile auth buttons when auth is implemented */}
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
