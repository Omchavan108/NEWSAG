import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useUser } from '@clerk/clerk-react';
import { SearchBar } from '../ui/SearchBar';

interface NavbarProps {
  onThemeToggle: () => void;
  isDark: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onThemeToggle, isDark }) => {
  const { isSignedIn, signOut } = useAuth();
  const { user } = useUser();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };

  return (
    <nav className="sticky top-0 z-50 glass border-b border-slate-200 dark:border-slate-800 px-4 md:px-8 py-4 transition-all duration-300">
      <div className="w-full flex items-center justify-between gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group flex-shrink-0">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/30 group-hover:scale-110 transition-transform duration-300">
            <span className="text-white font-black text-xl">NA</span>
          </div>
          <h1 className="text-xl font-medium tracking-tight hidden lg:block text-slate-700 dark:text-white">
            NewsAura
          </h1>
        </Link>

        {/* Center - Search & Nav */}
        <div className="flex-1 min-w-0 flex items-center gap-3">
          <SearchBar />

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className="px-3 py-2 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all whitespace-nowrap"
            >
              Home
            </Link>
            <Link
              to="/bookmarks"
              className="px-3 py-2 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all whitespace-nowrap"
            >
              Bookmarks
            </Link>
            <Link
              to="/read-later"
              className="px-3 py-2 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all whitespace-nowrap"
            >
              Read Later
            </Link>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(prev => !prev)}
            aria-expanded={mobileMenuOpen}
            className="md:hidden p-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
            aria-label="Toggle menu"
          >
            <svg className="w-5 h-5 text-slate-600 dark:text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <button 
            onClick={onThemeToggle}
            className="p-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all active:scale-90"
            aria-label="Toggle theme"
          >
            {isDark ? (
              <svg className="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
          
          {isSignedIn ? (
            <div className="flex items-center gap-2">
              <Link to="/profile" className="flex items-center gap-2 group p-0.5 pr-3 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all">
                <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-indigo-600">
                  <img src={user?.imageUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'user'}`} alt="User" />
                </div>
                <span className="text-xs font-black hidden sm:inline">{user?.username || 'Profile'}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="px-3 py-2 rounded-xl text-sm font-bold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all whitespace-nowrap"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link to="/login" className="px-4 py-2 rounded-xl text-sm font-bold bg-indigo-600 text-white hover:bg-indigo-700 transition-all">
              Login
            </Link>
          )}
        </div>

        {/* Mobile menu panel */}
        {typeof window !== 'undefined' && mobileMenuOpen && (
          <MobileMenuPanel setMobileMenuOpen={setMobileMenuOpen} />
        )}

      </div>
    </nav>
  );

  // Local small component to avoid cluttering main markup
  function MobileMenuPanel({ setMobileMenuOpen } : { setMobileMenuOpen: (v:boolean) => void }) {
    return (
      // This panel is controlled via CSS display and the shared state above. We keep markup here for clarity.
      <div className="md:hidden absolute top-full right-4 mt-2 w-44 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-2 z-50">
        <Link to="/" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Home</Link>
        <Link to="/bookmarks" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Bookmarks</Link>
        <Link to="/read-later" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-sm font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">Read Later</Link>
      </div>
    );
  }
};