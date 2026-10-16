# Mahim AI — Public GitHub repo shortlist (approve before integration)

## কী করা হয়েছে

এটি সব GitHub repository-র পূর্ণ তালিকা নয়—public repository অসংখ্য। Mahim AI-র Bengali-first UI এবং GitHub → Firebase → Render architecture-এর সঙ্গে মেলে এমন কয়েকটি যাচাইযোগ্য প্রার্থী বেছে নেওয়া হয়েছে। **এই shortlist-এর কোনো external repo/code এখনো app-এ merge করা হয়নি।** আপনি অনুমোদন দিলে একে একে license, dependency, secrets, security ও runtime পরীক্ষা করে যোগ করব।

## প্রস্তাবিত প্রার্থী

| Priority | Feature / repository | License | কী যোগ হবে | খরচ/ঝুঁকি ও সিদ্ধান্ত |
|---|---|---|---|---|
| 1 | [Mozilla PDF.js](https://github.com/mozilla/pdf.js) | Apache-2.0 | Browser-এ PDF দেখা ও text extraction; chat-এ PDF reference দেওয়ার ভিত্তি। | Library নিজে free; PDF-টি user-এর browser-এই পড়া যায়। বড় file ও PDF-র security/size limit পরীক্ষা করতে হবে। **প্রথম ধাপে ভালো candidate।** |
| 2 | [Tesseract.js](https://github.com/naptha/tesseract.js) | Apache-2.0 | Image/scan থেকে OCR text বের করা; browser বা Node-এ চলে। | WASM ও language data download/load করতে হবে; Bengali OCR quality sample দিয়ে পরীক্ষা দরকার। **PDF.js-এর পরে যোগ করা যায়।** |
| 3 | [GrapesJS](https://www.npmjs.com/package/grapesjs) | BSD-3-Clause | বর্তমান static landing-page form-কে drag-and-drop visual website builder-এ উন্নীত করা। | Editor-এর UI ও exported HTML/CSS integration দরকার; hosting ও domain স্বয়ংক্রিয় নয়। **দ্বিতীয় ধাপের ভালো candidate।** |
| 4 | [Google APIs Node.js client](https://github.com/googleapis/google-api-nodejs-client) | Apache-2.0 | OAuth দিয়ে Google Drive/Docs/Sheets/Calendar-এর নির্দিষ্ট action সংযোগের client library। | Google Cloud project, OAuth consent, scopes, user permission ও secure server setup লাগবে। **শুধু নির্বাচিত Google service অনুমোদন নিয়ে যোগ করতে হবে।** |
| 5 | [SearXNG](https://github.com/searxng/searxng) | AGPL-3.0 | নিজস্ব server-এ metasearch; web search adapter-এর ভিত্তি হতে পারে। | আলাদা Python service/hosting ও operational maintenance দরকার; AGPL-3.0 network deployment-এ source-sharing শর্ত থাকতে পারে। Upstream search engines rate-limit/block করতে পারে। **প্রথম পছন্দ নয়; license review চাই।** |
| 6 | [Official MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) | নতুন code Apache-2.0; পূর্বের code-এর license আলাদা হতে পারে | ভবিষ্যতে অনুমোদিত tool servers-এ standard protocol দিয়ে সংযোগের ভিত্তি। | MCP SDK নিজে Google Drive, email বা অন্য tool দেয় না; প্রতিটি server আলাদা, আলাদা permissions ও security audit লাগে। **Advanced; এখনই নির্বিচারে চালু নয়।** |
| 7 | [Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1) | Repo/model card অনুযায়ী Apache-2.0; weights-এর terms আলাদা করে যাচাই করতে হবে | Self-hosted text/image-to-video model। | Official repo-তে ছোট 1.3B variant-এরও প্রায় 8 GB VRAM ও generation time-এর কথা আছে; free hosting-এ বাস্তবসম্মত নয়। GPU/cloud cost ও model-weight license যাচাই দরকার। **GPU host না থাকলে এখন যোগ করা ঠিক হবে না।** |
| 8 | [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | GPL-3.0 | Self-hosted image/video diffusion workflow backend ও API। | GPU server, model weights, storage এবং GPL-3.0 review দরকার। **সরাসরি app-এর মধ্যে merge নয়; আলাদা GPU service হিসেবে বিবেচনা।** |

## Repository ছাড়াই কম খরচে যোগ করা যেতে পারে

- Browser-এর built-in speech synthesis দিয়ে AI answer পড়ে শোনানো এবং কিছু browser-এ speech recognition। Device/browser support একরকম নয়; Bengali quality পরীক্ষা করতে হবে।
- PDF/image attachment size/type limits, local preview এবং user consent/privacy notice।
- বর্তমান profile, chat list, API-key tab, Firebase Auth/Firestore skeleton ও provider adapters ইতিমধ্যে project-এ আছে; পুনরায় অন্য repo থেকে কপি দরকার নেই।

## এখনই যা indiscriminately যোগ করব না

- “সব public repo” একসঙ্গে—সংখ্যা অসীম, অনেক repo stale, malicious, incompatible বা restrictive-license হতে পারে।
- Random MCP/tool servers, scraped TV/live streams, unapproved ad scripts, বা model weights যাদের terms পরিষ্কার নয়।
- Video/image generation-কে free দাবি করা—API usage বা GPU hosting খরচ হতে পারে।

## অনুমোদনের জন্য প্রথম batch প্রস্তাব

1. PDF.js (PDF view/extract)
2. Tesseract.js (image OCR; Bengali test-এর পরে)
3. GrapesJS (visual website builder)
4. Browser-native text-to-speech (external repo ছাড়া)

তারপর আপনি চাইলে Google Drive/Docs OAuth integration; live search-এর জন্য SearXNG-এর AGPL review অথবা একটি অনুমোদিত search API; video generation-এর জন্য আলাদা GPU/API provider বেছে নেওয়া হবে।

## GitHub + Firebase + Render

বর্তমান app backend `server.py` Python-এ এবং `render.yaml` Render-এর Python web service সেট করে। তাই core app আগে GitHub → Firebase → Render-এ চালু ও পরীক্ষা করুন। External repo যোগ করলে তার license, dependencies, secrets handling এবং Render-এর Python/static setup-এর সঙ্গে compatibility যাচাই করতে হবে; Node-ভিত্তিক integration হলে আলাদা migration লাগতে পারে।
