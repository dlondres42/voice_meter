# Voice Meter

A full-stack application with FastAPI backend and React Native (Expo) mobile frontend.

<<<<<<< Updated upstream
## Project Structure
=======
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

## 📋 Visão Geral

O **Medidor de Voz** é uma ferramenta que ajuda você a melhorar suas habilidades de apresentação. Você digita o texto que pretende falar, grava sua apresentação, e o sistema compara sua fala com o texto esperado utilizando a API Whisper da OpenAI.

### ✨ Funcionalidades

- 📝 **Entrada de Texto** - Digite o texto que você pretende falar
- 🎙️ **Gravação de Áudio** - Grave sua apresentação diretamente no navegador
- 🤖 **Transcrição com IA** - Transcrição automática usando OpenAI Whisper
- 📊 **Comparação Git-Diff** - Visualização lado a lado com cores verde/vermelho
- 🔊 **Gráfico de Volume** - Visualização do volume do áudio ao longo do tempo
- 📈 **Métricas de Fala** - Velocidade (PPM), pausas detectadas, duração
- 💬 **Feedback Inteligente** - Recomendações personalizadas baseadas na análise
- 📜 **Histórico** - Acompanhe sua evolução ao longo do tempo
- 📊 **Estatísticas** - Visualize seu progresso com gráficos

## 🏗️ Arquitetura

![Arquitetura do Voice Meter](arquitetura_puml_png.png)

## 🛠️ Tecnologias

### Backend
- **Python 3.11** - Linguagem principal
- **FastAPI** - Framework web assíncrono
- **Librosa** - Análise de áudio (volume, pausas, velocidade)
- **OpenAI Whisper API** - Transcrição de fala
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados local
- **Pydub** - Conversão de formatos de áudio

### Frontend
- **React Native** - Framework mobile/web
- **Expo** - Plataforma de desenvolvimento
- **Expo Router** - Navegação baseada em arquivos
- **Expo AV** - Gravação de áudio
- **TypeScript** - Tipagem estática

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de serviços

## 🚀 Instalação

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- [Node.js 18+](https://nodejs.org/) (para desenvolvimento local)
- Chave de API da OpenAI

### Usando Docker (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/hlaff147/voice_meter.git
cd voice_meter
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua OPENAI_API_KEY
```

3. **Inicie os containers**
```bash
docker-compose up --build -d
```

4. **Acesse a aplicação**
- Frontend: http://localhost:8081
- Backend API: http://localhost:8000
- Documentação API: http://localhost:8000/docs

### Desenvolvimento Local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd mobile
npm install
npm run web
```

## 📱 Uso

### 1. Tela Inicial
- Clique em **"Iniciar Treinamento"** para começar

### 2. Digite seu Texto
- Escreva o texto que você pretende falar na apresentação
- Clique em **"Continuar para Gravação"**

### 3. Grave seu Áudio
- Clique no botão de microfone para iniciar a gravação
- Leia o texto em voz alta
- Clique novamente para parar a gravação

### 4. Analise os Resultados
- **Comparação de Textos**: Veja lado a lado o texto esperado e o transcrito
  - 🟢 Verde: palavras corretas
  - 🔴 Vermelho: palavras diferentes ou não detectadas
- **Gráfico de Volume**: Visualize a intensidade do áudio
- **Métricas**: Velocidade (PPM), pausas, duração
- **Feedback**: Mensagem personalizada com recomendações

### 5. Ver Detalhes
- Clique em **"Ver Detalhes Completos"** para mais informações
- Acesse o **Histórico** para ver gravações anteriores

## 🔌 API Endpoints

### Análise de Fala
```http
POST /api/v1/speech/analyze
Content-Type: multipart/form-data

file: <arquivo de áudio>
category: presentation|pitch|conversation|other
expected_text: <texto esperado>
```

**Resposta:**
```json
{
  "recording_id": 1,
  "transcribed_text": "...",
  "expected_text": "...",
  "similarity_ratio": 0.95,
  "words_per_minute": 145,
  "pause_count": 5,
  "duration_seconds": 30.5,
  "volume_data": [65.2, 70.1, ...],
  "missing_words": ["palavra1", "palavra2"],
  "feedback": "Excelente pronúncia!"
}
```

### Gravações
```http
GET /api/v1/recordings/recordings
GET /api/v1/recordings/recordings/{id}
GET /api/v1/recordings/statistics
```

### Categorias
```http
GET /api/v1/speech/categories
```

## 📁 Estrutura do Projeto
>>>>>>> Stashed changes

```
voice_meter/
├── backend/          # FastAPI backend
├── mobile/           # React Native (Expo) mobile app
└── database/         # Database scripts and migrations
```

## 🐳 Quick Start com Docker (Recomendado)

### Pré-requisitos

- [Docker](https://www.docker.com/get-started) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

### Rodar tudo com um comando

```bash
docker-compose up
```

✨ **Pronto!** Isso vai iniciar:
- **Backend API (FastAPI)** → http://localhost:8000
- **API Docs** → http://localhost:8000/docs
- **Mobile/Web (Expo)** → http://localhost:19006
- **PostgreSQL Database** → localhost:5432

### Comandos úteis

```bash
# Verificar se está tudo pronto
./check-docker.sh

# Iniciar com script interativo
./start-docker.sh

# Ver logs
docker-compose logs -f

# Parar tudo
docker-compose down

# Usar Makefile (mais fácil)
make up      # Inicia
make down    # Para
make logs    # Logs
make help    # Ver todos comandos
```

📖 **Documentação completa**: 
- [Guia Docker](DOCKER.md) - Setup completo
- [Quick Reference](DOCKER-QUICKREF.md) - Referência rápida
- [Troubleshooting](TROUBLESHOOTING-DOCKER.md) - Resolver problemas

---

## 🔧 Development Without Docker

If you need to run without Docker, you can manually set up conda environments. See the individual component READMEs:
- [Backend Setup](backend/README.md)
- [Mobile Setup](mobile/README.md)

## Development

### Backend (FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **API Docs**: http://localhost:8000/docs
- **Testing**: Run `make test` or `docker-compose exec backend pytest`

### Frontend (React Native + Expo)
- **Framework**: React Native with Expo
- **Routing**: Expo Router (file-based)
- **Language**: TypeScript
- **HTTP Client**: Axios
- **Platforms**: Web, iOS, Android

Access the running app:
- **Web Browser**: http://localhost:19006
- **Mobile**: Scan QR code with Expo Go app
- **iOS Simulator**: Press `i` in the mobile container logs
- **Android Emulator**: Press `a` in the mobile container logs

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Commands

Quick reference for common Docker operations:

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Run backend tests
make test

# See all available commands
make help
```

For more Docker commands, see [QUICKSTART.md](QUICKSTART.md) or run `make help`.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request
