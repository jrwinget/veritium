# Veritium - Scientific Article Verification System

[![Deploy to GitHub Pages](https://github.com/jrwinget/veritium/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)](https://github.com/jrwinget/veritium/actions/workflows/deploy.yml)
[![Docker Build](https://github.com/jrwinget/veritium/workflows/Docker%20Build/badge.svg)](https://github.com/jrwinget/veritium/actions/workflows/docker-build.yml)
[![Backend CI](https://github.com/jrwinget/veritium/workflows/Backend%20CI/badge.svg)](https://github.com/jrwinget/veritium/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/jrwinget/veritium/workflows/Frontend%20CI/badge.svg)](https://github.com/jrwinget/veritium/actions/workflows/frontend-ci.yml)

An open-source web application that analyzes scientific articles and evaluates how well they support user-provided claims. Built with transparency, accessibility, and reproducibility in mind.

## Features

### Core Functionality
- **Document Processing**: Upload PDFs/DOCX, fetch by URL/DOI
- **Claim Extraction**: Automatic extraction of key findings and conclusions
- **Similarity Analysis**: Semantic similarity matching between user claims and document content
- **Quality Assessment**: Methodological quality scoring based on research best practices
- **Evidence-Based Explanations**: Plain-language explanations with component scores
- **Shareable Results**: Generate shareable links for assessments
- **Feedback System**: Capture user feedback to improve accuracy

### Technical Features
- **Transparent Scoring**: Shows component scores, weights, and evidence sources
- **Accessibility First**: WCAG 2.1 AA compliance, keyboard navigation, ARIA labels
- **Reproducible Setup**: Docker Compose for consistent development environment
- **Comprehensive Testing**: Unit tests with ≥80% coverage
- **Optional LLM Integration**: Toggleable LLM-assisted analysis

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd veritium

# Start the application
docker-compose up --build

# Access the application
open http://localhost:3000
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture Overview

### Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration and utilities
│   ├── db/               # Database models and connections
│   ├── models/           # SQLAlchemy models
│   ├── services/         # Business logic
│   └── tests/            # Unit tests
├── requirements.txt      # Python dependencies
└── Dockerfile
```

**Key Services:**
- `DocumentService`: PDF/DOCX processing, URL/DOI fetching
- `TextExtractor`: Text extraction and metadata parsing
- `ClaimExtractor`: Heuristic + optional LLM claim extraction
- `QualityScorer`: Methodological quality assessment
- `SimilarityService`: Semantic similarity and evidence matching
- `AssessmentService`: Overall confidence scoring and assessment
- `ExplanationService`: Plain-language explanation generation

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/       # React components
│   ├── services/         # API client
│   ├── types/            # TypeScript definitions
│   └── utils/            # Utility functions
├── package.json          # Node dependencies
└── Dockerfile
```

**Key Components:**
- `HomePage`: Document upload and claim input
- `AssessmentPage`: Results display with scores and explanations
- `ScoreDisplay`: Transparent component score visualization
- `EvidenceSnippets`: Highlighted evidence passages
- `Citations`: Source citations with relevance scores

### Database (SQLite)
- `documents`: Stores processed papers and metadata
- `assessments`: Stores claim assessments and results

## CI/CD & Deployment

### GitHub Actions Workflows

The project includes automated CI/CD pipelines:

- **Backend CI**: Python testing, linting (flake8), formatting (Black), type checking (mypy)
- **Frontend CI**: Node.js testing, linting (ESLint), TypeScript compilation, build verification
- **Docker Build**: Multi-service container builds and integration testing
- **GitHub Pages Deploy**: Automatic deployment to GitHub Pages on main branch pushes
- **Status Check**: Repository health monitoring and scheduled checks

All workflows run on push/PR to main branch and include caching for faster builds.

### Deployment

**GitHub Pages**: Frontend is automatically deployed to GitHub Pages at `https://jrwinget.github.io/veritium/`

**Backend Deployment**: Configure your preferred service (Railway, Render, Fly.io) in the deploy workflow.

## Configuration

### Environment Variables

**Backend (.env):**
```bash
DATABASE_URL=sqlite:///data/veritium.db
USE_LLM=false                    # Enable/disable LLM features
LLM_MODEL=microsoft/DialoGPT-small
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_FILE_SIZE=52428800           # 50MB
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
```

### Model Downloads

The application will automatically download required models on first use:
- **Sentence Transformer**: `all-MiniLM-L6-v2` (~90MB)
- **LLM (optional)**: `microsoft/DialoGPT-small` (~350MB)

To pre-download models:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Demo Workflow

1. **Upload Document**: Drag & drop PDF, enter URL, or provide DOI
2. **Automatic Processing**: Text extraction, claim extraction, quality scoring
3. **Enter Claim**: Type your claim to verify (e.g., "Exercise reduces heart disease risk")
4. **Get Assessment**: View similarity scores, stance detection, confidence rating
5. **Review Evidence**: See matched text passages with relevance scores
6. **Share Results**: Generate shareable link for the assessment
7. **Provide Feedback**: Thumbs up/down to improve the system

## Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest app/tests/ -v --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm install
npm run test
npm run test:coverage
```

### Accessibility Testing
```bash
# Install axe-core
npm install -g @axe-core/cli

# Run accessibility audit
axe http://localhost:3000
```

## Sample Assets

Test the system with provided samples:
- `data/samples/sample_paper.txt`: Cardiovascular exercise study
- Upload and test with claims like:
  - "Exercise reduces blood pressure"
  - "Physical activity improves cholesterol"
  - "Meditation is better than exercise"

## API Reference

### Document Upload
```bash
# File upload
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@paper.pdf"

# URL fetch
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "url=https://example.com/paper.pdf"

# DOI fetch
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "doi=10.1000/123456"
```

### Create Assessment
```bash
curl -X POST "http://localhost:8000/api/v1/assessments/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "user_claim": "Exercise reduces heart disease"}'
```

## Limitations & Ethics

### Current Limitations
- **Language**: English text only
- **Document Types**: PDF and DOCX files only
- **Quality Assessment**: Heuristic-based, not domain-expert level
- **LLM Features**: Optional and experimental
- **Generalizability**: Trained on general scientific patterns

### Ethical Considerations
- **Research Tool Only**: Not for clinical or policy decisions
- **Human Oversight Required**: Always consult domain experts
- **Bias Awareness**: May inherit biases from training data
- **Transparency**: All component scores and evidence shown
- **Privacy**: No personal data collection

### Responsible Use
- Verify findings with original sources
- Consider multiple perspectives and studies
- Understand confidence intervals and limitations
- Use as starting point for deeper investigation

## Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd veritium

# Backend staging
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend staging
cd ../frontend
npm install
npm run dev

# Run tests
pytest backend/app/tests/
npm test --prefix frontend/
```

### Code Quality
- **Python**: Black formatting, flake8 linting, type hints
- **TypeScript**: ESLint, Prettier, strict type checking
- **Tests**: Minimum 80% coverage required
- **Accessibility**: WCAG 2.1 AA compliance

## License

Open source under MIT License. See LICENSE file for details.

## Roadmap

### Phase 1 (MVP) ✅
- [x] Core document processing pipeline
- [x] Similarity-based claim verification
- [x] Basic UI with accessibility features
- [x] Docker deployment setup

### Phase 2 (Enhancements)
- [ ] Advanced NLP models for better accuracy
- [ ] Multi-language support
- [ ] Integration with academic databases
- [ ] Advanced visualization and reporting

### Phase 3 (Scale)
- [ ] Production deployment guide
- [ ] API rate limiting and authentication
- [ ] Batch processing capabilities
- [ ] Performance optimization

## Support

For questions, issues, or contributions:
- GitHub Issues: [Report bugs or request features]
- Documentation: See `/docs` folder for detailed guides
- Community: [Link to discussions or forum]

---

**Disclaimer**: This tool provides automated analysis for research purposes only. Always consult original sources and domain experts for critical decisions. The system is designed to be transparent about its limitations and confidence levels.