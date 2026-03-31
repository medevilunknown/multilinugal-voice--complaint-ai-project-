import { Link, useLocation } from "react-router-dom";
import { Menu, X, User } from "lucide-react";
import { LANGUAGES, useLanguage } from "@/contexts/LanguageContext";
import { useState } from "react";
import BrandLogo from "@/components/BrandLogo";
import SettingsModal from "@/components/SettingsModal";
import { Button } from "@/components/ui/button";

export default function Navbar() {
  const { t, language, setLanguage } = useLanguage();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [languageOpen, setLanguageOpen] = useState(false);
  const isAdminRoute = location.pathname.startsWith("/admin");
  const isAdminLoginPage = location.pathname === "/admin";
  const showLanguageRow = !isAdminRoute;

  const links = isAdminRoute
    ? [
        { to: "/admin/dashboard", label: "Dashboard" },
        { to: "/admin/profile", label: t("profile") },
      ]
    : [
        { to: "/complaint", label: t("fileComplaint") },
        { to: "/track", label: t("trackComplaint") },
      ];

  const visibleLinks = isAdminLoginPage ? [] : links;

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="gov-gradient text-primary-foreground shadow-lg">
      {/* Main nav */}
      <div className="max-w-[1400px] mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <BrandLogo sizeClassName="w-10 h-10" className="shadow-sm" />
          <div>
            <div className="font-bold text-lg leading-tight tracking-tight">{t("cyberGuard")}</div>
            <div className="text-[10px] text-primary-foreground/60 leading-tight">{t("tagline")}</div>
          </div>
        </Link>

        {/* Desktop links + settings + languages */}
        <div className="hidden md:flex items-center gap-2 min-w-0">
          {visibleLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150
                ${isActive(link.to)
                  ? "bg-accent text-accent-foreground"
                  : "text-primary-foreground/80 hover:text-primary-foreground hover:bg-primary-foreground/10"
                }`}
            >
              {link.label}
            </Link>
          ))}

          <div className="flex items-center gap-1 ml-1 pl-2 border-l border-primary-foreground/15">
            <SettingsModal />
            
            {showLanguageRow && (
              <div className="relative">
                <button
                  onClick={() => setLanguageOpen((prev) => !prev)}
                  className="px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-150 text-primary-foreground/80 hover:text-primary-foreground hover:bg-primary-foreground/10"
                >
                  {t("language")}: {language.nativeName}
                </button>
                {languageOpen && (
                  <div className="absolute right-0 mt-2 w-52 max-h-56 overflow-y-auto rounded-md border border-primary-foreground/20 bg-primary shadow-xl z-50">
                    {LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang);
                          setLanguageOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 text-sm transition-all
                          ${language.code === lang.code
                            ? "bg-accent text-accent-foreground"
                            : "text-primary-foreground/80 hover:text-primary-foreground hover:bg-primary-foreground/10"
                          }`}
                      >
                        {lang.nativeName}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          <Button variant="outline" size="sm" className="ml-2 bg-transparent border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/10 hidden lg:flex items-center gap-2">
            <User className="h-4 w-4" />
            Sign In
          </Button>
        </div>

        {/* Mobile toggle */}
        <div className="flex items-center gap-2 md:hidden">
           <SettingsModal />
           <button
            className="p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-primary-foreground/10 px-4 py-3 space-y-1">
          {visibleLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              onClick={() => setMobileOpen(false)}
              className={`block px-3 py-2 rounded-md text-sm font-medium transition-all
                ${isActive(link.to)
                  ? "bg-accent text-accent-foreground"
                  : "text-primary-foreground/80 hover:bg-primary-foreground/10"
                }`}
            >
              {link.label}
            </Link>
          ))}
          {showLanguageRow && (
            <div className="pt-2 border-t border-primary-foreground/10 mt-2">
              <p className="text-xs text-primary-foreground/70 mb-2">
                {t("language")}: {language.nativeName}
              </p>
              <div className="max-h-44 overflow-y-auto space-y-1 pr-1">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang);
                      setMobileOpen(false);
                    }}
                    className={`w-full text-left px-2.5 py-1.5 rounded text-xs font-medium
                      ${language.code === lang.code
                        ? "bg-accent text-accent-foreground"
                        : "text-primary-foreground/80 hover:bg-primary-foreground/10"
                      }`}
                  >
                    {lang.nativeName}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
