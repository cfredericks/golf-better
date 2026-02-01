import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-green-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <span className="text-white text-xl font-bold">Golf Better</span>
              </Link>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
                <Link
                  to="/"
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium ${
                    isActive('/') && !isActive('/leagues')
                      ? 'text-white border-b-2 border-white'
                      : 'text-green-100 hover:text-white'
                  }`}
                >
                  Tournaments
                </Link>
                <Link
                  to="/leagues"
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium ${
                    isActive('/leagues')
                      ? 'text-white border-b-2 border-white'
                      : 'text-green-100 hover:text-white'
                  }`}
                >
                  Leagues
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {user && (
                <>
                  <span className="text-green-100 text-sm hidden sm:block">
                    {user.name}
                  </span>
                  {user.photoUrl && (
                    <img
                      src={user.photoUrl}
                      alt={user.name}
                      className="h-8 w-8 rounded-full"
                    />
                  )}
                  <button
                    onClick={logout}
                    className="text-green-100 hover:text-white text-sm font-medium"
                  >
                    Sign out
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
        {/* Mobile menu */}
        <div className="sm:hidden border-t border-green-600">
          <div className="px-2 py-2 space-x-2 flex">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/') && !isActive('/leagues')
                  ? 'bg-green-800 text-white'
                  : 'text-green-100 hover:bg-green-600'
              }`}
            >
              Tournaments
            </Link>
            <Link
              to="/leagues"
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                isActive('/leagues')
                  ? 'bg-green-800 text-white'
                  : 'text-green-100 hover:bg-green-600'
              }`}
            >
              Leagues
            </Link>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
