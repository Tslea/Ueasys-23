# 🎨 Fantasy World RAG - Frontend

> Modern React frontend per il Living Character System

## 🚀 Quick Start

```bash
# Installazione dipendenze
npm install

# Sviluppo
npm run dev

# Build produzione
npm run build

# Preview build
npm run preview
```

## 🛠️ Tech Stack

- **Framework**: React 18.2 con TypeScript
- **Build Tool**: Vite 5.0
- **Styling**: Tailwind CSS 3.4 con tema fantasy custom
- **State Management**: Zustand 4.4
- **Routing**: React Router 6
- **Animations**: Framer Motion 11
- **Icons**: Lucide React
- **HTTP Client**: Fetch API nativo + WebSocket

## 📁 Struttura

```
src/
├── components/
│   ├── auth/          # Componenti autenticazione
│   ├── common/        # UI components riutilizzabili
│   └── layout/        # Layout components (Header, Sidebar, etc.)
├── pages/
│   ├── admin/         # Pagine admin (Dashboard, CharacterCreator)
│   ├── Home.tsx       # Home page pubblica
│   ├── Login.tsx      # Login page
│   └── Chat.tsx       # Chat con personaggi
├── stores/
│   ├── authStore.ts   # Auth state management
│   ├── characterStore.ts  # Characters state
│   └── chatStore.ts   # Chat/WebSocket state
├── lib/
│   └── utils.ts       # Utility functions (cn, formatDate, etc.)
├── App.tsx            # Main app con routing
├── main.tsx           # Entry point
└── index.css          # Global styles + Tailwind
```

## 🎨 Design System

### Colori Fantasy

```css
--fantasy-gold: #C9A227      /* Oro principale */
--fantasy-accent: #8B5CF6    /* Accento viola */
--fantasy-dark: #1a1a2e      /* Background principale */
--fantasy-darker: #0D0D1A    /* Background profondo */
```

### Font

- **Cinzel** - Titoli e testi fantasy
- **Inter** - Testo body

### Componenti Comuni

```tsx
// Button con varianti
<Button variant="primary" | "secondary" | "outline" | "ghost" | "danger" />

// Card con effetto glass
<Card variant="default" | "glass" | "interactive" />

// Input con icona
<Input icon={<Mail />} label="Email" />

// Modal animato
<Modal isOpen={true} onClose={() => {}} title="Titolo" />

// Badge per stati
<Badge variant="default" | "success" | "warning" | "error" />
```

## 🔐 Autenticazione Admin

Il sistema ha un pannello admin protetto per la gestione dei personaggi.

### Credenziali Demo

```
Email: admin@fantasy.world
Password: fantasy123
```

## 📄 Pagine

### Pubbliche

- `/` - Home con lista personaggi
- `/chat/:characterId` - Chat fullscreen con personaggio

### Admin (protette)

- `/admin` - Dashboard
- `/admin/characters` - Lista personaggi
- `/admin/characters/new` - Crea personaggio (con AI extraction)
- `/admin/characters/:id/edit` - Modifica personaggio

## ✨ Feature Character Creator

### Drag & Drop AI Extraction

1. Trascina file (TXT, MD, YAML, JSON, PDF)
2. L'AI estrae automaticamente le informazioni del personaggio
3. Rivedi e modifica i campi estratti
4. Salva il personaggio

### Sezioni Personaggio

- **Info Base**: Nome, razza, classe, età, allineamento
- **Personalità**: Tratti, valori, paure, desideri, stile comunicativo
- **Background**: Origine, storia, eventi chiave, relazioni
- **Conoscenze**: Competenze, segreti, credenze, opinioni
- **Comportamento**: Obiettivi, motivazioni, reazioni, pattern decisionali

## 🔌 API Integration

### REST Endpoints

```typescript
// Characters
GET    /api/v1/characters
GET    /api/v1/characters/:id
POST   /api/v1/characters
PATCH  /api/v1/characters/:id
DELETE /api/v1/characters/:id

// Chat
POST   /api/v1/chat

// Extraction
POST   /api/extract-character
```

### WebSocket

```typescript
// Connessione
ws://localhost:8000/api/ws/chat/:characterId

// Eventi
{ type: 'message', content: '...' }
{ type: 'response', content: '...', character_name: '...' }
{ type: 'typing', is_typing: true }
```

## 🌐 Environment Variables

```env
# Backend API
VITE_API_URL=http://localhost:8000

# App
VITE_APP_NAME=Fantasy World RAG
```

## 📱 Responsive Design

Il frontend è completamente responsive:

- **Desktop** (>1024px): Layout completo con sidebar
- **Tablet** (768-1024px): Sidebar collassabile
- **Mobile** (<768px): Bottom navigation, full-width cards

## 🧪 Development

```bash
# Type checking
npm run type-check

# Lint
npm run lint

# Format
npm run format

# Build + Type check
npm run build
```

## 📦 Production Build

```bash
npm run build
```

I file di build saranno in `dist/`. Servili con qualsiasi web server statico.

## 🐳 Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

---

Made with 💜 for Fantasy World RAG
