# 🌊 ARGO AI - FloatChat Enhanced

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/yourusername/argoai)

**AI-Powered Conversational Interface for ARGO Ocean Data Analysis**

An advanced oceanographic data analysis platform that combines ARGO float data with AI-powered conversational interfaces, providing intuitive access to ocean observations through natural language queries and sophisticated visualizations.

---

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📊 Data Flow Diagram](#-data-flow-diagram)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [📖 Usage](#-usage)
- [🔧 API Reference](#-api-reference)
- [📁 Project Structure](#-project-structure)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Support](#-support)

---

## 🌟 Features

### 🤖 AI-Powered Analysis
- **Natural Language Processing**: Query oceanographic data using plain English
- **RAG Pipeline**: Retrieval-Augmented Generation for contextual responses
- **Vector Search**: Semantic search across ARGO metadata and measurements
- **Smart Recommendations**: AI-driven insights and analysis suggestions

### 📊 Advanced Visualizations
- **Interactive 2D/3D Plots**: Temperature, salinity, and pressure profiles
- **Geographic Maps**: Float trajectories and ocean basin coverage
- **Time Series Analysis**: Historical trends and seasonal variations
- **Statistical Dashboards**: Histograms, scatter plots, and correlation matrices

### 🌐 Data Management
- **Real-time Data Ingestion**: Automated ARGO data processing
- **Multi-format Support**: NetCDF, Parquet, and CSV compatibility
- **Database Integration**: PostgreSQL with vector search capabilities
- **Efficient Storage**: Optimized data structures for large-scale analysis

### 📱 User Interface
- **Responsive Design**: Desktop and mobile-friendly interface
- **Dark/Light Themes**: Customizable viewing experience
- **Export Capabilities**: Download plots, data, and reports
- **Real-time Updates**: Live data synchronization and notifications

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "External Data Sources"
        A[ARGO FTP Server]
        B[INCOIS Portal]
        C[Regional ARGO Centers]
    end
    
    subgraph "Data Ingestion Layer"
        D[ARGO Data Ingestion]
        E[Data Validation]
        F[Format Conversion]
    end
    
    subgraph "Storage Layer"
        G[(PostgreSQL Database)]
        H[(ChromaDB Vector Store)]
        I[(File System - NetCDF)]
    end
    
    subgraph "AI/ML Layer"
        J[Vector Store Manager]
        K[LLM Integration]
        L[RAG Pipeline]
        M[Embedding Generator]
    end
    
    subgraph "Application Layer"
        N[Streamlit UI]
        O[Database Manager]
        P[Visualization Engine]
        Q[Query Processor]
    end
    
    subgraph "User Interface"
        R[Web Dashboard]
        S[Chat Interface]
        T[Plot Gallery]
        U[Data Explorer]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    
    G --> O
    H --> J
    I --> O
    
    J --> L
    K --> L
    M --> H
    
    L --> Q
    O --> N
    P --> N
    Q --> N
    
    N --> R
    N --> S
    N --> T
    N --> U
```

---

## 📊 Data Flow Diagram

### 🔄 Complete Data Processing Pipeline

```mermaid
flowchart TD
    subgraph "Data Ingestion"
        A1[ARGO NetCDF Files<br/>263 files] --> A2[Data Validation<br/>QC Checks]
        A2 --> A3[Metadata Extraction<br/>Float Info, Locations]
        A3 --> A4[Data Transformation<br/>Standardization]
    end
    
    subgraph "Storage & Indexing"
        A4 --> B1[(PostgreSQL<br/>Structured Data)]
        A4 --> B2[(ChromaDB<br/>Vector Embeddings)]
        A4 --> B3[(Local Files<br/>NetCDF Archive)]
    end
    
    subgraph "AI Processing"
        B2 --> C1[Embedding Generator<br/>Sentence Transformers]
        C1 --> C2[Vector Search<br/>Semantic Similarity]
        C2 --> C3[RAG Pipeline<br/>Context Retrieval]
        C3 --> C4[LLM Processing<br/>Google Gemini]
    end
    
    subgraph "Query Processing"
        D1[User Query] --> D2[Intent Detection]
        D2 --> D3[Query Classification]
        D3 --> D4[Data Retrieval]
        D4 --> D5[Response Generation]
    end
    
    subgraph "Visualization"
        B1 --> E1[Data Aggregation]
        E1 --> E2[Plot Generation<br/>Plotly/Matplotlib]
        E2 --> E3[Interactive Maps<br/>Folium]
        E3 --> E4[Dashboard Assembly]
    end
    
    subgraph "User Interface"
        D5 --> F1[Chat Response]
        E4 --> F2[Visual Dashboard]
        F1 --> F3[Streamlit UI]
        F2 --> F3
        F3 --> F4[User Experience]
    end
    
    %% Styling
    classDef ingestion fill:#e1f5fe
    classDef storage fill:#f3e5f5
    classDef ai fill:#e8f5e8
    classDef query fill:#fff3e0
    classDef viz fill:#fce4ec
    classDef ui fill:#f1f8e9
    
    class A1,A2,A3,A4 ingestion
    class B1,B2,B3 storage
    class C1,C2,C3,C4 ai
    class D1,D2,D3,D4,D5 query
    class E1,E2,E3,E4 viz
    class F1,F2,F3,F4 ui
```

### 🔍 Query Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit UI
    participant QP as Query Processor
    participant VS as Vector Store
    participant LLM as Google Gemini
    participant DB as Database
    participant VIZ as Visualizer
    
    User->>UI: Submit natural language query
    UI->>QP: Process query intent
    
    alt Data Query
        QP->>VS: Search for relevant context
        VS->>QP: Return similar embeddings
        QP->>LLM: Generate response with context
        LLM->>QP: Return AI response
        QP->>DB: Fetch requested data
        DB->>QP: Return data results
        QP->>UI: Send response + data
    else Visualization Request
        QP->>DB: Query oceanographic data
        DB->>VIZ: Provide dataset
        VIZ->>UI: Generate interactive plots
    else Analysis Request
        QP->>DB: Fetch comprehensive data
        QP->>LLM: Request analytical insights
        LLM->>QP: Return analysis
        QP->>VIZ: Create supporting visuals
        VIZ->>UI: Render analysis dashboard
    end
    
    UI->>User: Display results
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- 4GB+ RAM recommended
- Google Gemini API key

### 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/argoai.git
cd argoai

# Run automated setup
python setup.py

# Configure your API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Launch the application
streamlit run app2.py
```

Your ARGO AI interface will be available at `http://localhost:8501`

---

## 📦 Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/argoai.git
cd argoai

# Install dependencies and setup environment
python setup.py
```

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Setup Directories
```bash
mkdir -p data/argo_data data/chroma_db logs outputs
```

#### Step 4: Configure Environment
```bash
cp config/.env.example .env
# Edit .env with your settings
```

### Option 3: Docker Setup

```bash
# Build Docker image
docker build -t argoai:latest .

# Run container
docker run -p 8501:8501 -v ./data:/app/data argoai:latest
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: AI/LLM Configuration
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/argoai
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Optional: Data Sources
ARGO_FTP_URL=ftp://ftp.ifremer.fr/ifremer/argo
INDIAN_ARGO_URL=https://incois.gov.in/OON/index.jsp

# Optional: Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_PROFILES_PER_FLOAT=1000
CHUNK_SIZE=100

# Optional: AI Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
MAX_TOKENS=4000
TEMPERATURE=0.1
```

### Database Configuration

#### PostgreSQL Setup (Recommended for Production)
```sql
-- Create database
CREATE DATABASE argoai;

-- Create user
CREATE USER argoai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE argoai TO argoai_user;
```

#### SQLite (Development)
For development, the application will automatically use SQLite if PostgreSQL is not available.

---

## 📖 Usage

### 🎯 Basic Usage

1. **Start the Application**
   ```bash
   streamlit run app2.py
   ```

2. **Load ARGO Data**
   - Place your NetCDF files in `data/argo_data/`
   - The system will automatically process them on startup

3. **Query Your Data**
   ```text
   "Show me temperature profiles for the Indian Ocean in 2023"
   "Compare salinity trends between Arabian Sea and Bay of Bengal"
   "What are the typical temperature ranges at 1000m depth?"
   ```

### 🗣️ Natural Language Queries

The AI system understands various query types:

#### Geographic Queries
```text
- "Show data from the Arabian Sea"
- "Temperature profiles near the equator"
- "Salinity measurements in the Bay of Bengal"
```

#### Temporal Queries
```text
- "Data from the last 6 months"
- "Seasonal temperature variations in 2023"
- "Monthly average salinity trends"
```

#### Parameter Queries
```text
- "Temperature vs depth profiles"
- "Pressure measurements below 1000m"
- "Quality controlled salinity data only"
```

#### Analytical Queries
```text
- "Correlation between temperature and salinity"
- "Anomalies in recent temperature data"
- "Statistical summary of float measurements"
```

### 📊 Visualization Features

#### Interactive Plots
- **Profile Plots**: T-S diagrams, depth profiles
- **Time Series**: Temporal analysis and trends
- **Geographic Maps**: Float locations and trajectories
- **Statistical Plots**: Histograms, box plots, scatter plots

#### Export Options
- PNG/SVG for high-quality images
- CSV/JSON for data export
- Interactive HTML plots
- PDF reports

---

## 🔧 API Reference

### Core Classes

#### `ARGODataIngestion`
```python
from src.ingestion.argo_ingestion import ARGODataIngestion

ingestion = ARGODataIngestion()

# Load NetCDF files
data = ingestion.load_netcdf_files("data/argo_data/")

# Process and validate data
processed_data = ingestion.process_argo_data(data)
```

#### `DatabaseManager`
```python
from src.database.database_manager import DatabaseManager

db = DatabaseManager()

# Query data
results = db.query_by_location(
    lat_min=0, lat_max=30,
    lon_min=60, lon_max=100
)

# Get float information
float_info = db.get_float_details(float_id=12345)
```

#### `ARGORAGPipeline`
```python
from src.ai.rag_pipeline import ARGORAGPipeline

rag = ARGORAGPipeline()

# Process natural language query
response = rag.process_query(
    "What is the average temperature at 500m depth?"
)
```

#### `ARGOVisualizer`
```python
from src.visualization.argo_plots import ARGOVisualizer

viz = ARGOVisualizer()

# Create temperature profile plot
fig = viz.create_profile_plot(
    data=temperature_data,
    parameter='temperature'
)
```

---

## 📁 Project Structure

```
argoai/
├── 📱 app2.py                          # Main Streamlit application
├── ⚙️ setup.py                         # Project setup and installation
├── 📋 requirements.txt                 # Python dependencies
├── 📄 README.md                        # Project documentation
│
├── 📁 config/                          # Configuration files
│   ├── .env.example                    # Environment template
│   └── database.yaml                   # Database configurations
│
├── 📁 src/                             # Source code
│   ├── 🔧 config.py                    # Application configuration
│   ├── 📁 ai/                          # AI/ML components
│   │   ├── llm_integration.py          # LLM wrapper and integration
│   │   ├── rag_pipeline.py             # RAG pipeline implementation
│   │   └── vector_store.py             # Vector database management
│   ├── 📁 database/                    # Database layer
│   │   ├── database_manager.py         # Database operations
│   │   └── models.py                   # Data models
│   ├── 📁 ingestion/                   # Data ingestion
│   │   └── argo_ingestion.py           # ARGO data processing
│   └── 📁 visualization/               # Plotting and visualization
│       ├── argo_plots.py               # Core plotting functions
│       └── enhanced_plots.py           # Advanced visualizations
│
├── 📁 data/                            # Data storage
│   ├── 📁 argo_data/                   # NetCDF files (263 files)
│   └── 📁 chroma_db/                   # Vector database storage
│
├── 📁 logs/                            # Application logs
├── 📁 outputs/                         # Generated outputs
├── 📁 scripts/                         # Utility scripts
├── 📁 tests/                           # Test files (organized)
├── 📁 docs/                            # Documentation
├── 📁 deployment/                      # Deployment configurations
└── 📁 venv/                            # Virtual environment
```

### 🔍 Key Components

| Component | Description | Technologies |
|-----------|-------------|-------------|
| **Frontend** | Interactive web interface | Streamlit, Plotly, Folium |
| **AI Engine** | Natural language processing | Google Gemini, LangChain |
| **Vector Store** | Semantic search capabilities | ChromaDB, FAISS |
| **Database** | Structured data storage | PostgreSQL, SQLAlchemy |
| **Visualization** | Advanced plotting engine | Plotly, Matplotlib, Seaborn |
| **Data Processing** | Oceanographic data handling | Pandas, Xarray, Dask |

---

## 🛠️ Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/argoai.git
cd argoai

# Create development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_database.py -v
pytest tests/test_ai/ -v

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
pylint src/

# Type checking
mypy src/
```

### Adding New Features

1. **Data Sources**: Add new ingestion modules in `src/ingestion/`
2. **Visualizations**: Extend `src/visualization/` with new plot types
3. **AI Models**: Integrate new models in `src/ai/`
4. **Database Models**: Update `src/database/models.py`

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow our coding standards
4. **Add tests**: Ensure your code is well-tested
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**: Describe your changes

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include unit tests for new features
- Update documentation as needed
- Ensure backward compatibility

---

## 📊 Data Sources

### ARGO Float Data
- **Global ARGO Data**: ftp://ftp.ifremer.fr/ifremer/argo
- **Indian Ocean ARGO Network**: https://incois.gov.in/OON/index.jsp
- **Regional ARGO Centers**: Various national and international sources

### Supported Data Formats
- **NetCDF4**: Primary format for ARGO data
- **Parquet**: Optimized for analytics
- **CSV**: For data exchange
- **JSON**: Metadata and configuration

### Data Variables
The system processes various oceanographic parameters:

| Variable | Description | Units |
|----------|-------------|--------|
| `TEMP` | Sea water temperature | °C |
| `PSAL` | Practical salinity | PSU |
| `PRES` | Sea water pressure | dbar |
| `LATITUDE` | Latitude of measurement | degrees_north |
| `LONGITUDE` | Longitude of measurement | degrees_east |
| `JULD` | Julian date | days |
| `PLATFORM_NUMBER` | Float identifier | - |
| `CYCLE_NUMBER` | Profile cycle | - |
| `DATA_MODE` | Data processing mode | - |

---

## 🚀 Deployment

### Production Deployment

#### Option 1: Streamlit Cloud
```bash
# Push to GitHub
git push origin main

# Connect repository to Streamlit Cloud
# Add secrets in Streamlit Cloud dashboard
```

#### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Option 3: Cloud Platform (AWS/GCP/Azure)
```bash
# Example for AWS ECS
docker build -t argoai .
docker tag argoai:latest your-registry/argoai:latest
docker push your-registry/argoai:latest
```

### Environment Configuration

#### Production Environment Variables
```env
# Production settings
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://prod_user:password@prod-db:5432/argoai

# Performance optimizations
MAX_PROFILES_PER_FLOAT=2000
CHUNK_SIZE=500
```

---

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Geographic and temporal indices
- **Partitioning**: By date ranges and geographic regions
- **Connection Pooling**: Efficient database connections

### Caching Strategy
- **Application Cache**: Frequently accessed data
- **Query Cache**: Common analysis results
- **Vector Cache**: Embedding search results

### Resource Management
- **Memory Usage**: Efficient data structures
- **CPU Utilization**: Parallel processing where applicable
- **Disk I/O**: Optimized file operations

---

## 🔒 Security

### API Security
- **API Key Management**: Secure credential handling
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Sanitize user inputs

### Data Security
- **Database Encryption**: Encrypted connections
- **File Security**: Secure file handling
- **Access Control**: Role-based permissions

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 ARGO AI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

### Getting Help
- 📧 **Email**: support@argoai.project
- 💬 **GitHub Issues**: [Create an issue](https://github.com/yourusername/argoai/issues)
- 📖 **Documentation**: [Full documentation](https://argoai.readthedocs.io)
- 🗨️ **Discussions**: [GitHub Discussions](https://github.com/yourusername/argoai/discussions)

### Troubleshooting

#### Common Issues

**1. API Key Errors**
```bash
# Check your .env file
cat .env | grep GOOGLE_API_KEY

# Verify API key format
# Should be: GOOGLE_API_KEY=AIza...
```

**2. Database Connection Issues**
```bash
# Test database connection
python -c "from src.database.database_manager import DatabaseManager; db = DatabaseManager(); print('Connected successfully' if db.test_connection() else 'Connection failed')"
```

**3. Memory Issues**
```bash
# Monitor memory usage
python -c "import psutil; print(f'Memory usage: {psutil.virtual_memory().percent}%')"

# Reduce batch size in config
export CHUNK_SIZE=50
```

**4. Port Already in Use**
```bash
# Run on different port
streamlit run app2.py --server.port 8502
```

### Performance Monitoring
- **Application Metrics**: Built-in performance monitoring
- **Error Tracking**: Comprehensive error logging
- **Usage Analytics**: User interaction tracking

---

## 🏆 Acknowledgments

### Contributors
- **Development Team**: Core development and maintenance
- **Data Scientists**: Oceanographic domain expertise
- **UI/UX Designers**: Interface design and user experience

### Data Sources
- **ARGO Program**: Global ocean observation network
- **INCOIS**: Indian National Centre for Ocean Information Services
- **Ifremer**: French Research Institute for Exploitation of the Sea

### Technologies
- **Streamlit**: Interactive web application framework
- **Google Gemini**: Advanced language model capabilities
- **ChromaDB**: Vector database for semantic search
- **Plotly**: Interactive visualization library

---

## 📊 Project Statistics

![GitHub stars](https://img.shields.io/github/stars/yourusername/argoai?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/argoai?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/argoai)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/argoai)

- **Lines of Code**: ~15,000+
- **Data Files Supported**: 263 NetCDF files
- **Ocean Parameters**: 12+ oceanographic variables
- **AI Models**: Multiple LLM and embedding models
- **Visualization Types**: 20+ plot categories
- **Geographic Coverage**: Global ocean basins

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/argoai&type=Date)](https://star-history.com/#yourusername/argoai&Date)

---

**Built with ❤️ for the oceanographic community**

*Empowering ocean scientists with AI-driven data analysis tools*

---

<div align="center">

### 🌊 Explore the Ocean with AI 🤖

[**Get Started**](https://github.com/yourusername/argoai#-quick-start) • [**Documentation**](https://argoai.readthedocs.io) • [**Examples**](./examples/) • [**API**](./docs/api.md)

</div>
