# Offline + Cash Hybrid Payment

30% deposit online, 70% cash at office.

## Features
- Online deposit (Stripe/Telr)
- Cash payment tracking
- Auto receipt generation (PDF)
- Multi-stage payment flow

## Setup
\`\`\`bash
npm install
cp .env.example .env
node server.js
\`\`\`

## Flow
1. Customer books online -> pays 30% deposit
2. Receives confirmation with cash instructions
3. Pays remaining 70% at office
4. Staff records cash payment -> generates receipt
