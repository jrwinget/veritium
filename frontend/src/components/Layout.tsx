import { Outlet, Link, useLocation } from 'react-router-dom'
import { BeakerIcon } from '@heroicons/react/24/outline'

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow" role="navigation" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link
                to="/"
                className="flex items-center space-x-2 text-xl font-bold text-primary-600 hover:text-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 rounded-md px-2 py-1"
                aria-label="Veritium home"
              >
                <BeakerIcon className="h-8 w-8" aria-hidden="true" />
                <span>Veritium</span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${location.pathname === '/'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  } focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2`}
                aria-current={location.pathname === '/' ? 'page' : undefined}
              >
                Home
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8" role="main">
        <Outlet />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12" role="contentinfo">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            <p>
              Veritium - Scientific Article Verification System
            </p>
            <p className="mt-2">
              <strong>Disclaimer:</strong> This tool provides automated analysis for research purposes only.
              Always consult original sources and domain experts for critical decisions.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}