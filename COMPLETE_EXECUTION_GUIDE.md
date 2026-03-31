# 🛡️ Guardia Lingua - Final Production Guide

Your platform is now **100% Production-Ready** and supports a **Serverless AI mode** to bypass Google Cloud billing.

## 🚀 Quick Start (No Backend Required)
If you don't have a Google Cloud billing account, you can run the app entirely in the browser:
1. **Deploy to Vercel**: (Already done!)
2. **Add Env Vars in Vercel**:
   - `VITE_SUPABASE_URL`: `https://nnoddmdwwladxasorzkh.supabase.co`
   - `VITE_SUPABASE_ANON_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. **Open the App**: Go to **Settings (Gear icon)** -> Paste your **Gemini API Key** -> Turn **OFF** "Managed AI".
4. **Chat!**: The AI will now work directly from your browser.

## ☁️ Cloud Deployment (Optional)
If you decide to enable billing later, use the included script:
```zsh
chmod +x deploy_backend.sh
./deploy_backend.sh
```

## 💻 Local Development (Ollama)
If you want to run the full platform locally on your Mac:
1. **Pull the Model**:
   ```zsh
   ollama pull aiasistentworld/GLM-4.5-Air-LLM
   ```
2. **Start the Platform**:
   ```zsh
   ./RUN_LOCAL_MACOS.sh
   ```
3. **Customize AI**: Edit `backend/.env` and change `OLLAMA_MODEL` to your preferred model.

## ✅ Completed Features
- **Real Google Social Login** (via Supabase)
- **BYOK (Bring Your Own Key)** support
- **Serverless AI Mode** (Direct Browser-to-Gemini)
- **Local Ollama Support** (Optimized for GLM-4.5)
- **Auto-Database Migrations**
- **Zero Lint Errors**

---
*Created with ❤️ by Antigravity*

