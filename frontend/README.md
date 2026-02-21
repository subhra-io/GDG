# PolicySentinel Frontend

AI-powered compliance monitoring dashboard built with Next.js, Tailwind CSS, Axios, and Recharts.

## Features

- 📊 Real-time compliance dashboard with metrics
- 📄 Policy document upload and management
- 🔍 AI-powered rule extraction from PDFs
- ⚠️ Violation detection and monitoring
- 📈 Compliance score visualization
- 🎯 Detailed violation analysis with AI justifications

## Tech Stack

- **Next.js 14** - React framework with App Router (compatible with Node.js 18)
- **Tailwind CSS 3** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Recharts** - Charting library for data visualization
- **TypeScript** - Type-safe development

## Getting Started

### Prerequisites

- Node.js 18+ installed (currently using 18.20.8)
- Backend API running on `http://localhost:8000`

> **Note**: The project uses Next.js 14 for compatibility with Node.js 18. If you upgrade to Node.js 20+, you can upgrade to Next.js 16. See `NODE_VERSION_FIX.md` for details.

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard (home page)
│   ├── layout.tsx         # Root layout with navigation
│   ├── policies/          # Policy management pages
│   │   └── page.tsx
│   └── violations/        # Violations pages
│       ├── page.tsx       # Violations list
│       └── [id]/page.tsx  # Violation details
├── components/            # Reusable React components
│   ├── ComplianceGauge.tsx
│   ├── MetricCard.tsx
│   ├── PolicyUpload.tsx
│   └── ViolationTable.tsx
├── lib/                   # Utilities and API client
│   └── api.ts            # Axios API client
└── public/               # Static assets
```

## Pages

### Dashboard (`/`)
- Compliance score gauge
- Key metrics (violations, policies, rules, records)
- Severity breakdown
- Quick stats
- Scan for violations button

### Policies (`/policies`)
- Upload policy PDF documents
- Extract rules with AI
- View uploaded policies
- Track processing status

### Violations (`/violations`)
- List all violations
- Filter by severity and status
- View violation details
- Track resolution progress

### Violation Details (`/violations/[id]`)
- Rule violated
- AI-generated justification
- Recommended remediation steps
- Record data
- Metadata (status, timestamp, risk score)

## API Integration

The frontend connects to the backend API using Axios. Configuration is in `lib/api.ts`.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### API Endpoints Used

- `POST /policies/upload` - Upload policy PDF
- `POST /policies/{id}/extract-rules` - Extract rules with AI
- `GET /policies` - List policies
- `POST /violations/scan` - Scan for violations
- `GET /violations` - List violations
- `GET /violations/{id}` - Get violation details
- `GET /dashboard/metrics` - Get dashboard metrics

## Components

### ComplianceGauge
Displays compliance score as a semi-circular gauge with color coding:
- Green (80-100): Good compliance
- Yellow (60-79): Moderate compliance
- Red (0-59): Poor compliance

### MetricCard
Reusable card component for displaying metrics with optional trends and color themes.

### PolicyUpload
File upload component with:
- PDF file selection
- Upload progress
- AI rule extraction trigger
- Status messages

### ViolationTable
Table component displaying violations with:
- Rule description
- Severity badges
- Status indicators
- Action links

## Styling

Uses Tailwind CSS 4 with custom configuration. Color scheme:
- Primary: Blue (#2563eb)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Danger: Red (#ef4444)

## Development Tips

### Hot Reload
Next.js automatically reloads when you save files. No need to restart the dev server.

### Type Safety
TypeScript is configured for strict mode. Add proper types for API responses.

### API Errors
All API calls include error handling. Check browser console for detailed error messages.

### CORS
Backend is configured to allow requests from `http://localhost:3000`. Update CORS settings if deploying to a different domain.

## Troubleshooting

### API Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check `.env.local` has correct API URL
- Verify CORS is enabled in backend

### Build Errors
- Run `npm install` to ensure all dependencies are installed
- Clear `.next` folder: `rm -rf .next`
- Check TypeScript errors: `npm run lint`

### Styling Issues
- Tailwind CSS 4 uses new `@import "tailwindcss"` syntax
- Check `app/globals.css` for proper imports
- Verify `postcss.config.mjs` is configured correctly

## Demo Flow

1. **Upload Policy** (`/policies`)
   - Select PDF file
   - Click "Upload Policy"
   - Click "Extract Rules with AI"
   - Wait 10-15 seconds for AI processing

2. **Scan for Violations** (`/`)
   - Click "Scan for Violations" on dashboard
   - Wait for scan to complete
   - View updated metrics

3. **Review Violations** (`/violations`)
   - Filter by severity or status
   - Click "View Details" on any violation
   - Read AI justification and remediation steps

## Performance

- Initial page load: ~1-2 seconds
- API calls: ~100-500ms (local backend)
- AI rule extraction: ~10-15 seconds
- Violation scan: ~2-5 seconds

## Future Enhancements

- [ ] Real-time updates with WebSockets
- [ ] Export violations to CSV/PDF
- [ ] Advanced filtering and search
- [ ] Violation workflow management
- [ ] User authentication
- [ ] Role-based access control
- [ ] Audit trail
- [ ] Email notifications

## License

MIT

## Support

For issues or questions, check the main project README or contact the development team.
