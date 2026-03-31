import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "https://nnoddmdwwladxasorzkh.supabase.co";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ub2RkbWR3d2xhZHhhc29yemtoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0NjY1MzksImV4cCI6MjA5MDA0MjUzOX0.2vQzZQdaoMchZeE7KhYMaU9wZG-VWJbSIyASXNq9-Rg";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
