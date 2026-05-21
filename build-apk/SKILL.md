---
name: build-apk
description: >
  Build Mnemos Android debug APK. Full flow: vite build → cap sync → gradle assembleDebug.
  Output: android/app/build/outputs/apk/debug/app-debug.apk.
  Trigger: "打包APK", "build apk", "打包安卓", "build android",
  "出APK", "生成apk", "打包發布版", "build release".
  Any request to produce an .apk file from the Mnemos project.
---

# Build APK

Package the Mnemos Capacitor/React Android app into a debug APK.

## Execution

```bash
~/Scripts/build-mnemos-apk
```

The script handles working directory, all 3 build steps, and verification.

## Workflow

```
npm run build  →  dist/
npx cap sync android  →  android/app/src/main/assets/
./gradlew assembleDebug  →  app-debug.apk
```

## Preflight (must verify before running)

1. Working directory is `~/Projects/Mnemos/` — script auto-cds but if you're running individual commands, check `pwd`
2. `vite.config.js` does NOT have `vite-plugin-singlefile` (removed 2026-05-03, breaks production build)
3. `package.json` has correct `"version": "1.0.0"`

## Post-build

APK at: `android/app/build/outputs/apk/debug/app-debug.apk`
