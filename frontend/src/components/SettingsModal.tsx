import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Settings, Key, User, Shield } from "lucide-react";
import { toast } from "sonner";

import { supabase } from "@/lib/supabase";
import { useAuth } from "@/contexts/AuthContext";

export const SettingsModal = () => {
  const [apiKey, setApiKey] = useState("");
  const [useManaged, setUseManaged] = useState(true);
  const { user, signOut } = useAuth();

  // Load preferences from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem("custom_gemini_key") || "";
    const savedManaged = localStorage.getItem("is_managed_ai") !== "false";
    setApiKey(savedKey);
    setUseManaged(savedManaged);
  }, []);

  const handleSave = () => {
    localStorage.setItem("custom_gemini_key", apiKey);
    localStorage.setItem("is_managed_ai", String(useManaged));
    toast.success("AI Settings updated successfully!");
  };

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin
      }
    });
    if (error) {
      toast.error("Auth failed: " + error.message);
    }
  };

  const handleLogout = async () => {
    await signOut();
    localStorage.removeItem("userEmail");
    toast.info("Logged out");
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="text-primary-foreground hover:bg-primary/80 transition-all">
          <Settings className="h-5 w-5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] bg-white rounded-xl shadow-2xl border-primary/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            AI Preferences
          </DialogTitle>
          <DialogDescription>
            Personalize your AI experience. Bring your own Gemini API key for uncapped usage.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-6 py-6">
          {user && (
            <div className="flex items-center justify-between p-3 bg-secondary/10 rounded-lg border border-secondary/20 border-dashed">
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-secondary-foreground" />
                <span className="text-sm font-medium">{user.email}</span>
              </div>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="h-7 text-[10px]">
                Sign Out
              </Button>
            </div>
          )}

          <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg border border-primary/10">
            <div className="space-y-0.5">
              <Label className="text-base font-semibold">Managed AI (Default)</Label>
              <p className="text-sm text-muted-foreground">
                Use our enterprise Gemini credits
              </p>
            </div>
            <Switch
              checked={useManaged}
              onCheckedChange={setUseManaged}
            />
          </div>

          {!useManaged && (
            <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
              <div className="space-y-2">
                <Label htmlFor="apiKey" className="flex items-center gap-2">
                  <Key className="h-4 w-4 text-primary" />
                   Personal Gemini Key
                </Label>
                <Input
                  id="apiKey"
                  type="password"
                  placeholder="Paste your API key here..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="font-mono text-sm"
                />
              </div>
            </div>
          )}

          <div className="border-t pt-4">
            <div className="flex flex-col gap-2">
              <Button onClick={handleSave} className="w-full">
                Save Preferences
              </Button>
              {!user && (
                <Button variant="outline" onClick={handleLogin} className="w-full flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Sign in with Google
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SettingsModal;
