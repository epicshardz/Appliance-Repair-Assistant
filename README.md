# Appliance Repair Assistant

A cross-platform mobile and web application that helps homeowners and technicians repair appliances using AI and a context vector database.

## Project Structure

```
.
├── backend/            # FastAPI backend with AI integration
│   ├── src/
│   │   ├── ai/        # LangChain and OpenAI integration
│   │   └── main.py    # Main FastAPI application
├── mobile/            # React Native mobile app
│   ├── src/
│   │   └── screens/   # Mobile app screens
│   └── App.tsx        # Main mobile app component
├── web/              # Next.js web application
│   └── src/
│       └── app/      # Web app pages and components
└── shared/           # Shared types and utilities
```

## Features

- 🤖 AI-powered repair assistance
- 📱 Cross-platform support (iOS, Android, Web)
- 📷 Model number scanning capability
- 🔍 Context-aware responses
- 💰 Monetization through Amazon affiliate links

## Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB
- Qdrant vector database
- OpenAI API key
- Amazon Product Advertising API credentials

## Getting Started

1. Setup Backend Environment:
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix
source venv/bin/activate
pip install -r requirements.txt
```

2. Setup Environment Variables:
Create .env files in each directory:

backend/.env:
```
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=appliance_repair
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=ApplianceRepair
```

3. Create Vector Database:
Place your appliance repair documentation in the `Data` folder. The system currently supports PDF files.

Then create the vector embeddings:
```bash
cd backend/scripts
python create_embeddings.py
```

This script will:
- Load PDF documents from the Data directory
- Split them into manageable chunks
- Create embeddings using OpenAI's text-embedding-3-large model
- Store the embeddings in your Qdrant "ApplianceRepair" collection

4. Start Backend:
```bash
cd backend
uvicorn src.main:app --reload
```

4. Start Web App:
```bash
cd web
npm install
npm run dev
```

5. Start Mobile App:
```bash
cd mobile
npm install
npx expo start
```

## Development

- Backend API: http://localhost:8000
- Web App: http://localhost:3000
- Mobile App: Use Expo Go app to test on device

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT models
- Qdrant for vector database
- MongoDB for chat history storage
- LangChain for AI orchestration
