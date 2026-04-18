import { Link } from "@tanstack/react-router";
import { GraduationCap, Github, Mail } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-border bg-card/50">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-4 lg:px-8">
        <div className="lg:col-span-2">
          <Link to="/" className="inline-flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg gradient-brand text-primary-foreground">
              <GraduationCap className="h-5 w-5" />
            </span>
            <span className="font-display text-lg font-semibold">Intelligent University Observatory</span>
          </Link>
          <p className="mt-3 max-w-md text-sm text-muted-foreground">
            An AI-powered observatory that surfaces internships, scholarships, research projects, courses
            and postdoc positions tailored to your academic journey.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-semibold">Explore</h4>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li><Link to="/opportunities" className="hover:text-foreground">All opportunities</Link></li>
            <li><Link to="/dashboard" className="hover:text-foreground">My dashboard</Link></li>
            <li><Link to="/profile" className="hover:text-foreground">My profile</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold">Account</h4>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li><Link to="/login" className="hover:text-foreground">Sign in</Link></li>
            <li><Link to="/register" className="hover:text-foreground">Create account</Link></li>
          </ul>
          <div className="mt-4 flex items-center gap-3 text-muted-foreground">
            <a href="mailto:hello@iuo.edu" aria-label="Email" className="hover:text-foreground"><Mail className="h-4 w-4" /></a>
            <a href="#" aria-label="GitHub" className="hover:text-foreground"><Github className="h-4 w-4" /></a>
          </div>
        </div>
      </div>
      <div className="border-t border-border">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 text-xs text-muted-foreground sm:px-6 lg:px-8">
          <p>© {new Date().getFullYear()} Intelligent University Observatory</p>
          <p>Built for students and researchers</p>
        </div>
      </div>
    </footer>
  );
}
