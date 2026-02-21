# PolicySentinel Frontend Setup Guide

## Quick Start

The frontend is now complete and ready to use! Follow these steps to get it running.

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 3. Ensure Backend is Running

Make sure the backend API is running on `http://localhost:8000`:

```bash
# In the root directory
source venv/bin/activate
python src/main.py
```

## What's Included

### Pages

1. **Dashboard** (`/`) - Main compliance monitoring dashboard
   - Compliance score gauge
   - Key metrics (violations, policies, rules, records)
   - Severity breakdown
   - Quick stats
   - Scan for violations button

2. **Policies** (`/policies`) - Policy document management
   - Upload PDF policy documents
   - Extract rules with AI
   - View uploaded policies list
   - Track processing status

3. **Violations** (`/violations`) - Violation management
   - List all violations with filters
   - Filter by severity and status
   - View violation details
   - Track resolution progress

4. **Violation Details** (`/violations/[id]`) - Detailed violation view
   - Rule violated
   - AI-generated justification
   - Recommended remediation steps
   - Record data
   - Metadata (status, timestamp, risk score)

### Components

- `ComplianceGauge` - Semi-circular gauge for compliance score
- `MetricCard` - Reusable metric display cards
- `PolicyUpload` - File upload with AI rule extraction
- `ViolationTable` - Violations table with sorting and filtering

### API Integration

All API calls are handled through `lib/api.ts` using Axios. The API base URL is configured in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Demo Flow

### Complete End-to-End Demo

1. **Start Backend** (if not running)
   ```bash
   source venv/bin/activate
   python src/main.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Upload Policy** (http://localhost:3000/policies)
   - Click "Select PDF File"
   - Choose `sample_aml_policy.pdf` (created by `scripts/create_sample_policy.py`)
   - Click "Upload Policy"
   - Wait for success message
   - Click "Extract Rules with AI"
   - Wait 10-15 seconds for AI processing

4. **Scan for Violations** (http://localhost:3000)
   - Click "Scan for Violations" button
   - Wait 2-5 seconds for scan to complete
   - View updated metrics and compliance score

5. **Review Violations** (http://localhost:3000/violations)
   - See list of detected violations
   - Filter by severity or status
   - Click "View Details" on any violation
   - Read AI justification and remediation steps

## Tech Stack

- **Next.js 14** - React framework with App Router
- **Tailwind CSS 3** - Utility-first CSS
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **TypeScript** - Type safety

> **Note**: Using Next.js 14 for Node.js 18 compatibility. See `NODE_VERSION_FIX.md` for upgrade path.

## Features Implemented

✅ Real-time compliance dashboard
✅ Policy upload and management
✅ AI-powered rule extraction
✅ Violation detection and monitoring
✅ Compliance score visualization
✅ Detailed violation analysis
✅ AI justifications and remediation
✅ Filtering and sorting
✅ Responsive design
✅ Error handling

## Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## Troubleshooting

### API Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check `.env.local` has correct API URL
- Verify CORS is enabled in backend

### Dependencies Installation Failed
- Node.js version warning is expected (requires Node 20+, but works with 18)
- Run `npm install --legacy-peer-deps` if needed

### Page Not Loading
- Clear browser cache
- Delete `.next` folder and rebuild: `rm -rf .next && npm run dev`

## Next Steps

The frontend is complete and functional! You can now:

1. Test the complete flow with sample data
2. Customize styling and branding
3. Add more features (see tasks.md for remaining optional tasks)
4. Deploy to production

## Demo Tips

- Have sample data loaded before demo
- Practice the flow 2-3 times
- Keep browser console open to catch any errors
- Have screenshots ready as backup
- Emphasize the AI features (rule extraction, justifications)

## Time to Demo-Ready

You're already demo-ready! The frontend is complete and integrated with the backend. Just test the flow once and you're good to go.

**Total implementation time**: ~2 hours
**Demo preparation time**: ~30 minutes

🎉 **You're ready to win Round 3!**
