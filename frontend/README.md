# PolicySentinel Frontend

Next.js 14 frontend application for PolicySentinel compliance monitoring platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Visualization**: D3.js, Recharts
- **UI Components**: Custom components with Tailwind

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Dashboard (home page)
│   ├── layout.tsx         # Root layout with navigation
│   ├── policies/          # Policy management pages
│   ├── violations/        # Violation pages
│   ├── reviews/           # Review workflow pages
│   ├── predictions/       # ML predictions pages
│   ├── notifications/     # Notifications pages
│   ├── audit/             # Audit trail pages
│   └── feedback/          # Feedback loop pages
├── components/            # Reusable React components
│   ├── RuleGraphViewer.tsx
│   ├── ViolationTable.tsx
│   ├── NotificationBell.tsx
│   └── ...
├── public/                # Static assets
└── styles/                # Global styles
```

## Available Scripts

```bash
# Development
npm run dev          # Start development server

# Production
npm run build        # Build for production
npm start            # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript compiler check
```

## Features

- **Dashboard**: Overview of compliance metrics
- **Policy Management**: Upload and manage policies
- **Rule Graph**: Interactive D3.js visualization
- **Violations**: View and manage detected violations
- **Reviews**: Human review workflow
- **Predictions**: ML-powered risk predictions
- **Notifications**: Real-time alerts
- **Audit Trail**: Complete activity logging
- **Feedback**: AI accuracy tracking

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

Configure the API URL in your environment or update the fetch calls in components.

## Development

### Adding a New Page

1. Create a new folder in `app/`
2. Add `page.tsx` for the route
3. Update navigation in `app/layout.tsx`

### Adding a New Component

1. Create component in `components/`
2. Use TypeScript for type safety
3. Style with Tailwind CSS classes

## Build

```bash
npm run build
```

This creates an optimized production build in the `.next` folder.

## Deployment

The frontend can be deployed to:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker container
- Any Node.js hosting

## Environment Variables

Create a `.env.local` file for environment-specific configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
