# Mahim AI চালু করার ধাপ — GitHub + Firebase + Render

এই project GitHub-এ source, Firebase-এ sign-in/chat history এবং Render-এ website/API চালানোর জন্য সাজানো। `firebase-config.js`-এ আপনি যে Web App config দিয়েছেন তা বসানো হয়েছে—সেটি সত্যিই আপনার Firebase project-এর config কি না যাচাই করুন। কোনো password, provider API secret বা Firebase Admin private key GitHub/chat-এ দেবেন না।

## ১) GitHub-এ code তুলুন

1. GitHub-এ `mahim-ai` নামে repository তৈরি করুন; setup শেষ হওয়া পর্যন্ত Private রাখা নিরাপদ।
2. ZIP extract করে `mahim-ai` folder-এর **ভেতরের files** repository root-এ রাখুন। `render.yaml`, `server.py`, `firebase-config.js`, `firestore.rules` ও `firebase.json` অবশ্যই থাকবে।
3. প্রথমে config যাচাই করুন; পরিবর্তন করলে commit/push করুন। `firebase-config.js` হলো public Firebase Web App client config—Admin service-account JSON নয়। Provider API keys এই ফাইলে রাখবেন না।

## ২) Firebase Auth ও Firestore

1. Firebase Console-এ project ID `mahim-ai-99f4e`-এর সঙ্গে মিলিয়ে Web App config যাচাই করুন। অন্য project হলে `firebase-config.js` আপডেট করুন।
2. **Authentication → Sign-in method**-এ Google এবং Email/Password enable করুন।
3. **Firestore Database** তৈরি করুন। Firebase CLI দরকার হলে:

```bash
npm install -g firebase-tools
firebase login
firebase use --add
firebase deploy --only firestore:rules
```

Deploy করার সময় CLI-তে সঠিক Firebase project বেছে নিন। Rules user-কে শুধু তার নিজের `users/{uid}/chats` ও usage path-এ access দেয়। Firebase Web API key authorization নয়; data protection-এর জন্য Firestore rules জরুরি। Firebase API key শুধু Firebase services-এর জন্য ব্যবহার/সীমাবদ্ধ রাখুন।

## ৩) Render-এ deploy

1. Render account-এ GitHub connect করুন। **New → Blueprint** বেছে repository select করুন। `render.yaml` থেকে Python web service তৈরি হবে।
2. Blueprint environment value `FIREBASE_WEB_API_KEY`-এ Firebase Web App config-এর `apiKey`-এর একই value দিন। `REQUIRE_AUTH=true` রাখুন; এটি sign-in ছাড়া backend chat/image request আটকায়।
3. Deploy হয়ে Render URL পাওয়ার পর Firebase Console → **Authentication → Settings → Authorized domains**-এ Render hostname যোগ করুন। তারপর sign-in পরীক্ষা করুন।
4. `/api/health` URL খুলে service status দেখুন। Render Free service idle হলে sleep/cold start হতে পারে।

## ৪) App-এর ব্যবহার ও খরচ

- Sign-in করে **Profile → API keys**-এ নিজের provider, model ID ও API key দিন। Key এই browser tab-এর memory-তে থাকে; localStorage/GitHub-এ লেখা হয় না।
- Chat adapter: OpenAI, Gemini, Anthropic, OpenRouter, Groq ও Together AI। Image endpoint বর্তমানে OpenAI-only। Provider-ভেদে quota/charge আলাদা; free hosting AI usage-কে free করে না।
- Firebase config-এ `measurementId` আছে, তবে Firebase Analytics এখনো চালু করা হয়নি। Analytics চালু করার আগে privacy notice/consent ঠিক করুন।

## ৫) Publisher ad tags

আপনার দেওয়া Native Banner, 300×250 Banner, Social Bar, Popunder ও Smartlink code app-এ যোগ করা হয়েছে। Social Bar/Popunder site-wide script, তাই break-এর বাইরেও দেখাতে/trigger হতে পারে; দুইটি banner timed break-এ load হয়; Smartlink break panel-এর user-click link। প্রতি ১০০টি successful chat response-এর পর ৩০-second UI break দেখায়; এই code আপনার approved publisher account থেকে এসেছে কি না যাচাই করুন। Domain approval, tracking/consent, actual fill ও payout এখানে test করা হয়নি; tag থাকলেই ad দেখা বা revenue নিশ্চিত হয় না। Consent gate তৈরি করা হয়নি—আপনার publisher policy ও প্রযোজ্য privacy law অনুযায়ী live traffic চালুর আগে consent ব্যবস্থা করুন।

## ৬) পরীক্ষা ও public launch

- Google/email sign-in, password reset, user-specific chat history, new/switch/delete/clear chat এবং API key remove পরীক্ষা করুন।
- দুইটি test account দিয়ে নিশ্চিত করুন একজন অন্যজনের Firestore chat পড়তে পারে না।
- Provider key, Firebase Admin private key, password বা `.env` GitHub-এ push করবেন না।
- Public launch-এর আগে privacy/retention notice, abuse/rate limits, monitoring/log redaction ও data deletion policy পর্যালোচনা করুন। Video generation, live TV/streams, live web search ও arbitrary external tools আলাদা integration ছাড়া চালু নয়।
