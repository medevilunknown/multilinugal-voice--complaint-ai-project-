import { useLanguage } from "@/contexts/LanguageContext";
import { Link } from "react-router-dom";
import { FileText, Search, Mic, Phone, AlertTriangle, Users, Globe } from "lucide-react";
import MicButton from "@/components/MicButton";
import { useSpeechToText, useTextToSpeech } from "@/hooks/useSpeech";
import { useEffect, useRef, useState } from "react";
import BrandLogo from "@/components/BrandLogo";

export default function HomePage() {
  const { t, isLanguageSelected, language } = useLanguage();
  const { isListening, transcript, startListening, stopListening } = useSpeechToText();
  const { speak } = useTextToSpeech();
  const greetedRef = useRef(false);
  const [showTranscript, setShowTranscript] = useState(false);

  // Greet user when language is selected
  useEffect(() => {
    if (isLanguageSelected && !greetedRef.current) {
      greetedRef.current = true;
      setTimeout(() => speak(t("greeting")), 500);
    }
  }, [isLanguageSelected, speak, t]);

  const toggleMic = () => {
    if (isListening) {
      stopListening();
      setShowTranscript(true);
    } else {
      startListening();
      setShowTranscript(false);
    }
  };

  const stats = [
    { icon: FileText, value: "2.5L+", label: "Complaints Filed" },
    { icon: Users, value: "1.8L+", label: "Cases Resolved" },
    { icon: Globe, value: "23", label: "Languages Supported" },
    { icon: Phone, value: "1930", label: "Helpline Number" },
  ];

  return (
    <div className="min-h-[calc(100vh-120px)]">
      {/* Hero Section */}
      <section className="gov-gradient text-primary-foreground py-16 md:py-24 relative overflow-hidden">
        {/* Subtle pattern overlay */}
        <div className="absolute inset-0 opacity-5" style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)",
          backgroundSize: "32px 32px",
        }} />

        <div className="max-w-[1400px] mx-auto px-4 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <div className="flex justify-center mb-6 animate-reveal-up">
              <BrandLogo sizeClassName="w-24 h-24 md:w-28 md:h-28" className="shadow-xl" />
            </div>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary-foreground/20 bg-primary-foreground/5 mb-6 animate-reveal-up">
              <AlertTriangle className="w-4 h-4 text-accent" />
              <span className="text-sm text-primary-foreground/80">{t("helpline")}</span>
            </div>

            <h1 className="text-3xl md:text-5xl font-bold leading-[1.1] tracking-tight mb-4 text-balance animate-reveal-up" style={{ animationDelay: "80ms" }}>
              {t("cyberGuard")}
            </h1>
            <p className="text-lg md:text-xl text-primary-foreground/70 mb-8 text-pretty animate-reveal-up" style={{ animationDelay: "160ms" }}>
              {t("tagline")} — {t("govIndia")}
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-reveal-up" style={{ animationDelay: "240ms" }}>
              <Link
                to="/complaint"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg bg-accent text-accent-foreground font-semibold text-base shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
              >
                <FileText className="w-5 h-5" />
                {t("fileComplaint")}
              </Link>
              <Link
                to="/track"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-lg bg-primary-foreground/10 text-primary-foreground font-semibold text-base border border-primary-foreground/20 hover:bg-primary-foreground/15 transition-all duration-200 active:scale-[0.98]"
              >
                <Search className="w-5 h-5" />
                {t("trackComplaint")}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="bg-card border-b border-border shadow-sm">
        <div className="max-w-[1400px] mx-auto px-4 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <div key={stat.label} className="text-center animate-reveal-up" style={{ animationDelay: `${i * 100}ms` }}>
              <stat.icon className="w-8 h-8 mx-auto mb-2 text-accent" />
              <div className="text-2xl font-bold text-foreground tabular-nums">{stat.value}</div>
              <div className="text-sm text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-[1400px] mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center mb-12 text-balance">How CyberGuard AI Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: "01", title: "Select Language", desc: "Choose from 22 official Indian languages. The AI will converse in your preferred language.", icon: Globe },
            { step: "02", title: "Describe the Incident", desc: "Speak or type your complaint. Our AI assistant guides you through every step.", icon: Mic },
            { step: "03", title: "Track & Resolve", desc: "Get a ticket ID. Track your complaint status in real-time in your language.", icon: Search },
          ].map((item, i) => (
            <div
              key={item.step}
              className="bg-card rounded-xl p-8 shadow-sm border border-border hover:shadow-md transition-shadow duration-300 animate-reveal-up"
              style={{ animationDelay: `${i * 120}ms` }}
            >
              <div className="text-xs font-bold text-accent mb-3 tracking-wider">STEP {item.step}</div>
              <item.icon className="w-10 h-10 text-primary mb-4" />
              <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
              <p className="text-sm text-muted-foreground text-pretty">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Voice Transcript Overlay */}
      {showTranscript && transcript && (
        <div className="fixed bottom-28 right-8 max-w-sm bg-card rounded-xl shadow-2xl border border-border p-4 z-50 animate-reveal-up">
          <p className="text-sm text-muted-foreground mb-1">{t("speakNow")}</p>
          <p className="text-foreground font-medium">{transcript}</p>
          <button
            onClick={() => setShowTranscript(false)}
            className="text-xs text-accent mt-2 hover:underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Floating Mic Button */}
      <div className="fixed bottom-8 right-8 z-50">
        <MicButton isListening={isListening} onToggle={toggleMic} size="lg" />
        {isListening && (
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap text-xs bg-foreground text-background px-3 py-1 rounded-full">
            {t("listening")}
          </div>
        )}
      </div>
    </div>
  );
}
