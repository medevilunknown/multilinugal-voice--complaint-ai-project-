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
  const [modelName, setModelName] = useState("gemini-1.5-flash");
  const { user, signOut } = useAuth();

  // Load preferences from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem("custom_gemini_key") || "";
    const savedManaged = localStorage.getItem("is_managed_ai") !== "false";
    const savedModel = localStorage.getItem("custom_gemini_model") || "gemini-1.5-flash";
    setApiKey(savedKey);
    setUseManaged(savedManaged);
    setModelName(savedModel);
  }, []);

  const handleSave = () => {
    const trimmedKey = apiKey.trim();
    localStorage.setItem("custom_gemini_key", trimmedKey);
    localStorage.setItem("is_managed_ai", String(useManaged));
    localStorage.setItem("custom_gemini_model", modelName);
    setApiKey(trimmedKey);
    toast.success("AI Settings updated successfully!");
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
             Bring your own Gemini API key for uncapped usage. 
             <span className="block mt-2 font-bold text-accent">🚀 Works without a backend if you provide your own key!</span>
          </DialogDescription>
        </DialogHeader>


        <div className="grid gap-6 py-4">
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

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-semibold">Model Version</Label>
                  {modelName === "custom" && (
                    <span className="text-[10px] text-accent font-bold animate-pulse">CUSTOM MODE</span>
                  )}
                </div>
                <select 
                  value={modelName.startsWith("gemini-") || modelName === "custom" ? (["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-3-flash"].includes(modelName) ? modelName : "custom") : "custom"}
                  onChange={(e) => setModelName(e.target.value === "custom" ? "" : e.target.value)}
                  className="w-full h-10 px-3 py-2 text-sm bg-background border border-input rounded-md ring-offset-background outline-none"
                >
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash (Stable)</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash (Next Gen)</option>
                  <option value="gemini-2.5-flash">Gemini 2.5 Flash (Placeholder)</option>
                  <option value="gemini-3-flash">Gemini 3 Flash (Placeholder)</option>
                  <option value="custom">-- Use Custom Model Name --</option>
                </select>
                
                {(modelName === "" || !["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-3-flash"].includes(modelName)) && (
                  <Input
                    placeholder="Enter custom model name (e.g. gemini-3-pro)"
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    className="mt-2 font-mono text-xs"
                  />
                )}
              </div>
            </div>
          )}

          <div className="border-t pt-4">
            <div className="flex flex-col gap-2">
              <Button onClick={handleSave} className="w-full">
                Save Preferences
              </Button>
            </div>
          </div>

        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SettingsModal;

