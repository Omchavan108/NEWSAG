
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth, useUser } from '@clerk/clerk-react';
import { Button } from '../components/ui/Button.tsx';
import { userService } from '../services/user.service';
import type { ProfileAnalyticsResponse } from '../services/user.service';

const StatCard: React.FC<{ label: string; value: React.ReactNode; icon?: React.ReactNode }> = ({ label, value, icon }) => {
  return (
    <div className="relative rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm dark:border-slate-700 dark:bg-slate-800">
      {icon ? <div className="absolute right-3 top-3 text-slate-300 dark:text-slate-500">{icon}</div> : null}
      <span className="block text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1 dark:text-slate-500">{label}</span>
      <div className="text-xl font-bold text-slate-900 dark:text-slate-100">{value}</div>
    </div>
  );
};

export const Profile: React.FC = () => {
  const { signOut } = useAuth();
  const { user } = useUser();
  const navigate = useNavigate();
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [analytics, setAnalytics] = useState<ProfileAnalyticsResponse | null>(null);

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };

  useEffect(() => {
    let isActive = true;
    userService
      .getProfileAnalytics()
      .then((res) => {
        if (!isActive) return;
        setAnalytics(res);
      })
      .catch(() => {
        if (!isActive) return;
        setAnalytics(null);
      })
      .finally(() => {
        if (!isActive) return;
        setIsLoadingStats(false);
      });

    return () => {
      isActive = false;
    };
  }, []);

  const userData = {
    name: user?.fullName || user?.firstName || user?.username || "User",
    handle: `@${user?.username || 'user'}`,
    email: user?.primaryEmailAddress?.emailAddress || '',
    bio: "News enthusiast using NewsAura to stay informed.",
    avatar: user?.imageUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'user'}`,
  };

  const placeholder = <span className="inline-block h-6 w-12 rounded bg-slate-200 dark:bg-slate-700 animate-pulse" />;
  const valueOr = (value: React.ReactNode) => (isLoadingStats ? placeholder : value);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="rounded-[2.5rem] bg-white border border-slate-200 shadow-lg px-8 py-10 md:px-12 md:py-12 dark:bg-slate-800 dark:border-slate-700">
          <div className="flex flex-col md:flex-row items-start gap-8">
            <div className="w-28 h-28 md:w-32 md:h-32 rounded-[1.75rem] overflow-hidden border border-slate-100 shadow-sm flex-shrink-0 dark:border-slate-700">
              <img src={userData.avatar} alt={userData.name} className="w-full h-full object-cover" />
            </div>
            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">{userData.name}</h2>
                  <p className="text-indigo-600 font-semibold dark:text-indigo-400">{userData.handle}</p>
                  <p className="text-sm text-slate-400 mt-1 dark:text-slate-500">{userData.email}</p>
                  <p className="text-slate-500 mt-4 max-w-xl dark:text-slate-400">{userData.bio}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Edit Profile</Button>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 rounded-xl text-sm font-bold text-red-600 hover:bg-red-50 border border-red-200 transition-all dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/20"
                  >
                    Logout
                  </button>
                </div>
              </div>

              <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                  label="Articles Read"
                  value={valueOr(analytics?.tier1.articles_read ?? '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M4 5a2 2 0 012-2h8a2 2 0 012 2v16l-6-3-6 3V5z" /></svg>}
                />
                <StatCard
                  label="Bookmarks"
                  value={valueOr(analytics?.tier1.bookmarks ?? '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>}
                />
                <StatCard
                  label="Read Later"
                  value={valueOr(analytics?.tier1.read_later ?? '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                />
                <StatCard
                  label="Total Saved"
                  value={valueOr(analytics?.tier1.total_saved ?? '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h16v4H4zM4 10h16v10H4z" /></svg>}
                />
              </div>

              <div className="mt-4 grid grid-cols-2 lg:grid-cols-3 gap-4">
                <StatCard
                  label="Top Category"
                  value={valueOr(analytics?.tier2.top_category ?? '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M4 6h16v12H4z" /></svg>}
                />
                <StatCard
                  label="Engagement"
                  value={valueOr(<span className="text-sm font-bold">{analytics?.tier3.engagement_label ?? '—'}</span>)}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M3 12h3v8H3zM9 8h3v12H9zM15 4h3v16h-3z" /></svg>}
                />
                <StatCard
                  label="Last Active"
                  value={valueOr(analytics?.tier1.last_active_at ? new Date(analytics.tier1.last_active_at).toLocaleDateString() : '—')}
                  icon={<svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v2H5a2 2 0 00-2 2v2h18V6a2 2 0 00-2-2h-2V2h-2v2H9V2H7zm14 8H3v10a2 2 0 002 2h14a2 2 0 002-2V10z" /></svg>}
                />
              </div>

              {!isLoadingStats && analytics?.tier2.weekly_activity?.length ? (
                <div className="mt-6">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3 dark:text-slate-500">Weekly Activity</h3>
                  <div className="flex flex-wrap gap-2">
                    {analytics.tier2.weekly_activity.map((item) => (
                      <div key={item.day} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-200">
                        {item.day} <span className="ml-1 text-slate-400 dark:text-slate-400">{item.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};