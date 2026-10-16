# Mahim AI চালু করুন — GitHub + Firebase + Render

এই project GitHub-এ code রাখা, Firebase-এ sign-in/chat data রাখা এবং Render-এ app/API চালানোর জন্য সাজানো। ZIP-এ কোনো Firebase Admin private key, provider API key বা password নেই। User-supplied ad code আছে; publisher account ও domain approval যাচাই করা হয়নি। Firebase/provider credentials নিজ account-এ যোগ করবেন।

## ১. ZIP খুলে GitHub repository তৈরি

1. `Mahim-AI-GitHub-Firebase-Render.zip` extract করুন. `mahim-ai` folder-এ project files থাকবে।
2. GitHub-এ নতুন repository খুলুন। Setup শেষ না হওয়া পর্যন্ত **Private** রাখাই নিরাপদ।
3. `mahim-ai` folder-এর **ভেতরের file-গুলো** repository root-এ রাখুন; outer folder-কে repository-র মধ্যে আরেক স্তর হিসেবে রাখবেন না। GitHub Desktop, Git command line অথবা GitHub web upload ব্যবহার করতে পারেন।
4. চাইলে terminal থেকে (URL/USERNAME নিজের repository দিয়ে বদলে):

```bash
cd path/to/mahim-ai
git init
git branch -M main
git add .
git commit -m "Initial Mahim AI workspace"
git remote add origin https://github.com/USERNAME/mahim-ai.git
git push -u origin main
```

`firebase-config.js`-এ আপনার দেওয়া Firebase Web App config বসানো আছে; project-এর সঙ্গে মেলে কি না যাচাই করুন। অন্য project হলে সেটি বদলে push করুন। Provider key, password, `.env`, Firebase Admin service-account JSON বা private key GitHub-এ দেবেন না। Firebase Web App config client-side config—এটি Admin credential নয়—তবু Firebase Auth/Firestore rules ঠিকমতো configure করতে হবে।

## ২. Firebase Auth ও Firestore

1. Firebase Console-এ আপনার project `mahim-ai-99f4e` এবং Web App আছে কি না যাচাই করুন। **Project settings → Your apps** থেকে `apiKey`, `authDomain`, `projectId`, `appId` নিয়ে `firebase-config.js`-এর values-এর সঙ্গে মিলিয়ে নিন; অন্য project হলে বদলে commit/push করুন।
2. **Authentication → Sign-in method**-এ Google এবং Email/Password enable করুন। Password reset-ও Firebase Auth দিয়ে চলে।
3. **Firestore Database** তৈরি করুন। Local terminal-এ Firebase CLI না থাকলে `npm install -g firebase-tools` চালান। তারপর:

```bash
firebase login
firebase use --add
firebase deploy --only firestore:rules
```

Deploy-এর আগে Firebase CLI যেন সঠিক project বেছে নিয়েছে, নিশ্চিত করুন। `firestore.rules` প্রত্যেক signed-in user-কে কেবল তার নিজের `users/{uid}/chats` ও usage path-এ access দেয়। Rules publish না হলে chat cloud sync বা counter fail করবে; তখন app browser-local fallback দেখাবে।

## ৩. Render-এ deploy

1. Render-এ GitHub account connect করুন। **New → Blueprint** বেছে এই repository select করুন। Render `render.yaml` থেকে Python web service বানাবে; `server.py` `/api/health`, `/api/chat` ও `/api/image` serve করে।
2. Render Blueprint environment setup-এ `FIREBASE_WEB_API_KEY`-এর value হিসেবে Firebase Web App-এর `apiKey` দিন। এটি Web API key—কোনো Admin private key নয়। `REQUIRE_AUTH=true` রাখুন।
3. Deploy শেষ হলে Render-এর `https://....onrender.com` URL নিন। Firebase Console → Authentication → Settings → **Authorized domains**-এ ওই hostname যোগ করুন। তারপর sign-in পরীক্ষা করুন।
4. GitHub-এ code push করলে `render.yaml`-এর auto-deploy নতুন build চালাতে পারে। Build/health failure হলে Render-এর deploy log দেখুন; app URL-এ `/api/health` খুলে status পরীক্ষা করুন।

## ৪. AI provider key

App-এ সাইন ইন করে **Profile → API keys**-এ নিজের provider, supported model ID এবং API key দিন। Key বর্তমান tab-এর memory-তে থাকে; browser storage/GitHub-এ লেখা হয় না। Chat/image request Render backend দিয়ে provider-এ যায়।

- Chat adapter: OpenAI, Gemini, Anthropic, OpenRouter, Groq, Together AI.
- Image adapter: বর্তমানে OpenAI-only.
- প্রতিটি provider-এর key/model আলাদা; “যেকোনো API key” universal নয়। Provider usage/quota অনুযায়ী charge হতে পারে—Render/Firebase free tier AI usage-কে free করে না।
- Config-এ `measurementId` আছে, তবে `getAnalytics()` চালু করিনি। Analytics ব্যবহার করলে আগে privacy notice/consent ঠিক করুন।

## ৫. Publisher ads ও বাকি feature

আপনার দেওয়া Native Banner, 300×250 Banner, Social Bar, Popunder ও Smartlink code app-এ যুক্ত আছে। Social Bar/Popunder site-wide, তাই এগুলো break-এর বাইরেও দেখাতে/trigger করতে পারে; দুইটি banner ১০০টি successful chat-এর পর ৩০-second break-এ load হয়; Smartlink ওই break-এর user-click link। Publisher dashboard-এ tag source, domain approval ও tracking/consent requirements যাচাই করুন; ad fill/revenue independently test করা হয়নি। Consent gate এই starter-এ নেই—publisher policy ও applicable privacy law অনুযায়ী live traffic-এর আগে consent ব্যবস্থা করুন। ৩০-second UI lock server-side abuse protection নয়। Video generation, live TV/streams, live web search এবং arbitrary external actions আলাদা service/API integration ছাড়া চালু নয়।

## ৬. Launch-এর আগে test checklist

- Google sign-in, email/password ও password reset—শুধু আপনার নিজের authorized Render domain-এ পরীক্ষা করুন।
- দুইটি test account ব্যবহার করে নিশ্চিত করুন যে একজন অন্যজনের chat পড়তে পারে না। Firestore rules publish হয়েছে কি না যাচাই করুন।
- Chat send, refresh-এর পর history, new chat, switch/delete/clear এবং API-key remove পরীক্ষা করুন।
- ১০০টি successful response পূরণ করার আগে test plan/usage cost বুঝে নিন; ৩০-second lock app-এর interface-এ কাজ করে।
- Public launch-এর আগে privacy notice, data retention/deletion policy, rate-limit/abuse handling এবং Firebase/Render logs-এ secrets না যাওয়া পরীক্ষা করুন।

## Free-tier ও সীমা

Render Free service idle হলে sleep/cold start হতে পারে; persistent server disk-এর ওপর chat history নির্ভর করে না—Firebase Firestore config হলে cloud data সেখানে থাকে। Firebase Spark ও provider-এর quota আছে। AI provider API, GPU/video service বা ad placement-এর খরচ/approval আলাদা। এই ZIP deploy-ready starter; public SaaS-এর পূর্ণ security, billing, monitoring বা moderation system নয়।
