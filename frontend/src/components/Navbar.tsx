import { Link, useLocation, useNavigate, useRouter } from "@tanstack/react-router";
import { Bell, Menu, X, GraduationCap, LogOut, User as UserIcon, LayoutDashboard } from "lucide-react";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { fetchUnreadCount } from "@/lib/services";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const PUBLIC_LINKS = [
  { to: "/", label: "Home" },
  { to: "/opportunities", label: "Opportunities" },
];

const PROTECTED_LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/profile", label: "Profile" },
];

export function Navbar() {
  const { token, user, logout } = useAuthStore();
  const router = useRouter();
  const navigate = useNavigate();
  const location = useLocation();
  const [unread, setUnread] = useState(0);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!token) {
      setUnread(0);
      return;
    }
    let active = true;
    const load = async () => {
      try {
        const c = await fetchUnreadCount();
        if (active) setUnread(c);
      } catch {
        /* silent */
      }
    };
    load();
    const id = setInterval(load, 60_000);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [token]);

  const links = token ? [...PUBLIC_LINKS, ...PROTECTED_LINKS] : PUBLIC_LINKS;

  const handleLogout = () => {
    logout();
    router.invalidate();
    navigate({ to: "/" });
  };

  const initials = user?.name
    ? user.name
        .split(/\s+/)
        .map((s) => s[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "U";

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 group" aria-label="Intelligent University Observatory home">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg gradient-brand text-primary-foreground shadow-elegant">
            <GraduationCap className="h-5 w-5" />
          </span>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold leading-tight">Intelligent</p>
            <p className="-mt-0.5 text-xs leading-tight text-muted-foreground">University Observatory</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary">
          {links.map((l) => {
            const active =
              l.to === "/" ? location.pathname === "/" : location.pathname.startsWith(l.to);
            return (
              <Link
                key={l.to}
                to={l.to}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm font-medium transition",
                  active
                    ? "bg-secondary text-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/60",
                )}
              >
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          {token ? (
            <>
              <Link
                to="/dashboard"
                aria-label={`Notifications${unread ? `, ${unread} unread` : ""}`}
                className="relative inline-flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary/60"
              >
                <Bell className="h-5 w-5" />
                {unread > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-semibold text-destructive-foreground">
                    {unread > 9 ? "9+" : unread}
                  </span>
                )}
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    aria-label="Account menu"
                    className="flex h-9 w-9 items-center justify-center rounded-full gradient-brand text-sm font-semibold text-primary-foreground shadow-card"
                  >
                    {initials}
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">{user?.name}</span>
                      <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate({ to: "/dashboard" })}>
                    <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate({ to: "/profile" })}>
                    <UserIcon className="mr-2 h-4 w-4" /> Profile
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                    <LogOut className="mr-2 h-4 w-4" /> Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          ) : (
            <div className="hidden items-center gap-2 sm:flex">
              <Button variant="ghost" asChild size="sm">
                <Link to="/login">Sign in</Link>
              </Button>
              <Button asChild size="sm" className="gradient-brand text-primary-foreground hover:opacity-95">
                <Link to="/register">Get started</Link>
              </Button>
            </div>
          )}

          <button
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary/60"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-background">
          <nav className="flex flex-col gap-1 p-3" aria-label="Mobile">
            {links.map((l) => {
              const active =
                l.to === "/" ? location.pathname === "/" : location.pathname.startsWith(l.to);
              return (
                <Link
                  key={l.to}
                  to={l.to}
                  className={cn(
                    "rounded-md px-3 py-2 text-sm font-medium",
                    active ? "bg-secondary" : "text-muted-foreground hover:bg-secondary/60",
                  )}
                >
                  {l.label}
                </Link>
              );
            })}
            {!token && (
              <div className="mt-2 grid grid-cols-2 gap-2">
                <Button variant="outline" asChild size="sm">
                  <Link to="/login">Sign in</Link>
                </Button>
                <Button asChild size="sm" className="gradient-brand text-primary-foreground">
                  <Link to="/register">Register</Link>
                </Button>
              </div>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
